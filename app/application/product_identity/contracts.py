from pydantic import BaseModel, Field

from app.domain.product_identity.models import (
    EvidenceBundle,
    EvidencePolicyResult,
    IdentityDecision,
    ProductIdentityProposal,
)


class ResolveProductIdentityCommand(BaseModel):
    case_id: str
    rfq_line: str
    document_ids: list[str] = Field(min_length=1)


class IdentityInferenceRequest(BaseModel):
    rfq_line: str
    evidence: EvidenceBundle


class ProductIdentityResult(BaseModel):
    case_id: str
    proposal: ProductIdentityProposal
    evidence: EvidenceBundle
    policy: EvidencePolicyResult
    decision: IdentityDecision
