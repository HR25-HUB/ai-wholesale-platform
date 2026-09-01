from pydantic import BaseModel
from pydantic_ai import Agent, ImageUrl
from pydantic_ai.models import Model

from app.application.product_identity.contracts import IdentityInferenceRequest
from app.domain.product_identity.models import (
    EvidenceModality,
    ProductClaim,
    ProductIdentityProposal,
)

_INSTRUCTIONS = """
You are a product identity evidence interpreter for B2B technical products.

Rules:
1. Extract product identity claims only from the evidence supplied in the user input.
2. Every returned claim must reference one or more evidence_id values that are present in the supplied evidence.
3. Do not use prior model knowledge, product-code conventions, or plausible guesses as evidence.
4. If an attribute is not supported by the supplied evidence, omit that claim.
5. Preserve technical values and manufacturer product codes exactly when the evidence provides them.
6. Never decide whether the case is accepted, rejected, or requires human review. Decision policy is outside the model.
""".strip()


class _ModelIdentityProposal(BaseModel):
    claims: list[ProductClaim]


def build_multimodal_user_content(
    request: IdentityInferenceRequest,
) -> list[str | ImageUrl]:
    content: list[str | ImageUrl] = [
        f"Resolve the product identity for this RFQ line:\n{request.rfq_line}"
        "\n\nUse only the evidence items below."
    ]

    for item in request.evidence.items:
        evidence_text = item.text or "[no extracted text]"
        content.append(
            "\n".join(
                [
                    f"evidence_id: {item.evidence_id}",
                    f"document_id: {item.document_id}",
                    f"page: {item.page}",
                    f"modality: {item.modality.value}",
                    f"content: {evidence_text}",
                ]
            )
        )
        if item.modality is EvidenceModality.PAGE_IMAGE and item.asset_uri:
            content.append(ImageUrl(url=item.asset_uri))

    return content


class PydanticAIMultimodalAdapter:
    def __init__(
        self,
        *,
        model: str | Model,
        model_id: str,
        prompt_version: str,
    ) -> None:
        self._model_id = model_id
        self._prompt_version = prompt_version
        self._agent = Agent(
            model,
            output_type=_ModelIdentityProposal,
            instructions=_INSTRUCTIONS,
        )

    async def propose(
        self,
        request: IdentityInferenceRequest,
    ) -> ProductIdentityProposal:
        result = await self._agent.run(build_multimodal_user_content(request))
        return ProductIdentityProposal(
            claims=result.output.claims,
            model_id=self._model_id,
            prompt_version=self._prompt_version,
        )
