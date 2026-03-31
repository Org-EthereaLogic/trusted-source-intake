# Databricks notebook source
# MAGIC %md
# MAGIC # Seed Demo Files
# MAGIC
# MAGIC Copies the four sample batches into the configured landing volume.
# MAGIC **Run this notebook once before your first pipeline refresh.**

# COMMAND ----------

spark.sql("CREATE SCHEMA IF NOT EXISTS ${var.catalog}.${var.schema}")
spark.sql("CREATE VOLUME IF NOT EXISTS ${var.catalog}.${var.schema}.landing")
spark.sql("CREATE VOLUME IF NOT EXISTS ${var.catalog}.${var.schema}.ops")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Copy sample batches into the landing path

# COMMAND ----------

from pathlib import Path

LANDING_PATH = spark.conf.get(
    "pipeline.landing_path",
    "/Volumes/main/trusted_source_intake/landing",
)

REPO_SAMPLE_DIR = Path("data/sample")
if not REPO_SAMPLE_DIR.exists():
    notebook_dir = (
        dbutils.entry_point.getDbutils()
        .notebook()
        .getContext()
        .notebookPath()
        .get()
        .rsplit("/", 2)[0]
    )
    REPO_SAMPLE_DIR = Path(f"/Workspace/{notebook_dir}/data/sample")

batch_dirs = sorted(REPO_SAMPLE_DIR.glob("batch_*"))
print(f"Found {len(batch_dirs)} batch directories to seed.\n")

for batch_dir in batch_dirs:
    for json_file in batch_dir.glob("*.json"):
        dest = f"{LANDING_PATH}/{batch_dir.name}/{json_file.name}"
        dbutils.fs.cp(f"file:{json_file.resolve()}", dest)
        print(f"  {batch_dir.name}/{json_file.name} → {dest}")

print(f"\nSeeding complete. {len(batch_dirs)} batches landed at {LANDING_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify landed files

# COMMAND ----------

display(dbutils.fs.ls(LANDING_PATH))
