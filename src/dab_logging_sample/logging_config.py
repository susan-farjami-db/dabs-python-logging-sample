"""Shared logging setup used by both the wheel entry point and the notebook task.

Centralizing this means notebooks and wheels emit identical log records, so the
driver logs and any downstream log shipping (cluster log delivery to S3/ADLS,
external SIEM, etc.) see a consistent format.
"""

from __future__ import annotations

import logging
import sys
from typing import Iterable

_DEFAULT_FORMAT = "%(asctime)s %(levelname)-8s %(name)s :: %(message)s"
_DEFAULT_DATEFMT = "%Y-%m-%dT%H:%M:%S%z"

# Libraries that are noisy at DEBUG/INFO. Pin them to WARNING so app code stays
# the signal, not the dependencies.
_NOISY_LIBRARIES: tuple[str, ...] = (
    "py4j",
    "py4j.java_gateway",
    "urllib3",
    "botocore",
    "boto3",
    "azure",
    "requests",
)


def configure_logging(
    level: str = "INFO",
    *,
    extra_quiet: Iterable[str] = (),
) -> logging.Logger:
    """Configure root logging and return the package logger.

    Calling this from a notebook or a wheel entry point produces identical
    output. Safe to call multiple times — re-runs in the same cluster session
    (common in notebooks) will reset handlers cleanly.
    """
    normalized = level.upper().strip()
    if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError(
            f"Invalid log level {level!r}; expected one of "
            "DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )

    root = logging.getLogger()
    # Notebook clusters reuse the Python kernel across runs, so handlers stack
    # up unless we clear them.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT, datefmt=_DEFAULT_DATEFMT))
    root.addHandler(handler)
    root.setLevel(normalized)

    for noisy in (*_NOISY_LIBRARIES, *extra_quiet):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logging.getLogger("dab_logging_sample")
