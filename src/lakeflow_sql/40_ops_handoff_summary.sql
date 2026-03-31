-- Trusted Source Intake — Operational handoff summary
-- Single-pane view aggregating the full intake pipeline into operational
-- metrics: landed, ready, quarantined, rescued, and replay counts.

CREATE OR REFRESH MATERIALIZED VIEW ops_handoff_summary
COMMENT 'Single-pane operational view of intake pipeline health'
AS
WITH raw_counts AS (
  SELECT
    COUNT(*)                                              AS total_landed,
    SUM(CASE WHEN _rescued_data IS NOT NULL THEN 1 ELSE 0 END) AS rescued_rows
  FROM LIVE.bronze_orders_raw
),
ready_count AS (
  SELECT COUNT(*) AS total_ready
  FROM LIVE.bronze_ready
),
quarantine_counts AS (
  SELECT
    COUNT(*)                                                    AS total_quarantined,
    SUM(CASE WHEN is_replay_duplicate = TRUE THEN 1 ELSE 0 END) AS replay_duplicates
  FROM LIVE.ops_quarantine_rows
),
batch_counts AS (
  SELECT
    COUNT(*)                                        AS total_batches,
    SUM(CASE WHEN is_replay = TRUE THEN 1 ELSE 0 END) AS replay_batches
  FROM LIVE.ops_batch_registry
)
SELECT
  rc.total_landed,
  rd.total_ready,
  qc.total_quarantined,
  qc.replay_duplicates,
  rc.rescued_rows,
  bc.total_batches,
  bc.replay_batches,
  ROUND(rd.total_ready / NULLIF(rc.total_landed, 0), 4)        AS ready_ratio,
  ROUND(qc.total_quarantined / NULLIF(rc.total_landed, 0), 4)  AS quarantine_ratio,
  current_timestamp()                                           AS summary_ts
FROM raw_counts rc
CROSS JOIN ready_count rd
CROSS JOIN quarantine_counts qc
CROSS JOIN batch_counts bc;
