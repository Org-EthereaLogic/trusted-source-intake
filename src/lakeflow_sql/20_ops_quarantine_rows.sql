-- Trusted Source Intake — Quarantine rules (7 named contract checks)
-- Every row from bronze_orders_raw is evaluated against all checks.
-- Rows that fail any check land here with an explicit reason array.
-- Replay rows (same batch_id, later file) are also quarantined.

CREATE OR REFRESH MATERIALIZED VIEW ops_quarantine_rows
COMMENT 'Rows that failed one or more intake contract checks with explicit reasons'
AS
WITH replay_batches AS (
  SELECT batch_id
  FROM LIVE.ops_batch_registry
  WHERE is_replay = TRUE
),
ranked AS (
  SELECT
    r.*,
    ROW_NUMBER() OVER (
      PARTITION BY r.batch_id, r.order_id
      ORDER BY r.source_file_ts ASC
    ) AS arrival_rank
  FROM LIVE.bronze_orders_raw r
),
checked AS (
  SELECT
    rk.*,
    ARRAY_COMPACT(ARRAY(
      CASE WHEN rk.batch_id IS NULL
           THEN 'batch_id_not_null' END,
      CASE WHEN rk.order_id IS NULL
           THEN 'order_id_not_null' END,
      CASE WHEN rk.customer_id IS NULL
           THEN 'customer_id_not_null' END,
      CASE WHEN rk.order_total IS NULL OR rk.order_total <= 0
           THEN 'order_total_positive' END,
      CASE WHEN rk.event_ts IS NULL
           THEN 'event_ts_not_null' END,
      CASE WHEN rk.event_ts IS NOT NULL
            AND TRY_CAST(rk.event_ts AS TIMESTAMP) IS NULL
           THEN 'event_ts_parseable' END,
      CASE WHEN rk._rescued_data IS NOT NULL
           THEN 'no_rescued_data' END
    )) AS failed_checks,
    CASE
      WHEN rb.batch_id IS NOT NULL AND rk.arrival_rank > 1
      THEN TRUE ELSE FALSE
    END AS is_replay_duplicate
  FROM ranked rk
  LEFT JOIN replay_batches rb ON rk.batch_id = rb.batch_id
)
SELECT
  batch_id,
  order_id,
  customer_id,
  order_total,
  event_ts,
  product_category,
  region,
  _rescued_data,
  source_file_name,
  ingest_ts,
  failed_checks       AS quarantine_reasons,
  is_replay_duplicate
FROM checked
WHERE SIZE(failed_checks) > 0
   OR is_replay_duplicate = TRUE;
