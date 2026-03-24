# AI Wholesale Platform — Copilot Instructions

## Project Overview
Enterprise wholesale automation platform (B2B). Event-driven architecture with
RFQ processing, supplier matching, dynamic pricing, and Bitrix24 CRM integration.

## Tech Stack
- **Python 3.14** — core language
- **FastAPI** — REST API (`app/main.py`)
- **Prefect** — workflow orchestration (`flows/`)
- **Pydantic v2** — domain models (`app/domain/`)
- **OpenSearch 2.15** — product search and vector embeddings
- **Redpanda** — event streaming (Kafka-compatible)
- **Streamlit** — internal dashboards (`dashboards/`)
- **Docker Compose** — local infrastructure (`infra/`)

## Project Structure
```
app/            → FastAPI app + Pydantic domain models
agents/         → AI agents (pricing, product, supplier)
flows/          → Prefect pipelines (rfq, catalog, procurement)
ai_platform/    → Data factory: parsing, embeddings, knowledge graph
contracts/      → Event schemas (pricing_events, rfq_events)
dashboards/     → Streamlit dashboards
scripts/        → Bootstrap and utility scripts
infra/          → Docker Compose, infrastructure configs
opensearch/     → Index mappings
tests/          → Pytest test suite
```

## Coding Conventions
- Use **Pydantic v2** BaseModel for all data structures; prefer `model_validator` over `validator`.
- Use **type hints** everywhere; target `basic` type checking level.
- Prefer **async/await** for I/O-bound code in FastAPI endpoints.
- Prefect flows use `@flow` / `@task` decorators; keep tasks small and idempotent.
- All configuration via environment variables (no hardcoded secrets).
- Test files go in `tests/`, named `test_*.py`, use pytest.

## Naming
- snake_case for functions, variables, modules.
- PascalCase for classes and Pydantic models.
- UPPER_SNAKE_CASE for constants and env vars.

## Important Notes
- Directory `ai_platform/` (NOT `platform/`) — renamed to avoid conflict with Python stdlib `platform` module.
- OpenSearch runs with security disabled in dev (DISABLE_SECURITY_PLUGIN=true).
- Virtual env is at `.venv/`.
