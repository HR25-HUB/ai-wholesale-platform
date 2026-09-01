import asyncio
import json
from pathlib import Path

from app.adapters.product_identity.fakes import (
    FakeMultimodalModelPort,
    FakeSearchPort,
)
from app.application.product_identity.contracts import ResolveProductIdentityCommand
from app.application.product_identity.handler import ResolveProductIdentityHandler
from app.domain.product_identity import (
    Evidence,
    EvidenceModality,
    EvidencePolicy,
    EvidenceRef,
    IdentityDecision,
    ProductClaim,
    ProductIdentityProposal,
)


FIXTURE_PATH = Path("evaluation/golden/abb_s203_c16.json")


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def build_evidence(fixture: dict[str, object]) -> list[Evidence]:
    document = fixture["document"]
    assert isinstance(document, dict)
    document_id = document["document_id"]
    source_pdf = document["source_pdf"]
    evidence_rows = fixture["evidence"]
    assert isinstance(document_id, str)
    assert isinstance(source_pdf, str)
    assert isinstance(evidence_rows, list)

    items: list[Evidence] = []
    for row in evidence_rows:
        assert isinstance(row, dict)
        evidence_id = row["evidence_id"]
        page = row["page"]
        summary = row["summary"]
        assert isinstance(evidence_id, str)
        assert isinstance(page, int)
        assert isinstance(summary, str)
        items.append(
            Evidence(
                evidence_id=evidence_id,
                document_id=document_id,
                page=page,
                modality=EvidenceModality.PAGE_IMAGE,
                text=summary,
                asset_uri=f"{source_pdf}#page={page}",
                content_hash=f"golden-{evidence_id}",
            )
        )
    return items


def build_proposal(
    fixture: dict[str, object],
    *,
    remove_evidence_for: str | None = None,
) -> ProductIdentityProposal:
    expected_claims = fixture["expected_claims"]
    assert isinstance(expected_claims, dict)

    claims: list[ProductClaim] = []
    for attribute, value in expected_claims.items():
        assert isinstance(attribute, str)
        assert isinstance(value, str)
        evidence = (
            []
            if attribute == remove_evidence_for
            else [EvidenceRef(evidence_id=f"ev-{attribute}")]
        )
        claims.append(
            ProductClaim(
                attribute=attribute,
                value=value,
                evidence=evidence,
            )
        )

    return ProductIdentityProposal(
        claims=claims,
        model_id="golden-fixture",
        prompt_version="v0.1",
    )


def run_case(
    fixture: dict[str, object],
    *,
    remove_evidence_for: str | None = None,
):
    critical_attributes = fixture["critical_attributes"]
    document = fixture["document"]
    case_id = fixture["case_id"]
    rfq_line = fixture["rfq_line"]
    assert isinstance(critical_attributes, list)
    assert all(isinstance(item, str) for item in critical_attributes)
    assert isinstance(document, dict)
    assert isinstance(document["document_id"], str)
    assert isinstance(case_id, str)
    assert isinstance(rfq_line, str)

    evidence = build_evidence(fixture)
    handler = ResolveProductIdentityHandler(
        search=FakeSearchPort(evidence),
        model=FakeMultimodalModelPort(
            build_proposal(
                fixture,
                remove_evidence_for=remove_evidence_for,
            )
        ),
        policy=EvidencePolicy(critical_attributes),
    )

    return asyncio.run(
        handler.execute(
            ResolveProductIdentityCommand(
                case_id=case_id,
                rfq_line=rfq_line,
                document_ids=[document["document_id"]],
            )
        )
    )


def test_golden_abb_s203_c16_is_accepted_with_complete_evidence() -> None:
    fixture = load_fixture()

    result = run_case(fixture)

    assert result.decision is IdentityDecision.ACCEPTED
    product_code = result.proposal.claim_by_attribute("product_code")
    assert product_code is not None
    assert product_code.value == "S203-C16"


def test_removing_any_critical_evidence_forces_review() -> None:
    fixture = load_fixture()
    critical_attributes = fixture["critical_attributes"]
    assert isinstance(critical_attributes, list)

    for attribute in critical_attributes:
        assert isinstance(attribute, str)
        result = run_case(fixture, remove_evidence_for=attribute)

        assert result.decision is IdentityDecision.REVIEW_REQUIRED
        assert any(
            violation.attribute == attribute
            and violation.code == "MISSING_EVIDENCE"
            for violation in result.policy.violations
        )
