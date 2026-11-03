# NUIF-PREFECT-001.A1.1 — Repository Inventory → Application Ports → Executable Prefect Flow

## Inventory (2026-11-03)
- `flows/rfq_pipeline.py` was a placeholder printing `RFQ pipeline started`.
- `agents/product_agent.py` is a no-op matcher returning empty matches.
- `app/domain/rfq.py` and `app/domain/product.py` are minimal Pydantic structures.
- `tests/test_basic.py` contains only `assert True`.
- No verified production PIM adapter, approved real RFQLine or deployed Prefect control plane identified in inspected paths.

## Deliberate scope
Adds `ProductCatalogPort`, read-only JSON snapshot adapter, conservative deterministic matching, Pydantic v2 contracts and one local Prefect flow. Domain files remain untouched. No AI calls, supplier/ERP/CRM writes, order creation or customer communication.

**Synthetic-data warning:** Unit tests use synthetic records. A passing synthetic match proves wiring and deterministic policy behavior, NOT real product identity correctness.

## Local verification
Python >=3.11; from repository root:

```powershell
uv sync
uv run pytest tests/test_prefect_rfq.py
uv run python -m flows.rfq_pipeline --rfq-line .\evidence\approved-rfq-line.json --catalog .\evidence\approved-catalog-export.json
```

The evidence files are not provided. Supply one authorized real RFQLine and a sanitized catalog export. RFQ JSON must validate as `RFQLineInput`; catalog JSON must contain a list of `ProductCatalogRecord`. `evidence_ref` must refer to real independent evidence. This slice checks existence of a nonempty reference, not underlying source authenticity; human verification is required before accepting a business decision.

## Execution boundary
Do not enable unattended remote deployments yet. Prefect `@flow` runs locally only. There is no durable business-result storage, evidence registry, verified PIM trust policy, IAM or crash recovery proof. No retries on input or domain failures.

## Acceptance tracker
- [x] Repository inventory for named paths.
- [x] Typed contracts and explicit read-only application port.
- [x] Executable local Prefect flow submitted for CI review.
- [ ] pytest, ruff, pyrefly CI green (not yet verified).
- [ ] Approved real source RFQLine + independent PIM evidence.
- [ ] Real product identity verified end-to-end.
- [ ] Durable deduplication, audit, crash recovery, authorized deployment.

## Rollback
Branch is isolated from main. Close draft PR or revert commit; no production integration was modified.
