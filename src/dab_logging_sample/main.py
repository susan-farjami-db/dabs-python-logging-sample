"""Entry point for the python_wheel_task in databricks.yml.

Run locally:
    python -m dab_logging_sample.main --log-level DEBUG --run-name local

On Databricks it is invoked by the Jobs runtime with parameters supplied from
the bundle (and optionally overridden in the Jobs UI per run).
"""

from __future__ import annotations

import argparse

from .logging_config import configure_logging


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample DAB wheel task")
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="DEBUG, INFO, WARNING, ERROR, or CRITICAL",
    )
    parser.add_argument(
        "--run-name",
        default="unnamed",
        help="Free-form label included in log lines for traceability",
    )
    # parse_known_args so unexpected Databricks-injected params don't blow up.
    args, _ = parser.parse_known_args(argv)
    return args


def do_work(run_name: str) -> None:
    import logging

    log = logging.getLogger(__name__)

    log.debug("debug-level diagnostic for run=%s", run_name)
    log.info("starting work for run=%s", run_name)

    for i in range(3):
        log.debug("step %d in progress", i)
    log.info("processed %d steps", 3)

    log.warning("example warning: this would be raised if X happened")
    log.info("run=%s finished", run_name)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    log = configure_logging(args.log_level)
    log.info("logger configured at level=%s for run=%s", args.log_level, args.run_name)
    do_work(args.run_name)


if __name__ == "__main__":
    main()
