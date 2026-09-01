from collections.abc import Iterable

from app.domain.product_identity.models import (
    EvidenceBundle,
    EvidencePolicyResult,
    IdentityDecision,
    PolicyViolation,
    ProductIdentityProposal,
)


class EvidencePolicy:
    def __init__(self, critical_attributes: Iterable[str]) -> None:
        self._critical_attributes = frozenset(critical_attributes)

    def evaluate(
        self,
        proposal: ProductIdentityProposal,
        evidence: EvidenceBundle,
    ) -> EvidencePolicyResult:
        evidence_ids = evidence.ids()
        violations: list[PolicyViolation] = []

        for attribute in sorted(self._critical_attributes):
            claim = proposal.claim_by_attribute(attribute)

            if claim is None:
                violations.append(
                    PolicyViolation(
                        code="MISSING_CLAIM",
                        attribute=attribute,
                    )
                )
                continue

            if not claim.evidence:
                violations.append(
                    PolicyViolation(
                        code="MISSING_EVIDENCE",
                        attribute=attribute,
                    )
                )
                continue

            for ref in claim.evidence:
                if ref.evidence_id not in evidence_ids:
                    violations.append(
                        PolicyViolation(
                            code="UNRESOLVED_EVIDENCE",
                            attribute=attribute,
                            evidence_id=ref.evidence_id,
                        )
                    )

        decision = (
            IdentityDecision.REVIEW_REQUIRED
            if violations
            else IdentityDecision.ACCEPTED
        )

        return EvidencePolicyResult(
            decision=decision,
            violations=violations,
        )
