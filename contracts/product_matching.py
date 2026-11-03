"""Typed integration contracts for one RFQ line product matching."""
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MatchDecision(StrEnum):
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    NOT_FOUND = "NOT_FOUND"


class RFQLineInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    rfq_line_id: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    part_number: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    source_reference: str = Field(min_length=1)
    input_version: str = Field(min_length=1, default="1")

    @field_validator("manufacturer", "part_number")
    @classmethod
    def reject_blank_identity(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("product identity must not be blank")
        return value.strip()


class ProductCatalogRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    product_id: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    part_number: str = Field(min_length=1)
    category: str | None = None
    evidence_ref: str = Field(min_length=1)


class ProductMatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    rfq_line_id: str
    product_id: str | None
    decision: MatchDecision
    match_type: str
    category: str | None = None
    evidence_refs: tuple[str, ...] = ()
    policy_version: str = "product-identity-v1"
    correlation_id: str
