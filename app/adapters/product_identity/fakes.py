from app.application.product_identity.contracts import IdentityInferenceRequest
from app.domain.product_identity.models import Evidence, ProductIdentityProposal


class FakeSearchPort:
    def __init__(self, evidence: list[Evidence]) -> None:
        self._evidence = list(evidence)

    async def search(
        self,
        query: str,
        *,
        document_ids: tuple[str, ...],
        limit: int = 10,
    ) -> list[Evidence]:
        del query
        allowed = set(document_ids)
        return [
            item
            for item in self._evidence
            if item.document_id in allowed
        ][:limit]


class FakeMultimodalModelPort:
    def __init__(self, proposal: ProductIdentityProposal) -> None:
        self._proposal = proposal
        self.last_request: IdentityInferenceRequest | None = None

    async def propose(
        self,
        request: IdentityInferenceRequest,
    ) -> ProductIdentityProposal:
        self.last_request = request
        return self._proposal.model_copy(deep=True)
