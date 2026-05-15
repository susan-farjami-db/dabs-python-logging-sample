# Databricks notebook source
# MAGIC %md
# MAGIC # DAB logging sample — notebook task
# MAGIC
# MAGIC Demonstrates the same logging pattern as the wheel task, but driven by
# MAGIC notebook widgets so the log level is configurable per-run from the Jobs UI
# MAGIC (and from the notebook itself during interactive development).

# COMMAND ----------

dbutils.widgets.dropdown(
    "log_level",
    "INFO",
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    "Log level",
)
dbutils.widgets.text("run_name", "unnamed", "Run name")

log_level = dbutils.widgets.get("log_level")
run_name = dbutils.widgets.get("run_name")

# COMMAND ----------

# MAGIC %md
# MAGIC Use the same `configure_logging` helper as the wheel so notebooks and
# MAGIC wheels emit identical log records.

# COMMAND ----------

from dab_logging_sample.logging_config import configure_logging

log = configure_logging(log_level)
log.info("logger configured at level=%s for run=%s", log_level, run_name)

# COMMAND ----------

import logging

log = logging.getLogger(__name__)

log.debug("debug-level diagnostic for run=%s", run_name)
log.info("starting work for run=%s", run_name)

for i in range(3):
    log.debug("step %d in progress", i)
log.info("processed %d steps", 3)

log.warning("example warning: this would be raised if X happened")
log.info("run=%s finished", run_name)
