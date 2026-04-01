# Databricks notebook source
# MAGIC %md
# MAGIC # Review Pipeline Outputs
# MAGIC
# MAGIC Run this notebook after a pipeline refresh to inspect the intake
# MAGIC control results: handoff summary, batch registry, quarantine
# MAGIC details, and certified ready rows.

# COMMAND ----------

dbutils.widgets.text("catalog", "main")
dbutils.widgets.text("schema", "trusted_source_intake")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")
print(f"Reviewing {catalog}.{schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Handoff Summary — single-pane operational view

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM ops_handoff_summary;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Batch Registry — per-batch metadata and replay flags

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   batch_id,
# MAGIC   batch_first_seen_ts,
# MAGIC   file_count,
# MAGIC   total_rows,
# MAGIC   is_replay,
# MAGIC   source_files
# MAGIC FROM ops_batch_registry
# MAGIC ORDER BY batch_first_seen_ts;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Quarantine Details — failed rows with reasons

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   batch_id,
# MAGIC   order_id,
# MAGIC   customer_id,
# MAGIC   order_total,
# MAGIC   event_ts,
# MAGIC   quarantine_reasons,
# MAGIC   is_replay_duplicate,
# MAGIC   source_file_name
# MAGIC FROM ops_quarantine_rows
# MAGIC ORDER BY batch_id, source_file_name;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Ready Rows — certified for downstream consumption

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   batch_id,
# MAGIC   COUNT(*) AS ready_rows
# MAGIC FROM bronze_ready
# MAGIC GROUP BY batch_id
# MAGIC ORDER BY batch_id;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Raw Ingest — full row counts by batch and file

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   batch_id,
# MAGIC   source_file_name,
# MAGIC   COUNT(*) AS row_count,
# MAGIC   MIN(ingest_ts) AS first_ingest,
# MAGIC   SUM(CASE WHEN _rescued_data IS NOT NULL THEN 1 ELSE 0 END) AS rescued_rows
# MAGIC FROM bronze_orders_raw
# MAGIC GROUP BY batch_id, source_file_name
# MAGIC ORDER BY batch_id, source_file_name;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Expected Results
# MAGIC
# MAGIC | Batch | Scenario | Expected Outcome |
# MAGIC |-------|----------|-----------------|
# MAGIC | B-001 | Clean baseline | All 10 rows in bronze_ready |
# MAGIC | B-002 | Schema drift | Rescued/quarantined rows |
# MAGIC | B-001 (replay) | Duplicate replay | Flagged in registry, blocked from ready |
# MAGIC | B-004 | Partial payload | All 5 rows quarantined |
