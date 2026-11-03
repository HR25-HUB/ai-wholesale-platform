# Practical assignment — one principle, one enforced PR

1. Check out a feature branch from `main` in `HR25-HUB/ai-wholesale-platform`.
2. Copy the kit files at their relative paths into the repository without replacing unrelated files.
3. Run `python -m unittest discover -s tests/architecture -p 'test_*.py' -v`.
4. Run `python scripts/check_architecture.py --root . --report architecture-evidence.json`.
5. Temporarily add `from prefect import flow` to `app/domain/rfq.py`, rerun the scanner, and confirm nonzero exit and a violation in evidence. **Revert this test edit before commit.**
6. Commit kit files, create a PR, inspect `Architecture Gates` and upload artifact.
7. Configure a required status check in GitHub repository branch protection or a repository ruleset only after maintainer approval and a successful pilot PR.

## Definition of Done
- No production behavior is changed by the kit.
- Healthy baseline returns exit code 0.
- Controlled violation returns exit code 1.
- PR check is green for approved code, red for the controlled violation.
- Evidence is available as a CI artifact; maintainer has approved ADR.
- Required check enforcement is explicitly verified after settings are configured.
