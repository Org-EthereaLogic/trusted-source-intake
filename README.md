# Before Anyone Queries Bronze, How Do You Know the Data Is Ready?

**Enterprise Data Trust — Chapter 1: Trusted Source Intake**

Built by Anthony Johnson | EthereaLogic LLC

---

Source systems silently send duplicate batches, drop required fields, or change schemas without notice — and downstream consumers start using the data before anyone has validated it.

This chapter demonstrates a governed intake gate that catches schema drift, blocks duplicate replays, quarantines invalid records with explicit reasons, and certifies what is safe for downstream consumption.

Every decision made from the platform depends on the assumption that ingested data is complete, unique, and contract-compliant. This chapter proves that assumption can be enforced — and shows what happens when it is not.

## Executive Summary

| Leadership question | Answer |
| ------------------- | ------ |
| What business risk does this address? | Source systems silently send duplicate batches, drop required fields, or change schemas — and downstream consumers start using the data before anyone has validated it. |
| What does this chapter prove? | A four-component intake control that catches schema drift, blocks duplicate replays, quarantines invalid records with explicit reasons, and provides a single operational view of batch health. |
| Why does it matter? | Every downstream decision depends on trusting that ingested data is complete, unique, and contract-compliant. This pattern enforces that assumption before anyone queries Bronze. |

## Key Exhibits

### Exhibit 1: Single-Pane Intake Verdict

The operational handoff summary shows the full pipeline outcome in one view — 33 rows landed, 10 ready, 23 quarantined, 10 replay duplicates blocked, 8 rescued from schema drift.

<p align="center">
  <img src="docs/images/ch1/03_handoff_summary.png" alt="Handoff summary showing 33 landed, 10 ready, 23 quarantined, 10 replay, 8 rescued" width="900"/>
</p>

### Exhibit 2: Pipeline Completion with Zero Failures

The Databricks pipeline refresh completed all five tables with zero warnings and zero failures — proving the control pattern runs cleanly on the platform.

<p align="center">
  <img src="docs/images/ch1/02_refresh_success.png" alt="Pipeline refresh showing 5 tables completed, 0 warnings, 0 failures" width="900"/>
</p>

### Exhibit 3: Explicit Quarantine with Named Violations

Every blocked row carries an array of named check failures. Nothing is silently dropped — 23 rows quarantined with explicit reason arrays showing exactly which contract checks failed.

<p align="center">
  <img src="docs/images/ch1/05_quarantine_reasons.png" alt="23 rows quarantined with explicit reason arrays" width="900"/>
</p>

## The Business Problem

Enterprise ingestion pipelines face four problems that consistently erode trust in the data platform:

- **Schema drift goes unnoticed.** A source system changes a field. The pipeline absorbs the change silently. Downstream reports break — or worse, they produce numbers that look right but aren't.
- **Duplicate batches slip through.** Operations resends yesterday's file under a new name. Without business-level deduplication, every downstream aggregate is inflated.
- **Required fields arrive empty.** A partial extract produces rows where key business fields are null. These rows pass basic schema checks because the columns exist.
- **Consumers query before validation.** Dashboards and models start reading from Bronze the moment data lands. There is no gate between "data arrived" and "data is ready."

These are not edge cases. They are the daily operational reality of enterprise data engineering.

## What This Repository Proves

| Verified outcome | Evidence from this repository |
| ---------------- | ----------------------------- |
| Schema drift is captured, not absorbed | Auto Loader rescued data mode isolates drifted columns; 8 rows rescued and quarantined |
| Duplicate replays are blocked | Batch registry detects business-level replays; 10 rows flagged across redelivered batches |
| Invalid records are quarantined with reasons | 7 named contract checks produce explicit violation arrays; 23 rows quarantined |
| Handoff gate provides a single operational view | One materialized view aggregates landed, ready, quarantined, rescued, and replay counts |

## Decision / KPI Contract

**Business decision:** should downstream users trust today's landed data?

| KPI | Meaning |
| --- | ------- |
| `total_landed` | Rows ingested from source files |
| `total_ready` | Rows that passed all 7 contract checks and replay detection |
| `total_quarantined` | Rows blocked with explicit reason arrays |
| `replay_duplicates` | Rows from redelivered batches, blocked at the registry level |
| `rescued_rows` | Rows with schema drift captured in `_rescued_data` |

