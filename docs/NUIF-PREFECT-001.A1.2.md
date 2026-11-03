# NUIF-PREFECT-001.A1.2 — Real RFQLine → Verified PIM Evidence → CI-Gated Prefect Run

## Evidence taxonomy
**FACT (repository):** A1.1 contains local Prefect flow, conservative matching and read-only JSON catalog adapter.
**UNKNOWN:** No approved real RFQLine, independently authenticated PIM source or eligible human reviewer verified by this PR.
**NOT A FACT:** A green synthetic CI run is *not* proof of matching a real SKU.

## Controls
1. Authorized operator obtains exactly one real RFQLine from approved RFQ source and one corresponding catalog export from approved PIM.
2. Strip customer PII and secrets. Store files only in restricted local/evidence storage; **do not commit exports**.
3. Build manifest with SHA-256 digests of the raw JSON files. Record `case_id`, expected approved product ID, `source_system`, immutable source record reference, approver identity, timezone-aware review date and `APPROVED` decision.
4. Independent reviewer verifies the source systems and original records, not just manifest values. The gate checks hashes and consistency; it **cannot authenticate an approver** or guarantee upstream source truth.
5. In isolated, restricted workspace execute:
   ```powershell
   uv run python -m scripts.verify_real_rfq --manifest .\private\manifest.json --rfq .\private\rfq.json --catalog .\private\catalog.json --output .\private\result-evidence.json
   ```
6. Preserve the resulting sanitized evidence bundle in controlled Evidence Registry, linked to original source records and local Prefect run record. The command emits a correlation ID; **a verified Prefect run ID is not yet captured**.
7. Manually review evidence and compare it with the actual PIM record before marking the business outcome VERIFIED.

## CI boundary
GitHub Actions runs Ruff, Pyrefly, pytest (synthetic fixtures) and a dependency-boundary check on PRs. It neither receives nor validates real production data. A1.2 therefore needs BOTH green CI and independently approved restricted real-case verification. Neither substitutes for the other.

## Stop conditions
- Missing authorized real RFQ/PIM evidence.
- No independently identified human approver.
- SHA-256 mismatch.
- Same product ID appears more than once in snapshot.
- Ambiguous identity, missing evidence or unmatched expected result.
- Production secrets or PII in artifacts.
- Any external write or unattended deployment.
- CI failure or unavailable CI result.

## Pending before production
Durable idempotency, source provenance authentication, persistent run-ID linking, tamper-resistant Evidence Registry, failure/restart tests, pinned uv.lock, RBAC and production deployment controls.

## Rollback
Keep this as a draft, stacked on A1.1; no service deployment or live external mutations.
