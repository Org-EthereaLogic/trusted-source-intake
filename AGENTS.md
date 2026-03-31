# Trusted Source Intake Agent Governance

## Authorized Agent Behavior

All coding agents working in this repository must:

1. Read [README.md](/Users/etherealogic-2/Dev/Databricks/trusted-source-intake/README.md), [architecture.md](/Users/etherealogic-2/Dev/Databricks/trusted-source-intake/docs/architecture.md), and [case_study.md](/Users/etherealogic-2/Dev/Databricks/trusted-source-intake/docs/case_study.md) before proposing or editing code.
2. Treat Chapter 1 as an intake-control repository with its own evidence lineage inside the three-chapter portfolio.
3. Preserve Chapter 1 boundaries. This repo proves trusted intake, replay detection, quarantine, and ready-handoff logic. It does not prove silent drift prevention, benchmark superiority, or live production Databricks execution.
4. Keep the SQL intake rules and Python contract checks aligned. A contract name or rule change in one surface must be reflected in the other.
5. Preserve deterministic sample data and the local demo metrics surface used in the README and case study.
6. Keep docs, notebooks, bundle config, and CI aligned with executable behavior.
7. Keep this public repository free of proprietary UMIF terms, formulas, or hidden IP-bearing logic.

## Claim Scope

- Chapter 1 may validate only the checked-in intake pattern implemented by the SQL pipeline, Python contract checks, deterministic sample batches, and local demo metrics.
- The checked-in sample corpus models one order-events intake domain arriving as four batches. Do not restate that as a verified five-source-system implementation.
- Chapter 1 may not claim production readiness, full-medallion coverage beyond intake handoff, or live Databricks workspace execution without separate evidence.
- Missing test, demo, or provenance evidence blocks completion claims.

## Required Control Surfaces

- `src/lakeflow_sql/` and `src/intake/` are the canonical implementation surfaces.
- `data/sample/` is the canonical demo corpus.
- `resources/`, `databricks.yml`, and `notebooks/` are the canonical deployment and walkthrough surfaces.
- `.github/workflows/ci.yml`, `.codacy.yaml`, and `SECURITY.md` are the baseline quality and security surfaces.

## Hard Stops

- No secrets in repository files, sample data, notebooks, docs, or bundle config.
- No unverifiable KPI, PASS, or readiness claims.
- No documentation changes that diverge from the tested Python behavior or checked-in SQL logic.
- No introduction of proprietary UMIF formulas, terminology, or claim language into this public repository.
