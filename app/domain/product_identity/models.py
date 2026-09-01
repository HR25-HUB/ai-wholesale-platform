from enum import StrEnum

from pydantic import BaseModel, Field


class EvidenceModality(StrEnum):
    TEXT = "text"
    TABLE = "table"
    PAGE_IMAGE = "page_image"


class IdentityDecision(StrEnum):
    ACCEPTED = "accepted"
    REVIEW_REQUIRED = "review_required"


class Evidence(BaseModel):
    evidence_id: str
    document_id: str
    page: int = Field(ge=1)
    modality: EvidenceModality
    text: str | None = None
    asset_uri: str | None = None
    content_hash: str


class EvidenceBundle(BaseModel):
    items: list[Evidence]

    def ids(self) -> set[str]:
        return {item.evidence_id for item in self.items}


class EvidenceRef(BaseModel):
    evidence_id: str


class ProductClaim(BaseModel):
    attribute: str
    value: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ProductIdentityProposal(BaseModel):
    claims: list[ProductClaim]
    model_id: str
    prompt_version: str

    def claim_by_attribute(self, attribute: str) -> ProductClaim | None:
        return next(
            (claim for claim in self.claims if claim.attribute == attribute),
            None,
        )


class PolicyViolation(BaseModel):
    code: str
    attribute: str
    evidence_id: str | None = None


class EvidencePolicyResult(BaseModel):
    decision: IdentityDecision
    violations: list[PolicyViolation] = Field(default_factory=list)
