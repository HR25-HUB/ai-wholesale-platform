# Design

## Boundary

The Product Identity slice follows Hexagonal Architecture.

```text
Input Adapter
    |
ResolveProductIdentityHandler
    |
    +--> SearchPort ------------> FakeSearch / OpenSearchAdapter
    |
    +--> MultimodalModelPort ---> FakeMultimodalModel / real model adapter
    |
    '--> EvidencePolicy --------> ProductIdentityResult
```

## Domain

Core types:
- `Evidence`
- `EvidenceBundle`
- `EvidenceRef`
- `ProductClaim`
- `ProductIdentityProposal`
- `IdentityDecision`
- `PolicyViolation`
- `EvidencePolicyResult`

The domain owns decision semantics. Infrastructure may provide evidence or claims but cannot decide acceptance.

## Application

`ResolveProductIdentityHandler` performs:

1. Retrieve evidence using `SearchPort`.
2. Build an immutable `EvidenceBundle`.
3. Ask `MultimodalModelPort` for a typed `ProductIdentityProposal`.
4. Run `EvidencePolicy`.
5. Return `ProductIdentityResult`.

## Adapters

v0.1 starts with fake adapters so the full application path is executable without external systems.

Real adapters are introduced behind the same ports:
- OpenSearch hybrid retrieval adapter.
- Multimodal model adapter.

## Failure semantics

Semantic uncertainty is not an infrastructure exception.

- Missing claim -> `REVIEW_REQUIRED`.
- Missing evidence -> `REVIEW_REQUIRED`.
- Broken evidence reference -> `REVIEW_REQUIRED`.
- External I/O failure -> adapter/application error handling, not a domain decision.

## Future extension

Redpanda events and Prefect flows may wrap the application use case after the synchronous golden slice is proven. They must not change domain policy semantics.