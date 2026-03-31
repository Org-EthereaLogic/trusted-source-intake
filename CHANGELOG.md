# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] — 2026-03-31

### Added

- Five-file SQL pipeline: raw ingest, batch registry, quarantine rules, ready output, handoff summary
- Seven named contract checks mirroring SQL quarantine logic in Python
- Deterministic sample data generator with four enterprise failure scenarios
- Local demo metrics runner producing handoff summary and batch registry
- Databricks Asset Bundle configuration with dev/prod targets
- Lakeflow Declarative Pipeline resource definition
- Demo job resource with seed + pipeline refresh tasks
- Two Databricks notebooks: seed demo files and review outputs
- Architecture documentation with data flow diagram and design decisions
- Case study documentation with verified demo results
- CI workflow with Codacy, Codecov, and Snyk integration
- 56 passing tests across contracts, sample data, and demo metrics
