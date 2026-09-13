# ADR-001 — Business metrics SHALL NOT use Excel formulas as the source of truth

- Status: Proposed
- Context: Dashboard Factory v0.1

## Context
Manual and AI-generated Excel dashboards can embed business semantics in workbook formulas. This makes metric lineage, versioning, testing, reconciliation, and reuse difficult.

## Decision
Business metric definitions SHALL live in versioned metric contracts and deterministic Python/SQL implementation.

Excel MAY:
- display verified values;
- contain presentation-only formulas where required by rendering constraints;
- provide filtering and drill-down views.

Excel SHALL NOT be the authoritative implementation of business metric semantics.

## Consequences
### Positive
- metrics are testable and reproducible;
- Excel, API, Streamlit, and future BI tools can share the same semantics;
- metric changes are reviewable Git changes;
- AI-generated dashboard changes have a constrained safety boundary.

### Negative
- higher initial engineering cost;
- metric registry and contract validation require maintenance;
- legacy Excel dashboards need migration rather than direct reuse.

## Verification
A dashboard release must be blocked when:
- a referenced metric is unknown;
- its contract is invalid/unapproved;
- golden or reconciliation checks fail;
- the rendered value differs from the verified snapshot.

## Revisit when
A dedicated semantic-layer product is introduced and can provide equivalent versioning, deterministic execution, lineage, and tests.
