import asyncio

from pydantic_ai import ImageUrl, models
from pydantic_ai.models.test import TestModel

from app.adapters.product_identity.pydantic_ai_multimodal import (
    PydanticAIMultimodalAdapter,
    build_multimodal_user_content,
)
from app.application.product_identity.contracts import IdentityInferenceRequest
from app.domain.product_identity import Evidence, EvidenceBundle, EvidenceModality

models.ALLOW_MODEL_REQUESTS = False


def make_request(*, include_image: bool = False) -> IdentityInferenceRequest:
    evidence = [
        Evidence(
            evidence_id="ev-product-code",
            document_id="abb-official",
            page=21,
            modality=EvidenceModality.TEXT,
            text="S203-C16",
            content_hash="hash-product-code",
        )
    ]
    if include_image:
        evidence.append(
            Evidence(
                evidence_id="ev-page-image",
                document_id="abb-official",
                page=21,
                modality=EvidenceModality.PAGE_IMAGE,
                text="ABB catalogue page containing S203-C16",
                asset_uri="https://example.com/abb-page-21.png",
                content_hash="hash-page-image",
            )
        )

    return IdentityInferenceRequest(
        rfq_line="ABB S203-C16 автомат 3P 16A",
        evidence=EvidenceBundle(items=evidence),
    )


def test_builds_interleaved_multimodal_content_with_evidence_identity() -> None:
    content = build_multimodal_user_content(make_request(include_image=True))

    text_parts = [part for part in content if isinstance(part, str)]
    image_parts = [part for part in content if isinstance(part, ImageUrl)]

    assert any("ev-product-code" in part for part in text_parts)
    assert any("ev-page-image" in part for part in text_parts)
    assert len(image_parts) == 1
    assert image_parts[0].url == "https://example.com/abb-page-21.png"


def test_returns_domain_proposal_and_injects_adapter_metadata() -> None:
    adapter = PydanticAIMultimodalAdapter(
        model=TestModel(),
        model_id="test-model",
        prompt_version="product-identity-v0.1",
    )

    proposal = asyncio.run(adapter.propose(make_request()))

    assert proposal.model_id == "test-model"
    assert proposal.prompt_version == "product-identity-v0.1"
    assert isinstance(proposal.claims, list)
    assert not hasattr(proposal, "decision")
