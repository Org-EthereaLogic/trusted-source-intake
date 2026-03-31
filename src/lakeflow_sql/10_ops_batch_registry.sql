-- Trusted Source Intake — Batch registry with replay detection
-- Groups ingested rows by business batch_id.
-- Flags replayed batches: same batch_id arriving from more than one source file.

CREATE OR REFRESH MATERIALIZED VIEW ops_batch_registry
COMMENT 'Per-batch metadata with replay detection flags'
AS
WITH batch_files AS (
  SELECT
    batch_id,
    source_file_name,
    MIN(ingest_ts) AS first_seen_ts,
    COUNT(*)       AS row_count
  FROM LIVE.bronze_orders_raw
  GROUP BY batch_id, source_file_name
)
SELECT
  batch_id,
  MIN(first_seen_ts)                          AS batch_first_seen_ts,
  COUNT(DISTINCT source_file_name)            AS file_count,
  SUM(row_count)                              AS total_rows,
  CASE
    WHEN COUNT(DISTINCT source_file_name) > 1 THEN TRUE
    ELSE FALSE
  END                                         AS is_replay,
  COLLECT_SET(source_file_name)               AS source_files
FROM batch_files
GROUP BY batch_id;
