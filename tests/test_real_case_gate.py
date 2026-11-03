"""All test evidence here is synthetic and must never be used as real proof."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.application.evidence_verification import (
    RealCaseManifest,
    load_and_validate_case,
    verify_result,
)
from app.application.product_matching import MatchRFQLine
from app.infrastructure.catalog_snapshot import JsonCatalogSnapshot


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    rfq = tmp_path / "rfq.json"
    catalog = tmp_path / "catalog.json"
    manifest = tmp_path / "manifest.json"
    rfq.write_text(json.dumps({
        "rfq_line_id": "R-001",
        "manufacturer": "Vendor One",
        "part_number": "PN-1",
        "quantity": 1,
        "source_reference": "source:rfq/1",
    }), encoding="utf-8")
    catalog.write_text(json.dumps([{
        "product_id": "P-001",
        "manufacturer": "Vendor One",
        "part_number": "PN-1",
        "evidence_ref": "source:pim/1",
    }]), encoding="utf-8")
    manifest.write_text(json.dumps({
        "case_id": "CASE-001",
        "rfq_sha256": digest(rfq.read_bytes()),
        "catalog_sha256": digest(catalog.read_bytes()),
        "expected_product_id": "P-001",
        "attestation": {
            "source_system": "isolated-fixture",
            "source_record_ref": "source:rfq/1",
            "reviewer_id": "fixture-reviewer",
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "decision": "APPROVED",
        },
    }), encoding="utf-8")
    return manifest, rfq, catalog


def test_matching_bundle_consistent(tmp_path: Path) -> None:
    # This tests schema/digest consistency, NOT reviewer authenticity.
    manifest_path, rfq_path, catalog_path = write_fixture(tmp_path)
    manifest, line = load_and_validate_case(manifest_path, rfq_path, catalog_path)
    result = MatchRFQLine(JsonCatalogSnapshot(str(catalog_path))).execute(line, "run-test")
    bundle = verify_result(manifest, result)
    assert bundle.product_id == "P-001"
    assert bundle.correlation_id == "run-test"


def test_changed_catalog_is_rejected(tmp_path: Path) -> None:
    manifest, rfq, catalog = write_fixture(tmp_path)
    catalog.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="digest mismatch"):
        load_and_validate_case(manifest, rfq, catalog)


def test_wrong_expected_product_rejected(tmp_path: Path) -> None:
    manifest_path, rfq, catalog = write_fixture(tmp_path)
    obj = json.loads(manifest_path.read_text(encoding="utf-8"))
    obj["expected_product_id"] = "P-unknown"
    manifest_path.write_text(json.dumps(obj), encoding="utf-8")
    with pytest.raises(ValueError, match="exactly once"):
        load_and_validate_case(manifest_path, rfq, catalog)


def test_synthetic_manifest_is_rejected() -> None:
    with pytest.raises(ValueError, match="synthetic evidence"):
        RealCaseManifest.model_validate({
            "case_id": "synthetic-001",
            "rfq_sha256": "a" * 64,
            "catalog_sha256": "b" * 64,
            "expected_product_id": "P-1",
            "attestation": {
                "source_system": "pim",
                "source_record_ref": "source:rfq/1",
                "reviewer_id": "reviewer-1",
                "reviewed_at": "2026-11-03T10:00:00+03:00",
                "decision": "APPROVED",
            },
        })


def test_forged_line_reference_rejected(tmp_path: Path) -> None:
    manifest, rfq, catalog = write_fixture(tmp_path)
    obj = json.loads(rfq.read_text(encoding="utf-8"))
    obj["source_reference"] = "source:rfq/forged"
    payload = json.dumps(obj)
    rfq.write_text(payload, encoding="utf-8")
    manifest_obj = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_obj["rfq_sha256"] = digest(payload.encode())
    manifest.write_text(json.dumps(manifest_obj), encoding="utf-8")
    with pytest.raises(ValueError, match="source reference"):
        load_and_validate_case(manifest, rfq, catalog)
