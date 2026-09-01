# Tasks

## Phase 1 — Domain gate

- [x] Add Product Identity domain models.
- [x] Implement deterministic `EvidencePolicy`.
- [x] Add four policy tests:
  - complete evidence -> `ACCEPTED`;
  - missing evidence -> `REVIEW_REQUIRED`;
  - unresolved evidence -> `REVIEW_REQUIRED`;
  - missing critical claim -> `REVIEW_REQUIRED`.

## Phase 2 — In-memory application slice

- [x] Add `ResolveProductIdentityCommand` and result contract.
- [x] Add `SearchPort` and `MultimodalModelPort` protocols.
- [x] Implement `ResolveProductIdentityHandler`.
- [x] Add `FakeSearchPort` and `FakeMultimodalModelPort`.
- [x] Add an application test proving the end-to-end in-memory path.

## Phase 3 — Golden ABB case

- [x] Add golden fixture for `ABB S203-C16 автомат 3P 16A`.
- [x] Assert expected manufacturer, product code and critical attributes.
- [x] Add evidence mutation test proving removal of critical evidence forces `REVIEW_REQUIRED`.

## Phase 4 — Infrastructure replacement

- [x] Implement `OpenSearchAdapter` behind `SearchPort`.
- [x] Add a dedicated `product_evidence` index mapping and hybrid search pipeline bootstrap.
- [x] Add OpenSearch query/mapping contract tests without requiring a live cluster in CI.
- [x] Implement PydanticAI multimodal model adapter behind `MultimodalModelPort`.
- [x] Add offline PydanticAI adapter tests with model requests disabled.
- [x] Keep domain/application tests unchanged.

## Quality gate

- [x] `pytest` green: 13 tests.
- [x] `ruff check` green.
- [x] `pyrefly check` green.
- [x] Unsupported accepted critical claims = 0.

## Phase 5 — Live integration evidence

- [ ] Render the approved ABB catalogue page into a page-image asset.
- [ ] Ingest real text/page evidence into the `product_evidence` index using one versioned embedding profile.
- [ ] Configure a real PydanticAI multimodal provider through environment/secrets, without provider logic in domain/application layers.
- [ ] Execute the real ABB S203-C16 case end-to-end.
- [ ] Capture retrieval hits, model proposal, evidence references, policy result, latency, and model/prompt versions.
- [ ] Re-run the same case with one critical evidence item removed and prove the final decision becomes `REVIEW_REQUIRED`.

## Live Definition of Done

The live Golden Case may be considered complete only when the same RFQ produces `ACCEPTED` with complete real evidence and deterministically produces `REVIEW_REQUIRED` after a controlled critical-evidence mutation.