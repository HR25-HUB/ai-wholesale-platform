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
- [ ] Implement real multimodal model adapter behind `MultimodalModelPort`.
- [x] Keep domain/application tests unchanged.

## Quality gate

- [x] `pytest` green.
- [x] `ruff check` green.
- [x] `pyrefly check` green.
- [x] Unsupported accepted critical claims = 0.
