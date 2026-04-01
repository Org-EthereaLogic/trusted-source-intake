-- Trusted Source Intake — Raw ingest with rescued data
-- Streaming table: captures every landed file via Auto Loader.
-- Schema drift is rescued into _rescued_data rather than silently absorbed.

CREATE OR REFRESH STREAMING TABLE bronze_orders_raw
COMMENT 'Raw ingest from landing volume with rescued data for schema drift visibility'
AS SELECT
  batch_id,
  order_id,
  customer_id,
  CAST(order_total AS DOUBLE) AS order_total,
  event_ts,
  product_category,
  region,
  _rescued_data,
  _metadata.file_name            AS source_file_name,
  _metadata.file_modification_time AS source_file_ts,
  current_timestamp()            AS ingest_ts
FROM STREAM read_files(
  '${landing_path}',
  format             => 'json',
  rescuedDataColumn  => '_rescued_data',
  multiLine          => 'true',
  schemaEvolutionMode => 'rescue'
);
