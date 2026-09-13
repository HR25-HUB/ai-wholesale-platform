from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from dashboard_factory.evidence import build_metric_evidence, write_metric_evidence
from dashboard_factory.loaders import (
    ContractLoadError,
    DatasetLoadError,
    load_metric_definition,
    load_rfq_fixture,
)
from dashboard_factory.metric_engine import (
    MetricEngine,
    MetricUndefinedError,
    UnsupportedConditionError,
)
from dashboard_factory.models import Condition, FilterSpec, MetricDefinition

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "rfq_offer_conversion.jsonl"
CONTRACT = ROOT / "metrics" / "sales" / "rfq_offer_conversion.yaml"


def test_golden_rfq_offer_conversion_is_verified_at_rfq_grain(tmp_path: Path) -> None:
    rows = load_rfq_fixture(GOLDEN)
    definition = load_metric_definition(CONTRACT)

    result = MetricEngine().calculate(rows, definition)

    assert len(rows) == 6
    assert len({row.rfq_id for row in rows}) == 5
    assert result.numerator == 2
    assert result.denominator == 4
    assert result.value == Decimal("0.5")

    evidence = build_metric_evidence(
        dataset_id="golden-rfq-offer-conversion-v1",
        result=result,
        engine_version="0.1.0",
    )
    output = write_metric_evidence(tmp_path / "metric_evidence.json", evidence)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["dataset_id"] == "golden-rfq-offer-conversion-v1"
    assert payload["metric_id"] == "rfq_offer_conversion"
    assert payload["metric_version"] == "1.0.0"
    assert payload["engine_version"] == "0.1.0"
    assert payload["status"] == "VERIFIED"
    assert payload["result"]["numerator"] == 2
    assert payload["result"]["denominator"] == 4
    assert payload["result"]["value"] == "0.5"


def test_unknown_field_fails_closed() -> None:
    rows = load_rfq_fixture(GOLDEN)
    definition = MetricDefinition(
        metric_id="bad_metric",
        version="1.0.0",
        name="Bad Metric",
        grain="rfq",
        unit="ratio",
        denominator=FilterSpec(
            all=(Condition(field="does_not_exist", operator="equals", value=True),)
        ),
        numerator=FilterSpec(),
    )

    with pytest.raises(UnsupportedConditionError, match="Unknown field"):
        MetricEngine().calculate(rows, definition)


def test_zero_denominator_is_explicit_terminal_error() -> None:
    rows = load_rfq_fixture(GOLDEN)
    definition = MetricDefinition(
        metric_id="no_offers",
        version="1.0.0",
        name="No Offers",
        grain="rfq",
        unit="ratio",
        denominator=FilterSpec(all=(Condition(field="status", operator="equals", value="never"),)),
        numerator=FilterSpec(),
    )

    with pytest.raises(MetricUndefinedError, match="no_offers"):
        MetricEngine().calculate(rows, definition)


def test_invalid_metric_contract_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "invalid.yaml"
    path.write_text("metric_id: only_id\n", encoding="utf-8")

    with pytest.raises(ContractLoadError, match="Invalid metric contract"):
        load_metric_definition(path)


def test_duplicate_line_identity_fails_closed(tmp_path: Path) -> None:
    first = GOLDEN.read_text(encoding="utf-8").splitlines()[0]
    path = tmp_path / "duplicates.jsonl"
    path.write_text(first + "\n" + first + "\n", encoding="utf-8")

    with pytest.raises(DatasetLoadError, match="duplicate"):
        load_rfq_fixture(path)
