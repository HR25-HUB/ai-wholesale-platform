# RFQ Procurement Control Plane

Production-oriented Next.js bounded context for supplier quote comparison and procurement decisions.

## Scope v0.1

`100 RFQ lines → supplier quotes → deterministic eligibility/ranking → REVIEW/BLOCK/ABSTAIN → manager decision surface`.

The UI is intentionally **read-only**. It must not create purchase orders, send supplier messages, update 1C/Saleor, or mutate RFQ state.

## Stack

- Next.js 16.3 App Router
- React 19.2
- TypeScript 6 strict mode
- Zod for boundary validation (adapter phase)
- Vitest for deterministic domain tests
- pnpm

Node.js 20.9+ is required by current Next.js documentation.

## Local development

```bash
cd apps/rfq-procurement-ui
corepack enable
pnpm install
pnpm dev
```

Open `http://localhost:3000`.

Quality gate:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Architecture

```text
External RFQ / FastAPI / 1C / Saleor
              ↓
        Adapter + Zod
              ↓
      Canonical RFQ Contract
              ↓
       Decision Engine
              ↓
        Policy / Ranking
              ↓
         Next.js UI
```

The domain engine does not import React, Next.js, databases, HTTP clients, or external systems.

## Safety model

`AI proposes → deterministic policy validates → human reviews when required → execution adapter (future) → audit`.

Current allowed effects: none outside rendering and test execution.

## Next vertical slices

1. `v0.1.1` — interactive per-line selection + mandatory justification for non-recommended supplier.
2. `v0.1.2` — landed cost, MOQ, supplier consolidation, balanced offer optimization.
3. `v0.1.3` — customer proposal projection with immutable versions.
4. `v0.1.4` — Golden Scenario Harness.
5. `v0.2` — FastAPI real/shadow adapter, still without production execution.

## Definition of Done for production integration

Do not enable writes until all conditions hold:

- canonical contract validated at adapter boundary;
- critical policy violation cannot produce `DECIDE`;
- `ABSTAIN` is supported and audited;
- Golden + benchmark + adversarial suites pass;
- decisions are traceable to source quotes;
- execution ports are separately permissioned and disabled by default;
- Human-in-the-loop gate exists for policy exceptions.
