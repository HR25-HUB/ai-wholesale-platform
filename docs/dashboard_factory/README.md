# Dashboard Factory

## Purpose
Dashboard Factory converts operational datasets into verified metric snapshots and reproducible analytical artifacts.

The first production slice is RFQ analytics. Excel is supported as an input/output adapter, but metric truth belongs to versioned contracts and deterministic code.

## Architecture

```text
Excel/CSV
  -> canonical RFQ dataset
  -> metric contract
  -> metric engine
  -> verified metric snapshot
  -> dashboard specification
  -> XlsxWriter renderer
  -> Excel artifact + evidence metadata
```

## Bounded responsibilities
- **Domain**: metric identity, definitions, results, invariants.
- **Application**: calculate metric, verify snapshot, build dashboard.
- **Infrastructure**: Excel/Parquet/DuckDB/XlsxWriter adapters.
- **AI layer**: proposes contract/spec changes; never becomes the authority for metric truth.

## Safety model
`AI proposes -> schema/policy validates -> deterministic tests execute -> human approves semantic/risk-bearing changes -> system publishes -> audit records`

## Current scope
### DF-001.3
One verified RFQ metric set -> one generated Excel dashboard.

### DF-001.4
One manager dashboard request -> one AI-assisted, test-backed PR.

## Local development
From `services/dashboard_factory`:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pyrefly check
uv run pytest -q
```

## Stop conditions
Do not publish an artifact when any of these are true:
- schema validation failed;
- metric contract is missing/unapproved;
- golden test failed;
- reconciliation failed;
- unknown metric or dimension is referenced;
- renderer output fails semantic artifact tests.
