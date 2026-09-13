# AGENTS.md — AI Wholesale Platform

## Mission
Build production-grade automation for B2B wholesale operations. Prefer one verified vertical slice over broad platform work.

## Operating protocol
Use this change loop for every non-trivial task:

1. Read the issue, relevant docs, contracts, tests, and nearest `AGENTS.md`.
2. Restate the executable acceptance contract before editing.
3. Identify the bounded context and keep domain logic out of adapters/UI.
4. Implement the smallest end-to-end slice.
5. Add or update tests before declaring completion.
6. Run deterministic quality gates.
7. Produce evidence: changed files, tests, commands, assumptions, residual risks.
8. Stop before merge/deploy unless explicitly authorized.

## Architecture rules
- Prefer DDD + Hexagonal Architecture.
- Domain code must not depend on Excel, HTTP, Redpanda, Prefect, OpenSearch, Streamlit, or vendor SDKs.
- Use typed contracts for all boundaries.
- Use Pydantic v2 for external/application contracts; domain value objects may use frozen dataclasses when simpler.
- Use explicit schema/event versioning.
- Side-effecting consumers must be idempotent; use Inbox/Outbox when crossing transactional boundaries.
- AI may propose; policy validates; deterministic gates verify; a human approves risk-bearing changes.
- Business metrics must be defined outside Excel formulas and UI code.

## Python quality gates
Required before a PR is ready:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyrefly check
uv run pytest -q
```

If a repository-level command is unavailable, run the equivalent command in the changed service and record that limitation in the PR.

## Testing
- Unit tests: domain rules and pure transformations.
- Contract tests: Pydantic/YAML/event schemas.
- Integration tests: adapters against controlled fixtures.
- Golden tests: fixed real-world-like datasets with explicit expected outcomes.
- Never replace deterministic assertions with an LLM judgment.

## Dashboard Factory rules
For `services/dashboard_factory/**`:
- Excel is an input/output adapter, never the source of metric truth.
- Metric definitions live in versioned contracts.
- Rendering consumes verified metric snapshots.
- Unknown metrics or dimensions must fail closed.
- Generated workbooks must include evidence/lineage metadata.
- No arbitrary `eval`, dynamic Python execution, or unreviewed SQL from metric YAML.

## Git discipline
- Branch from `main`.
- One issue = one coherent change/PR when practical.
- Prefer Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- Do not commit secrets, credentials, private exports, generated `.xlsx`, evidence containing customer data, or local `.env` files.
- Do not rewrite shared history.

## Definition of Done
A change is done only when:
- acceptance criteria are satisfied;
- tests cover the new behavior;
- deterministic gates pass;
- docs/contracts are updated when semantics change;
- evidence is attached to the PR;
- risks and rollback/stop conditions are explicit.
