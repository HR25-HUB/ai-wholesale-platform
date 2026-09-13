# Implement one Dashboard Factory change

Use the current GitHub Issue as the acceptance contract.

## Required workflow
1. Read `AGENTS.md`, `.github/copilot-instructions.md`, and `.github/instructions/dashboard-factory.instructions.md`.
2. Inspect only the bounded context required by the issue.
3. State the change classification: schema / metric / renderer / orchestration / docs.
4. Add or update a failing test first for behavior changes.
5. Implement the smallest vertical slice.
6. Run:
   - `uv sync --all-groups`
   - `uv run ruff check .`
   - `uv run ruff format --check .`
   - `uv run pyrefly check`
   - `uv run pytest -q`
7. Do not claim success for gates you did not execute.
8. Produce a PR-ready result containing:
   - acceptance criteria mapping;
   - changed files;
   - tests/gates executed;
   - evidence artifact paths;
   - risks and rollback/stop conditions.

## Non-negotiable constraints
- Do not create hidden metric semantics in Excel formulas.
- Do not use `eval` or arbitrary code execution for YAML contracts.
- Do not invent missing business facts.
- Fail closed on unknown metric IDs, dimensions, or schema versions.
- Do not merge or deploy.
