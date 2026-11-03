"""Fail-closed evidence gate for an authorized real RFQ/PIM snapshot.

Cryptographic hashes prove file consistency, not source authenticity.
Source authenticity is an explicit human attestation.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from contracts.product_matching import (
    MatchDecision,
    ProductCatalogRecord,
    ProductMatchResult,
    RFQLineInput,
)


class VerifiedSourceAttestation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_system: str = Field(min_length=3)
    source_record_ref: str = Field(min_length=3)
    reviewer_id: str = Field(min_length=3)
    reviewed_at: datetime
    decision: Literal["APPROVED"]
    # External control: approver must inspect original PIM and source RFQ independently.

    @field_validator("reviewed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("reviewed_at must contain a timezone")
        return value


class RealCaseManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str = Field(min_length=3)
    rfq_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    catalog_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_product_id: str = Field(min_length=1)
    attestation: VerifiedSourceAttestation

    @model_validator(mode="after")
    def refuse_synthetic_sources(self) -> "RealCaseManifest":
        fields = (
            self.case_id, self.expected_product_id,
            self.attestation.source_system,
            self.attestation.source_record_ref,
            self.attestation.reviewer_id,
        )
        if any(value.casefold().startswith(("synthetic", "example:", "test:")) for value in fields):
            raise ValueError("synthetic evidence cannot pass the real-case gate")
        return self


class EvidenceOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: str
    correlation_id: str
    rfq_sha256: str
    catalog_sha256: str
    product_id: str
    policy_version: str
    decision: Literal["VERIFIED"]
    source_record_ref: str
    reviewed_at: datetime
    # No customer details or raw input data in the emitted outcome.


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_and_validate_case(
    manifest_path: Path,
    rfq_path: Path,
    catalog_path: Path,
) -> tuple[RealCaseManifest, RFQLineInput]:
    manifest = RealCaseManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    if sha256_file(rfq_path) != manifest.rfq_sha256:
        raise ValueError("RFQ source digest mismatch")
    if sha256_file(catalog_path) != manifest.catalog_sha256:
        raise ValueError("PIM catalog digest mismatch")

    line = RFQLineInput.model_validate_json(rfq_path.read_text(encoding="utf-8"))
    if line.source_reference != manifest.attestation.source_record_ref:
        raise ValueError("source reference does not match approved RFQ source")
    if line.rfq_line_id.casefold().startswith(("synthetic", "test-")):
        raise ValueError("synthetic RFQ line is not a real-case input")

    records = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("catalog snapshot must be an array")
    parsed = [ProductCatalogRecord.model_validate(row) for row in records]
    expected = [row for row in parsed if row.product_id == manifest.expected_product_id]
    if len(expected) != 1:
        raise ValueError("expected product must occur exactly once in PIM snapshot")
    if expected[0].evidence_ref.casefold().startswith(("synthetic", "test:")):
        raise ValueError("synthetic PIM evidence cannot pass the real-case gate")
    return manifest, line


def verify_result(
    manifest: RealCaseManifest,
    result: ProductMatchResult,
) -> EvidenceOutcome:
    if result.decision != MatchDecision.VERIFIED or result.match_type != "EXACT":
        raise ValueError("result is not a verified exact match")
    if result.product_id != manifest.expected_product_id:
        raise ValueError("result does not match independently approved PIM identity")
    if not result.evidence_refs or any(
        ref.casefold().startswith(("synthetic", "test:")) for ref in result.evidence_refs
    ):
        raise ValueError("missing or synthetic PIM evidence reference")
    return EvidenceOutcome(
        case_id=manifest.case_id,
        correlation_id=result.correlation_id,
        rfq_sha256=manifest.rfq_sha256,
        catalog_sha256=manifest.catalog_sha256,
        product_id=result.product_id,
        policy_version=result.policy_version,
        decision="VERIFIED",
        source_record_ref=manifest.attestation.source_record_ref,
        reviewed_at=manifest.attestation.reviewed_at,
    )
