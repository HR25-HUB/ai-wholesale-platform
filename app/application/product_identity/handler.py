from app.application.product_identity.contracts import (
    IdentityInferenceRequest,
    ProductIdentityResult,
    ResolveProductIdentityCommand,
)
from app.application.product_identity.ports import MultimodalModelPort, SearchPort
from app.domain.product_identity.models import EvidenceBundle
from app.domain.product_identity.policies import EvidencePolicy


class ResolveProductIdentityHandler:
    def __init__(
        self,
        *,
        search: SearchPort,
        model: MultimodalModelPort,
        policy: EvidencePolicy,
    ) -> None:
        self._search = search
        self._model = model
        self._policy = policy

    async def execute(
        self,
        command: ResolveProductIdentityCommand,
    ) -> ProductIdentityResult:
        evidence_items = await self._search.search(
            command.rfq_line,
            document_ids=tuple(command.document_ids),
            limit=10,
        )
        evidence = EvidenceBundle(items=evidence_items)

        proposal = await self._model.propose(
            IdentityInferenceRequest(
                rfq_line=command.rfq_line,
                evidence=evidence,
            )
        )

        policy_result = self._policy.evaluate(proposal, evidence)

        return ProductIdentityResult(
            case_id=command.case_id,
            proposal=proposal,
            evidence=evidence,
            policy=policy_result,
            decision=policy_result.decision,
        )
