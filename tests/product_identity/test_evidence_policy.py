from app.domain.product_identity.models import (
    Evidence,
    EvidenceBundle,
    EvidenceModality,
    EvidenceRef,
    IdentityDecision,
    ProductClaim,
    ProductIdentityProposal,
)
from app.domain.product_identity.policies import EvidencePolicy


CRITICAL = {
    "manufacturer",
    "product_code",
    "poles",
    "rated_current",
    "trip_curve",
}


def make_evidence(attribute: str) -> Evidence:
    return Evidence(
        evidence_id=f"ev-{attribute}",
        document_id="abb-s200-official",
        page=27,
        modality=EvidenceModality.TEXT,
        text=f"evidence for {attribute}",
        content_hash=f"hash-{attribute}",
    )


def make_proposal() -> ProductIdentityProposal:
    values = {
        "manufacturer": "ABB",
        "product_code": "S203-C16",
        "poles": "3",
        "rated_current": "16 A",
        "trip_curve": "C",
    }
    return ProductIdentityProposal(
        claims=[
            ProductClaim(
                attribute=attribute,
                value=value,
                evidence=[EvidenceRef(evidence_id=f"ev-{attribute}")],
            )
            for attribute, value in values.items()
        ],
        model_id="golden-fixture",
        prompt_version="v0.1",
    )


def make_bundle() -> EvidenceBundle:
    return EvidenceBundle(items=[make_evidence(name) for name in CRITICAL])


def test_accepts_when_all_critical_claims_have_resolvable_evidence() -> None:
    result = EvidencePolicy(CRITICAL).evaluate(make_proposal(), make_bundle())

    assert result.decision is IdentityDecision.ACCEPTED
    assert result.violations == []


def test_requires_review_when_critical_claim_has_no_evidence() -> None:
    proposal = make_proposal()
    claim = proposal.claim_by_attribute("trip_curve")
    assert claim is not None
    claim.evidence = []

    result = EvidencePolicy(CRITICAL).evaluate(proposal, make_bundle())

    assert result.decision is IdentityDecision.REVIEW_REQUIRED
    assert any(
        violation.code == "MISSING_EVIDENCE"
        and violation.attribute == "trip_curve"
        for violation in result.violations
    )


def test_requires_review_when_evidence_reference_does_not_resolve() -> None:
    bundle = make_bundle()
    bundle.items = [
        item for item in bundle.items if item.evidence_id != "ev-trip_curve"
    ]

    result = EvidencePolicy(CRITICAL).evaluate(make_proposal(), bundle)

    assert result.decision is IdentityDecision.REVIEW_REQUIRED
    assert any(
        violation.code == "UNRESOLVED_EVIDENCE"
        and violation.attribute == "trip_curve"
        for violation in result.violations
    )


def test_requires_review_when_critical_claim_is_missing() -> None:
    proposal = make_proposal()
    proposal.claims = [
        claim for claim in proposal.claims if claim.attribute != "trip_curve"
    ]

    result = EvidencePolicy(CRITICAL).evaluate(proposal, make_bundle())

    assert result.decision is IdentityDecision.REVIEW_REQUIRED
    assert any(
        violation.code == "MISSING_CLAIM"
        and violation.attribute == "trip_curve"
        for violation in result.violations
    )
