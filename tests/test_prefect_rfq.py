"""Synthetic unit scenarios only; live PIM/e2e evidence remains outstanding."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.application.product_matching import MatchRFQLine
from app.infrastructure.catalog_snapshot import JsonCatalogSnapshot
from contracts.product_matching import MatchDecision, RFQLineInput
from flows.rfq_pipeline import rfq_pipeline


def line(**overrides: object) -> RFQLineInput:
    values = dict(
        rfq_line_id="SYNTHETIC-001",
        manufacturer="Example Manufacturer",
        part_number="PART-001",
        quantity=2,
        source_reference="synthetic:unit-test",
    )
    values.update(overrides)
    return RFQLineInput.model_validate(values)


def catalog(tmp_path: Path, entries: list[dict[str, str]]) -> str:
    path = tmp_path / "synthetic-catalog.json"
    path.write_text(json.dumps(entries), encoding="utf-8")
    return str(path)


def record(**overrides: str) -> dict[str, str]:
    values = dict(
        product_id="P-001",
        manufacturer="Example Manufacturer",
        part_number="PART-001",
        category="synthetic",
        evidence_ref="synthetic:record-001",
    )
    values.update(overrides)
    return values


def test_verified_exact_match(tmp_path: Path) -> None:
    path = catalog(tmp_path, [record()])
    result = MatchRFQLine(JsonCatalogSnapshot(path)).execute(line(), "trace-001")
    assert result.decision == MatchDecision.VERIFIED
    assert result.product_id == "P-001"
    assert result.evidence_refs == ("synthetic:record-001",)


def test_ambiguous_duplicates_require_review(tmp_path: Path) -> None:
    path = catalog(tmp_path, [record(), record(product_id="P-002")])
    result = MatchRFQLine(JsonCatalogSnapshot(path)).execute(line(), "trace-002")
    assert result.decision == MatchDecision.REVIEW_REQUIRED
    assert result.product_id is None


def test_missing_match(tmp_path: Path) -> None:
    path = catalog(tmp_path, [])
    result = MatchRFQLine(JsonCatalogSnapshot(path)).execute(line(), "trace-003")
    assert result.decision == MatchDecision.NOT_FOUND


def test_invalid_quantity_fails_fast() -> None:
    with pytest.raises(ValidationError):
        line(quantity=0)


def test_manufacturer_mismatch_never_verified(tmp_path: Path) -> None:
    path = catalog(tmp_path, [record(manufacturer="Different Manufacturer")])
    result = MatchRFQLine(JsonCatalogSnapshot(path)).execute(line(), "trace-004")
    assert result.decision == MatchDecision.REVIEW_REQUIRED


def test_prefect_flow_executes_locally(tmp_path: Path) -> None:
    path = catalog(tmp_path, [record()])
    result = rfq_pipeline(line(), path, "trace-005")
    assert result.decision == MatchDecision.VERIFIED
    assert result.correlation_id == "trace-005"


def test_repeat_is_deterministic(tmp_path: Path) -> None:
    path = catalog(tmp_path, [record()])
    service = MatchRFQLine(JsonCatalogSnapshot(path))
    first = service.execute(line(), "trace-replay")
    second = service.execute(line(), "trace-replay")
    assert first == second
    # No durable deduplication claim: slice performs no business writes.
