---
applyTo: "services/dashboard_factory/**,docs/dashboard_factory/**"
---
# Dashboard Factory instructions

Work evidence-first. Preserve separation between data ingestion, metric semantics, verification, and rendering.

## Mandatory model
`source -> canonical dataset -> metric contract -> metric engine -> verified snapshot -> renderer -> artifact`

## Constraints
- Never put business metric formulas in Excel cells as the source of truth.
- Never let a renderer redefine metric semantics.
- Never accept a metric/dimension that is absent from the approved registry.
- Metric contracts must be versioned and validated before execution.
- Prefer constrained YAML/Pydantic specifications over generated arbitrary code.
- Treat schema drift, reconciliation failure, failed golden tests, or unapproved metric semantics as blocking conditions.
- Store evidence metadata, not sensitive business source files, in Git.

## Change protocol
1. Identify whether the change is data schema, metric semantics, rendering, or orchestration.
2. Make the change at the owning layer only.
3. Add the smallest failing test first when behavior changes.
4. Keep adapters replaceable behind ports.
5. Update ADR/EXECPLAN when a decision or scope changes.
6. Report exactly which gates were executed.

## Initial vertical slice
Target `DF-001.3`: verified RFQ KPI snapshots rendered into an Excel dashboard without embedded business formulas.
Then `DF-001.4`: one manager request -> one verified PR.
