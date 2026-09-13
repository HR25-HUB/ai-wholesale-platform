from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from dashboard_factory.cli import app

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "rfq_offer_conversion.jsonl"
CONTRACT = ROOT / "metrics" / "sales" / "rfq_offer_conversion.yaml"


def test_verify_metric_cli_writes_verified_evidence(tmp_path: Path) -> None:
    evidence_out = tmp_path / "metric_evidence.json"

    result = CliRunner().invoke(
        app,
        [
            "verify-metric",
            "--dataset",
            str(GOLDEN),
            "--contract",
            str(CONTRACT),
            "--dataset-id",
            "golden-rfq-offer-conversion-v1",
            "--evidence-out",
            str(evidence_out),
        ],
    )

    assert result.exit_code == 0, result.stdout
    assert "metric=rfq_offer_conversion" in result.stdout
    assert "numerator=2" in result.stdout
    assert "denominator=4" in result.stdout
    assert "value=0.5" in result.stdout
    assert "status=VERIFIED" in result.stdout

    payload = json.loads(evidence_out.read_text(encoding="utf-8"))
    assert payload["dataset_id"] == "golden-rfq-offer-conversion-v1"
    assert payload["metric_id"] == "rfq_offer_conversion"
    assert payload["metric_version"] == "1.0.0"
    assert payload["status"] == "VERIFIED"
    assert payload["result"]["numerator"] == 2
    assert payload["result"]["denominator"] == 4
    assert payload["result"]["value"] == "0.5"
