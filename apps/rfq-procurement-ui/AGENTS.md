# AGENTS.md — RFQ Procurement UI

## Mission
Build a safe, auditable procurement decision surface for wholesale RFQs. Optimize for correctness, traceability, reversibility, and business evidence before automation.

## Non-negotiable architecture
- Domain logic lives under `src/features/procurement/domain` and must remain framework-independent.
- UI components may consume domain results but must not contain supplier-ranking or policy logic.
- External systems enter through typed adapters; validate untrusted payloads before canonical contracts.
- Never add direct writes to 1C, Saleor, supplier email, PO creation, or RFQ status from UI code.
- Any future execution path must implement: `proposal → policy → deterministic gate → human approval if required → execution → audit`.

## Decision safety
- Critical anomalies must never produce an autonomous `DECIDE`.
- Unknown/insufficient evidence should become `ABSTAIN`, not guessed values.
- Partial availability cannot be represented as full availability.
- Expired quotations cannot be selected.
- Substitutions must be explicit.
- Non-recommended/manual selections require a reason in the future write-enabled slice.

## Engineering workflow
1. Read this file and `.github/copilot-instructions.md`.
2. State the affected domain contract/invariant in the PR.
3. Implement the smallest vertical slice.
4. Run `pnpm lint && pnpm typecheck && pnpm test && pnpm build` from this app.
5. Do not update expected baselines merely to make tests green; explain business changes.

## Completion evidence
Every PR touching procurement decisions must report:
- changed invariants/policies;
- test results;
- whether any recommendation/economic result changed;
- new failure modes introduced/mitigated;
- rollback path.
