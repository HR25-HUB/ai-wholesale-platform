"""Read-only application use case. Domain-grade identity policy is deterministic."""
from collections.abc import Sequence
from typing import Protocol

from contracts.product_matching import (
    MatchDecision,
    ProductCatalogRecord,
    ProductMatchResult,
    RFQLineInput,
)


class ProductCatalogPort(Protocol):
    def find_by_part_number(self, part_number: str) -> Sequence[ProductCatalogRecord]: ...


def normalize_identity(value: str) -> str:
    """Conservative normalization: no punctuation stripping or fuzzy equivalence."""
    return " ".join(value.strip().casefold().split())


class MatchRFQLine:
    def __init__(self, catalog: ProductCatalogPort):
        self._catalog = catalog

    def execute(self, line: RFQLineInput, correlation_id: str) -> ProductMatchResult:
        candidates = self._catalog.find_by_part_number(line.part_number)
        exact = [
            candidate
            for candidate in candidates
            if normalize_identity(candidate.part_number) == normalize_identity(line.part_number)
            and normalize_identity(candidate.manufacturer) == normalize_identity(line.manufacturer)
        ]
        # Multiple catalog identities must never be silently auto-approved.
        if len(exact) == 1 and exact[0].evidence_ref.strip():
            match = exact[0]
            return ProductMatchResult(
                rfq_line_id=line.rfq_line_id,
                product_id=match.product_id,
                decision=MatchDecision.VERIFIED,
                match_type="EXACT",
                category=match.category,
                evidence_refs=(match.evidence_ref,),
                correlation_id=correlation_id,
            )
        if candidates:
            return ProductMatchResult(
                rfq_line_id=line.rfq_line_id,
                product_id=None,
                decision=MatchDecision.REVIEW_REQUIRED,
                match_type="CANDIDATE",
                evidence_refs=tuple(sorted({c.evidence_ref for c in candidates})),
                correlation_id=correlation_id,
            )
        return ProductMatchResult(
            rfq_line_id=line.rfq_line_id,
            product_id=None,
            decision=MatchDecision.NOT_FOUND,
            match_type="NONE",
            correlation_id=correlation_id,
        )
