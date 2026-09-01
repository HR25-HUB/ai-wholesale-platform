# Specification

## Input

`ResolveProductIdentityCommand` with:
- `case_id`
- `rfq_line`
- approved `document_ids`

Golden input:

```text
ABB S203-C16 автомат 3P 16A
```

## Expected identity

```yaml
manufacturer: ABB
product_code: S203-C16
attributes:
  poles: "3"
  rated_current: "16 A"
  trip_curve: "C"
```

## Required behavior

### Positive case

Given a proposal containing all critical claims and an evidence bundle in which every referenced evidence ID resolves, the policy returns `ACCEPTED`.

### Missing evidence

Given a critical claim with no evidence references, the policy returns `REVIEW_REQUIRED` with `MISSING_EVIDENCE`.

### Unresolved evidence

Given a critical claim that references an evidence ID absent from the bundle, the policy returns `REVIEW_REQUIRED` with `UNRESOLVED_EVIDENCE`.

### Missing critical claim

Given no claim for a configured critical attribute, the policy returns `REVIEW_REQUIRED` with `MISSING_CLAIM`.

## Architectural constraints

- Domain code imports no OpenSearch, model-provider, Prefect, Redpanda, FastAPI, or Streamlit modules.
- `SearchPort` and `MultimodalModelPort` are application-facing protocols.
- Model output contains claims and evidence references only; it does not contain the final decision.
- Final decision is computed deterministically by `EvidencePolicy`.

## Acceptance gate

The same golden RFQ must:

1. return `ACCEPTED` with complete evidence;
2. return `REVIEW_REQUIRED` after evidence for any critical attribute is removed.