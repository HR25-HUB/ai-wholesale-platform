import asyncio

from app.adapters.product_identity.fakes import (
    FakeMultimodalModelPort,
    FakeSearchPort,
)
from app.application.product_identity.contracts import ResolveProductIdentityCommand
from app.application.product_identity.handler import ResolveProductIdentityHandler
from app.domain.product_identity.models import (
    Evidence,
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


def test_resolve_identity_runs_end_to_end_with_fake_adapters() -> None:
    evidence = [
        Evidence(
            evidence_id=f"ev-{attribute}",
            document_id="abb-s200-official",
            page=27,
            modality=EvidenceModality.TEXT,
            text=f"evidence for {attribute}",
            content_hash=f"hash-{attribute}",
        )
        for attribute in CRITICAL
    ]
    values = {
        "manufacturer": "ABB",
        "product_code": "S203-C16",
        "poles": "3",
        "rated_current": "16 A",
        "trip_curve": "C",
    }
    proposal = ProductIdentityProposal(
        claims=[
            ProductClaim(
                attribute=attribute,
                value=value,
                evidence=[EvidenceRef(evidence_id=f"ev-{attribute}")],
            )
            for attribute, value in values.items()
        ],
        model_id="fake-model",
        prompt_version="v0.1",
    )

    model = FakeMultimodalModelPort(proposal)
    handler = ResolveProductIdentityHandler(
        search=FakeSearchPort(evidence),
        model=model,
        policy=EvidencePolicy(CRITICAL),
    )

    result = asyncio.run(
        handler.execute(
            ResolveProductIdentityCommand(
                case_id="abb-s203-c16-001",
                rfq_line="ABB S203-C16 автомат 3P 16A",
                document_ids=["abb-s200-official"],
            )
        )
    )

    assert result.decision is IdentityDecision.ACCEPTED
    assert result.proposal.claim_by_attribute("product_code") is not None
    assert result.proposal.claim_by_attribute("product_code").value == "S203-C16"  # type: ignore[union-attr]
    assert model.last_request is not None
    assert model.last_request.rfq_line == "ABB S203-C16 автомат 3P 16A"
