# Architecture — Trusted Source Intake

Author: Anthony Johnson | EthereaLogic LLC

## Overview

This document describes the data flow and design rationale for the intake
control pattern implemented in this repository.

## Data Flow

```
Source Files (JSON)
  │
  ▼
Landing Volume (Unity Catalog)
  │  /Volumes/{catalog}/{schema}/landing/
  │
  ▼
┌──────────────────────────────────────────────────┐
│  00_bronze_raw_ingest.sql                        │
│  STREAMING TABLE: bronze_orders_raw              │
│  Auto Loader with rescued data mode              │
│  Captures: business columns + _rescued_data +    │
│            file metadata + ingest timestamp       │
└──────────────┬───────────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌────────────────────┐
│ 10_ops_     │  │ 20_ops_            │
│ batch_      │  │ quarantine_        │
│ registry    │  │ rows               │
│             │  │                    │
│ Groups by   │  │ 7 named checks:   │
│ batch_id,   │  │ • batch_id_not_null│
│ detects     │  │ • order_id_not_null│
│ replays     │  │ • customer_id_...  │
│ (multi-file │  │ • order_total_pos  │
│  batches)   │  │ • event_ts_not_null│
└─────────────┘  │ • event_ts_parse   │
                 │ • no_rescued_data  │
                 │                    │
                 │ + replay duplicate │
                 │   detection        │
                 └────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  30_bronze_ready.sql                             │
│  MATERIALIZED VIEW: bronze_ready                 │
│  Only rows passing all 7 checks + not replay dup │
│  This is the certified output for downstream.    │
└──────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│  40_ops_handoff_summary.sql                      │
│  MATERIALIZED VIEW: ops_handoff_summary          │
│  Aggregates: landed / ready / quarantined /      │
│              rescued / replay counts + ratios    │
└──────────────────────────────────────────────────┘
```

## Design Decisions

**Rescued data over schema enforcement.** Auto Loader's `rescuedDataColumn`
captures schema drift into a dedicated column instead of failing the pipeline.
This means drift is visible and quarantined rather than silently absorbed or
causing pipeline failures.

**Business-level replay detection.** Auto Loader deduplicates at the file level
(same file path won't be re-ingested). But enterprise operations teams often
resend a batch under a new file name. The batch registry catches this by
grouping on `batch_id` and flagging batches that arrive from multiple files.

**Explicit quarantine reasons.** Every quarantined row carries an array of the
specific contract checks it failed. This replaces the common pattern of silently
filtering bad rows — which makes debugging production issues much harder.

**Ready gate before consumption.** The `bronze_ready` view is the first point
where downstream consumers should query. By separating raw ingest from the
certified output, the pattern ensures no one queries data that hasn't passed
validation.

## Contract Checks

| # | Check Name | SQL Expression | Failure Meaning |
|---|------------|---------------|-----------------|
| 1 | `batch_id_not_null` | `batch_id IS NULL` | Row has no batch identity |
| 2 | `order_id_not_null` | `order_id IS NULL` | Row has no record identity |
| 3 | `customer_id_not_null` | `customer_id IS NULL` | Missing business entity |
| 4 | `order_total_positive` | `order_total IS NULL OR <= 0` | Invalid transaction amount |
| 5 | `event_ts_not_null` | `event_ts IS NULL` | Missing event timestamp |
| 6 | `event_ts_parseable` | `TRY_CAST(event_ts AS TIMESTAMP) IS NULL` | Unparseable timestamp |
| 7 | `no_rescued_data` | `_rescued_data IS NOT NULL` | Schema drift detected |

## Deployment

The repository uses Databricks Asset Bundles for deployment:

```bash
databricks bundle validate --target dev
databricks bundle deploy --target dev
```

The bundle config (`databricks.yml`) parameterizes catalog, schema, and landing
path so the same pipeline can be deployed to dev, test, and prod targets.
