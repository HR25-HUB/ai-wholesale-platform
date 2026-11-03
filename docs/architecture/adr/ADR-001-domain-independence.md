# ADR-001 — Domain independence

- Status: Proposed (requires architect review)
- Date: 2026-11-03
- Context: HR25-HUB/ai-wholesale-platform; `app/domain` contains Pydantic business models.

## Decision
Code in `app/domain/` must not import delivery, agents, workflow or infrastructure modules. Enforce using `ARCH-DOMAIN-001` static AST check in PR CI. Pydantic models are temporarily permitted as part of the observed baseline; this is not a claim of pure domain entities.

## Why
RFQ, Product and Supplier representations must remain testable independently of Prefect, FastAPI and OpenSearch. This is one architectural invariant, not a claim that full hexagonal architecture is already implemented.

## Alternatives
- Document-only guidance: no deterministic enforcement.
- Import linter dependency: more mature tooling but would require project dependency/lock changes.
- Standard-library AST check: narrow, small, explainable pilot, but does not resolve imports hidden in dynamic import calls or runtime dependency injection.

## Consequences
CI fails on newly introduced prohibited imports. Further rules require an explicit ADR and independent tests. Branch protection is a separate GitHub setting and is NOT configured by this kit.

## Falsification
Change `app/domain/rfq.py` to include `from prefect import flow`; CI must fail. Remove the import; CI must pass. A domain import via `importlib.import_module` is outside this baseline and requires a follow-up gate.
