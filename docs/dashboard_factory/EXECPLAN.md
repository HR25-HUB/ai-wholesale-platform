# EXECPLAN — Dashboard Factory v0.1

## Objective
Deliver one verified RFQ analytical vertical slice that can be developed and maintained in VS Code with GitHub Copilot under deterministic quality gates.

## Scope
### In
- canonical RFQ line contract;
- versioned metric contract;
- deterministic metric engine;
- verified metric snapshot;
- declarative dashboard specification;
- XlsxWriter renderer boundary;
- tests, CI, evidence metadata;
- Copilot/agent instructions and GitHub change workflow.

### Out
- Redpanda integration;
- Prefect scheduling;
- Superset deployment;
- live 1C/CRM adapters;
- automatic merge/deploy;
- general-purpose semantic layer.

## Milestones
### M1 — DF-001.2 Metric truth
Exit criteria:
- RFQ contract validates;
- `rfq_offer_conversion` contract is versioned;
- metric engine returns numerator, denominator, value;
- golden unit tests pass.

### M2 — DF-001.3 Dashboard-as-Code
Exit criteria:
- dashboard YAML validates;
- renderer consumes verified snapshots only;
- generated workbook contains Dashboard, RFQ_Detail, Evidence;
- no business formula is authoritative inside Excel;
- semantic artifact tests pass.

### M3 — DF-001.4 AI-assisted change
Exit criteria:
- one real GitHub Issue is implemented by Copilot/agent workflow;
- tests and evidence are included in the PR;
- human review confirms metric semantics;
- PR is merge-ready but not auto-merged.

## Quality gates
```text
ruff check
ruff format --check
pyrefly check
pytest
contract validation
golden verification
artifact semantic verification
```

## Evidence required per PR
- acceptance criteria mapping;
- test output summary;
- metric/schema versions affected;
- evidence bundle path or generated CI artifact;
- known risks;
- rollback/stop condition.

## KPIs
| Metric | Baseline | Target | Threshold/Action |
|---|---|---|---|
| manual dashboard formula edits | manual/unknown | 0 | any edit -> investigate |
| metric reconciliation error | unknown | 0 | non-zero -> block |
| change lead time | unknown | < 1 working day for small change | >2 days -> review complexity |
| CI pass before review | inconsistent | 100% | fail -> not review-ready |
| verified metric coverage | 0 | first 4 RFQ KPIs | missing critical KPI -> review |

## Risks
| Risk | Impact | Detection | Mitigation / stop condition |
|---|---|---|---|
| wrong metric grain | high | golden/reconciliation | block release |
| schema drift | high | Pydantic validation | fail closed |
| hidden Excel logic | high | artifact inspection | no authoritative formulas |
| AI invents metric semantics | high | registry validation + review | reject unknown/unapproved metric |
| over-platforming | medium | cycle time | keep current milestone bounded |

## First developer task
Implement `DF-001.2`: one Golden RFQ dataset -> one verified `rfq_offer_conversion` snapshot.
