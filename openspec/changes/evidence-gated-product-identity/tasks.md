# Tasks

## Phase 1 — Domain gate

- [ ] Add Product Identity domain models.
- [ ] Implement deterministic `EvidencePolicy`.
- [ ] Add four policy tests:
  - complete evidence -> `ACCEPTED`;
  - missing evidence -> `REVIEW_REQUIRED`;
  - unresolved evidence -> `REVIEW_REQUIRED`;
  - missing critical claim -> `REVIEW_REQUIRED`.

## Phase 2 — In-memory application slice

- [ ] Add `ResolveProductIdentityCommand` and result contract.
- [ ] Add `SearchPort` and `MultimodalModelPort` protocols.
- [ ] Implement `ResolveProductIdentityHandler`.
- [ ] Add `FakeSearchPort` and `FakeMultimodalModelPort`.
- [ ] Add an application test proving the end-to-end in-memory path.

## Phase 3 — Golden ABB case

- [ ] Add golden fixture for `ABB S203-C16 автомат 3P 16A`.
- [ ] Assert expected manufacturer, product code and critical attributes.
- [ ] Add evidence mutation test proving removal of critical evidence forces `REVIEW_REQUIRED`.

## Phase 4 — Infrastructure replacement

- [ ] Implement `OpenSearchAdapter` behind `SearchPort`.
- [ ] Implement real multimodal model adapter behind `MultimodalModelPort`.
- [ ] Keep domain/application tests unchanged.

## Quality gate

- [ ] `pytest` green.
- [ ] `ruff check` green.
- [ ] `pyrefly check` green once configured in repository tooling.
- [ ] Unsupported accepted critical claims = 0.