# Evidence-Gated Product Identity

## Goal

Prove one trustworthy Product Identity vertical slice for the RFQ line `ABB S203-C16 автомат 3P 16A`.

The slice must identify the product from retrieved technical-document evidence and must never accept a critical product claim that cannot be resolved to evidence from the approved evidence bundle.

## Business outcome

Reduce manual RFQ product-identification work while preserving an auditable human-review boundary.

## Scope

In scope:
- Product Identity domain contracts.
- Deterministic `EvidencePolicy`.
- `SearchPort` and `MultimodalModelPort`.
- Fake adapters for in-memory tests.
- One ABB S203-C16 golden case.
- OpenSearch and multimodal adapters as replaceable infrastructure boundaries.

Out of scope:
- PIM mutation.
- Substitute/analogue selection.
- Supplier sourcing.
- Pricing and proposal generation.
- Redpanda/Prefect orchestration in the executable path.

## Core invariant

`No Evidence -> No Accepted Critical Claim`.

A complete evidence set may yield `ACCEPTED`. Missing, unresolved, or absent evidence for any critical attribute must yield `REVIEW_REQUIRED`.

## Critical attributes for the golden case

- `manufacturer`
- `product_code`
- `poles`
- `rated_current`
- `trip_curve`

## Success criteria

1. Domain policy tests are deterministic and infrastructure-free.
2. The in-memory application slice passes using fake adapters.
3. Golden ABB S203-C16 resolves to the expected product identity when evidence is complete.
4. Removing evidence for any critical attribute changes the decision to `REVIEW_REQUIRED`.
5. The LLM/model adapter cannot set the final decision.