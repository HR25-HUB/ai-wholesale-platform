# AI Wholesale Platform — Copilot Instructions

## Project Overview
Enterprise wholesale automation platform (B2B). Event-driven architecture with RFQ processing, supplier matching, pricing, catalog automation, analytics, and CRM/ERP integration.

## Tech Stack
- **Python 3.14** — core language
- **uv** — Python dependency/environment workflow for new services
- **Ruff** — linting and formatting
- **Pyrefly** — static type verification for new Python services
- **FastAPI** — REST API (`app/main.py`)
- **Prefect** — workflow orchestration (`flows/`)
- **Pydantic v2** — typed external/application contracts
- **OpenSearch** — product search and vector retrieval
- **Redpanda** — event streaming (Kafka-compatible)
- **Streamlit** — internal dashboards (`dashboards/`)
- **Docker Compose** — local infrastructure (`infra/`)

## Project Structure
```text
app/                         -> FastAPI app + existing domain models
agents/                      -> AI agents
flows/                       -> Prefect pipelines
ai_platform/                 -> data/AI platform components
contracts/                   -> event and integration schemas
dashboards/                  -> Streamlit dashboards
services/dashboard_factory/  -> verified metric/dashboard vertical slice
scripts/                     -> bootstrap and utility scripts
infra/                       -> local infrastructure
opensearch/                  -> index mappings
tests/                       -> repository-level tests
docs/dashboard_factory/      -> Dashboard Factory ADR/EXECPLAN/docs
```

## Required change protocol
- Read root `AGENTS.md` before non-trivial work.
- Also read the nearest path-specific `.github/instructions/*.instructions.md` file for the files being changed.
- Treat a GitHub Issue as the executable acceptance contract.
- Prefer one end-to-end vertical slice over broad platform design.
- Do not claim tests or gates passed unless they were executed.
- Stop before merge/deploy unless explicitly authorized.

## Architecture rules
- Prefer DDD + Hexagonal Architecture.
- Keep domain/business rules independent from Excel, HTTP, Prefect, Redpanda, OpenSearch, Streamlit, and vendor SDKs.
- Use typed, versioned contracts at system boundaries.
- Side effects must be idempotent; use Inbox/Outbox when transactional boundaries require it.
- AI proposes changes; policy/contracts validate; deterministic gates verify; humans approve semantic or risk-bearing changes.

## Coding Conventions
- Use **Pydantic v2** for boundary/application contracts; frozen dataclasses are acceptable for simple domain value objects.
- Use type hints everywhere.
- Prefer async/await for I/O-bound FastAPI code.
- Prefect tasks should be small, explicit, and idempotent.
- Configuration comes from environment variables; never hardcode secrets.
- Use pytest for automated tests.
- For JS/TS additions, validate external data with **Zod**.

## Python quality gates for new services
```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyrefly check
uv run pytest -q
```

## Dashboard Factory invariant
The analytical chain is:
`source -> canonical dataset -> metric contract -> deterministic metric engine -> verified snapshot -> renderer -> artifact`.

Excel is an adapter/presentation surface, not the source of metric truth. Never hide authoritative business metric semantics in workbook formulas.

## Naming
- snake_case for functions, variables, modules.
- PascalCase for classes and Pydantic models.
- UPPER_SNAKE_CASE for constants and environment variables.

## Important Notes
- Directory `ai_platform/` (NOT `platform/`) avoids conflict with the Python stdlib `platform` module.
- OpenSearch security may be disabled only in local/dev configuration.
- Do not commit `.env`, credentials, production exports, customer data, generated workbooks, or sensitive evidence bundles.
