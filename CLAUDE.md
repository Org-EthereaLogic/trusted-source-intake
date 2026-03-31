# Claude Code Instructions — Trusted Source Intake

## Workspace Intent

This repository is Chapter 1 of the Enterprise Data Trust portfolio. It is a public, evidence-driven repository proving a trusted-source intake control pattern with deterministic sample data, mirrored SQL and Python contract logic, and Databricks bundle scaffolding.

## Decision Order

1. `CLAUDE.md`
2. `CONSTITUTION.md`
3. `DIRECTIVES.md`
4. `AGENTS.md`
5. `SECURITY.md`
6. `README.md`
7. `docs/architecture.md`
8. `docs/case_study.md`

## Non-Negotiable Rules

- Keep Chapter 1 claim-limited to intake, quarantine, replay detection, and ready handoff.
- Do not describe the checked-in sample as a verified five-source-system implementation.
- Keep SQL and Python rule surfaces aligned.
- Keep docs and notebooks aligned with the local demo output and checked-in tests.
- Do not add secrets, proprietary UMIF logic, or hidden IP-bearing terminology.

## Common Commands

```bash
pip install -e ".[dev]"
PYTHONPATH=src python -m pytest -q
python -m ruff check src tests
PYTHONPATH=src python -m intake.demo_metrics
```

## What Exists Today

- `src/lakeflow_sql/` contains the five-file SQL intake pipeline.
- `src/intake/` contains the Python contract checks, deterministic sample-data generator, and demo metrics runner.
- `data/sample/` contains the four checked-in sample batches.
- `resources/` and `databricks.yml` contain the bundle and refresh-job surfaces.
- `notebooks/` contains the seed and review walkthrough notebooks.
- `tests/` contains 56 tests across contracts, sample data, and demo metrics.
- `.github/workflows/ci.yml` runs lint, tests, security, and bundle-validation paths.

## What Does Not Exist Yet

- No verified live Databricks workspace execution evidence in this repository.
- No production credentials, production datasets, or production readiness proof.
- No justification for claims beyond the intake handoff boundary.
