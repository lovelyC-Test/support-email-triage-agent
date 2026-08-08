"""Configure logging once. Every module gets its logger from here.

Nothing in the application prints; everything logs, with the trace identifier
attached. A print statement tells you what happened while you were watching. A
structured log tells you what happened in a run nobody was watching.

The convention is one line per node entry and one per node exit, carrying the
decision that node made, which is enough to reconstruct any past run.

Reads ``log_level`` and ``log_format`` from :func:`support_desk.config.get_settings`.
"""

import logging
import sys
from typing import Any

import structlog

from ..config import get_settings

#: Configuration happens exactly once. Calling structlog.configure twice
#: duplicates every line of output.
_configured = False


def configure() -> None:
    """Set up stdlib logging and structlog processors. Safe to call repeatedly."""
    global _configured
    if _configured:
        return

    settings = get_settings()
    level = logging.getLevelNamesMapping().get(settings.log_level.upper(), logging.INFO)

    # structlog renders the whole line, so stdlib must not add a prefix of its own.
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer()
        if settings.log_format == "json"
        else structlog.dev.ConsoleRenderer()
    )

    structlog.configure(
        processors=[
            # Brings in the trace_id bound by bind_run().
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            # The renderer turns the event dict into a string, so it goes last.
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    _configured = True


def get_logger(name: str) -> Any:
    """Return a bound logger for ``name``, configuring logging on first use.

    Modules call ``get_logger(__name__)`` at import time, so a failure here
    makes the package unimportable.
    """
    configure()
    return structlog.get_logger(name)


def bind_run(trace_id: str) -> None:
    """Attach ``trace_id`` to every log line for the rest of this run.

    Called once per run from the entry layer. The clear matters: without it, a
    second email processed in the same process carries the first one's id.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(trace_id=trace_id)
