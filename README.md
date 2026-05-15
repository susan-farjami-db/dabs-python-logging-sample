# DAB Python Logging Sample

A minimal [Databricks Asset Bundle](https://docs.databricks.com/aws/en/dev-tools/bundles/index.html)
demonstrating a clean, runtime-configurable pattern for Python logging in
production jobs.

The goal is to make the log level a knob you can turn **without redeploying**:
default per environment, override per run from the Jobs UI, no code changes.

## The pattern in one screen

```
┌─────────────────────────────────────────────────────────────┐
│  databricks.yml  ──  bundle variable `log_level`            │
│      │                                                      │
│      │  per-target default (dev=DEBUG, prod=WARNING)        │
│      │  passed as job parameter:  --log-level ${var...}     │
│      ▼                                                      │
│  Python entry point  ──  argparse reads --log-level         │
│      │                                                      │
│      ▼                                                      │
│  configure_logging(level)  ──  shared helper                │
│      • sets root logger level                               │
│      • silences noisy libs (py4j, urllib3, boto…)           │
│      • single formatter for driver logs + log shipping      │
└─────────────────────────────────────────────────────────────┘
```

Per-run override: in the Jobs UI, click **Run now with different parameters**
and change `--log-level` to `DEBUG`. No redeploy.

Per-deploy override: `databricks bundle deploy --var="log_level=DEBUG"`.

## Layout

```
.
├── databricks.yml              # bundle definition; both job types live here
├── pyproject.toml              # wheel build config
├── src/dab_logging_sample/
│   ├── __init__.py
│   ├── logging_config.py       # the reusable bit — copy this into your repo
│   └── main.py                 # python_wheel_task entry point
└── notebooks/
    └── example_notebook.py     # notebook_task variant using the same helper
```

The piece you'd actually copy into a real project is
[`src/dab_logging_sample/logging_config.py`](src/dab_logging_sample/logging_config.py).
Everything else is scaffolding to show it running end-to-end.

## Why both a wheel and a notebook task?

Same helper, two entry points:

| Task type   | How log level is read         | Best for                                  |
|-------------|-------------------------------|-------------------------------------------|
| Python wheel | `argparse` on `--log-level`   | Production code, reusable libraries, CI   |
| Notebook    | `dbutils.widgets.get("log_level")` | Exploration, ad-hoc jobs, mixed teams |

Mix both in the same bundle if your team has both styles. The
`configure_logging()` helper is the shared contract — same format, same noisy-lib
suppression, same handler reset behavior across kernel reuses.

## Deploy & run

### Prereqs

```bash
# Python build backend (DAB invokes `python -m build --wheel` to package the wheel)
pip install build
```

Edit `databricks.yml` and replace `<your-workspace>` in the `targets.dev.workspace.host`
(and `targets.prod` if you use it) with your actual workspace URL,
e.g. `https://adb-1234567890.azuredatabricks.net` or `https://your-workspace.cloud.databricks.com`.

### Install the Databricks CLI

Skip if you already have it:

```bash
# macOS
brew tap databricks/tap && brew install databricks

# Linux / macOS (no Homebrew)
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Windows (PowerShell, winget)
winget install Databricks.DatabricksCLI
```

For other Windows installers (Chocolatey, manual zip) see the
[official install docs](https://docs.databricks.com/aws/en/dev-tools/cli/install.html).

```bash
# Configure auth (one-time, OAuth)
databricks auth login --host https://<your-workspace>.cloud.databricks.com

# Build the wheel + upload bundle artifacts
databricks bundle deploy --target dev

# Run the wheel job
databricks bundle run wheel_job --target dev

# Run the notebook job
databricks bundle run notebook_job --target dev

# Override log level for a one-off run (without redeploying).
# For the wheel job, pass named params straight to the task:
databricks bundle run wheel_job --target dev --python-named-params log-level=DEBUG,run-name=adhoc

# For the notebook job, override the widget value:
databricks bundle run notebook_job --target dev --params log_level=DEBUG
```

## Local test (no Databricks needed)

```bash
python -m pip install -e .
python -m dab_logging_sample.main --log-level DEBUG --run-name local
```

You should see output like:

```
2026-05-15T13:30:00-0700 INFO     dab_logging_sample :: logger configured at level=DEBUG for run=local
2026-05-15T13:30:00-0700 DEBUG    dab_logging_sample.main :: debug-level diagnostic for run=local
2026-05-15T13:30:00-0700 INFO     dab_logging_sample.main :: starting work for run=local
...
```

## Customizing

- **Different format / JSON logs?** Edit `_DEFAULT_FORMAT` in
  `logging_config.py`, or swap `logging.Formatter` for a structured-logging
  formatter (`python-json-logger`, `structlog`, etc.).
- **Different noisy libraries?** Add to `_NOISY_LIBRARIES` or pass `extra_quiet`
  to `configure_logging()`.
- **Ship logs off-cluster?** Configure
  [cluster log delivery](https://docs.databricks.com/aws/en/compute/configure.html#cluster-log-delivery)
  to S3/ADLS in the `new_cluster` block of `databricks.yml`. The format above is
  designed to be greppable as plain text and machine-parseable as space-delimited
  records.

## References

- [Databricks Asset Bundles overview](https://docs.databricks.com/aws/en/dev-tools/bundles/index.html)
- [Bundle variables](https://docs.databricks.com/aws/en/dev-tools/bundles/variables.html)
- [Python `logging` HOWTO](https://docs.python.org/3/howto/logging.html)
