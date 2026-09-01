from typing import Protocol

from app.application.product_identity.contracts import IdentityInferenceRequest
from app.domain.product_identity.models import Evidence, ProductIdentityProposal


class SearchPort(Protocol):
    async def search(
        self,
        query: str,
        *,
        document_ids: tuple[str, ...],
        limit: int = 10,
    ) -> list[Evidence]: ...


class EmbeddingPort(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class MultimodalModelPort(Protocol):
    async def propose(
        self,
        request: IdentityInferenceRequest,
    ) -> ProductIdentityProposal: ...
