# Case Study — Trusted Source Intake

Author: Anthony Johnson | EthereaLogic LLC

## Context

Enterprise data platforms that consolidate information from multiple
operational systems face a consistent set of intake challenges. Source systems
change schemas without notice, operations teams resend batches after perceived
failures, and partial extracts arrive with missing required fields.

These problems are well-documented in the data engineering community, but most
organizations address them reactively — debugging production issues after
downstream consumers have already acted on bad data.

## The Pattern

This repository implements a proactive intake control pattern that sits between
file landing and downstream consumption. The pattern has four components:

1. **Raw ingest with rescued data** — Schema drift is captured, not absorbed.
2. **Batch registry** — Business-level replay detection on top of file-level deduplication.
3. **Seven named contract checks** — Failed rows are quarantined with explicit reasons.
4. **Handoff summary** — A single operational view of pipeline health.

## Verified Demo Results

The local demo runs all four test scenarios (33 rows across 4 batches) and
produces the following handoff summary:

| Metric | Value |
|--------|-------|
| Total landed | 33 |
| Total ready | 10 |
| Total quarantined | 23 |
| Replay duplicates | 10 |
| Rescued rows | 8 |
| Ready ratio | 0.303 |
| Quarantine ratio | 0.697 |

The high quarantine ratio is expected — three of the four test batches are
specifically designed to trigger failures. In a production environment with
predominantly clean data, the ready ratio would be significantly higher, and
the quarantine view would surface only the exceptions that need attention.

## Applicability

The intake pattern is source-agnostic. While the demo uses a single
order-events source, the quarantine logic, replay protection, and handoff gate
apply to any JSON, CSV, or Parquet source landed into a Unity Catalog volume.

The pattern is particularly valuable when:

- Multiple source systems feed one platform (e.g., HR, ERP, project management)
- Operations teams have the ability to resend files manually
- Downstream consumers (dashboards, models) start querying soon after landing
- Governance requires audit-ready evidence of data certification