**Control rule:** only `bronze_ready` is downstream-safe. All other tables are operational surfaces for triage, audit, and replay investigation.

## Why This Pattern

- **Gap 1.** Raw ingest alone is not certification. A pipeline that absorbs every file without checking completeness, uniqueness, or schema conformance provides no basis for downstream trust.
- **Gap 2.** Replay detection must be business-level, not file-level. The platform deduplicates files, but business teams resend the same batch under new filenames. The batch registry catches this.
- **Gap 3.** Quarantine must use explicit reasons, not silent filtering. Every blocked row carries an array of named check failures so operations teams can triage without guessing.

## How It Works

1. **Raw ingest with rescued data.** Auto Loader captures everything, including schema changes, into a streaming table. Drift is rescued into a dedicated column rather than silently absorbed.
2. **Batch registry.** A materialized view groups ingested rows by business batch identifier and tracks first-seen timestamps, file counts, and replay flags.
3. **Seven named contract checks.** Every row must pass all seven validation rules before reaching the ready output. Failed rows are quarantined with explicit reason arrays.
4. **Operational handoff summary.** A single materialized view aggregates the full pipeline into actionable metrics: landed, ready, quarantined, rescued, and duplicate counts with ratios.
5. **Downstream gate.** Only `bronze_ready` is published as downstream-safe. All other tables exist for operational review.

For the full architecture diagram and design rationale, see [docs/architecture.md](docs/architecture.md).

## Databricks Fit

- **Lakeflow Declarative Pipelines** (formerly DLT) for streaming ingestion and materialized views.
- **Auto Loader** with `cloudFiles` for incremental file processing with rescued data mode.
- **Unity Catalog** for governed table publication and volume-based landing zones.
- **Databricks Asset Bundles** for source-controlled deployment and pipeline refresh.
- The intake pattern is source-agnostic and applies to any enterprise ingestion pipeline regardless of source count.

## Reproducibility

```bash
git clone https://github.com/Org-EthereaLogic/trusted-source-intake.git
cd trusted-source-intake

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
PYTHONPATH=src pytest tests/ -q    # Expected: 56 passed
PYTHONPATH=src python -m intake.demo_metrics
```

## Evidence Appendix

| Evidence item | What it shows |
| ------------- | ------------- |
| ![Seeded landing volume](docs/images/ch1/01_seeded_landing_volume.png) | 4 batch directories landed in the Unity Catalog volume |
| ![Batch registry](docs/images/ch1/04_batch_registry_replay.png) | B-001 replay detected: file_count=2, is_replay=true |
| ![Ready rows](docs/images/ch1/06_ready_rows.png) | B-001 = 10 ready rows — only the clean batch passes |

## Scope Boundary

This validates the intake control pattern on one order-events source across four sample batches in a Databricks Free Edition workspace. It does not constitute production-scale proof or multi-source verification. The demonstration models a daily order-events source designed to trigger specific failure modes. The pattern itself is source-agnostic.

## Engineering Signals

- GitHub Actions workflow: [ci.yml](https://github.com/Org-EthereaLogic/trusted-source-intake/actions/workflows/ci.yml)

## Additional Documentation

- [Architecture and design rationale](docs/architecture.md)
- [Implementation case study](docs/case_study.md)

## Part of a Series

This is **Chapter 1** of the *Enterprise Data Trust* portfolio — a three-part body of work addressing the full lifecycle of data reliability in enterprise Databricks platforms.

| Chapter | Focus | Repository |
| ------- | ----- | ---------- |
| **1. Trusted Source Intake** | Validate and certify data before downstream consumption | ← You are here |
| 2. Silent Failure Prevention | Detect distribution drift before it reaches executive dashboards | [silent-failure-prevention](https://github.com/Org-EthereaLogic/silent-failure-prevention) |
| 3. Measurable Control Effectiveness | Prove that your data controls work against known failure scenarios | [measurable-control-effectiveness](https://github.com/Org-EthereaLogic/measurable-control-effectiveness) |

MIT License. See [LICENSE](LICENSE.md) for details.
