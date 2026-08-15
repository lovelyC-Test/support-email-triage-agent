"""Command line entrypoint: process one email, or a whole folder.

Run it with either of:

    python -m support_desk.main --version
    support-desk --version

This is the entry layer: it turns typed words into arguments, gives each run a
trace id, hands off to the graph, and turns the result back into an exit code.
Nothing below this file knows a command line exists.
"""

import argparse
from pathlib import Path
from typing import cast
from uuid import uuid4

from . import __version__
from .graph import get_graph
from .state import SupportState
from .utils.logging import bind_run, get_logger


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser.

    Kept separate from :func:`main` so a test can inspect the parser without
    running the program.
    """
    parser = argparse.ArgumentParser(
        prog="support-desk",
        description="Triage a support email: classify, route, ground, gate, escalate.",
    )
    # action="version" makes argparse handle the printing and the exit itself.
    parser.add_argument("--version", action="version", version=__version__)

    subcommands = parser.add_subparsers(dest="command", metavar="COMMAND")

    process = subcommands.add_parser("process", help="Process a single email file")
    process.add_argument("path", type=Path, help="Path to the email file")

    process_folder = subcommands.add_parser(
        "process-folder", help="Process every email in a folder"
    )
    process_folder.add_argument("path", type=Path, help="Folder containing email files")

    return parser


def process_email(path: Path) -> SupportState:
    """Run one email through the graph and return the final state.

    Each email gets its own trace id, bound before the graph starts so every
    line logged anywhere downstream carries it.
    """
    trace_id = uuid4().hex[:12]
    bind_run(trace_id)

    log = get_logger(__name__)
    log.info("run_start", source=str(path))

    initial: SupportState = {"trace_id": trace_id, "raw_email": path.read_text(encoding="utf-8")}
    # invoke() is typed loosely; the graph is parameterised on SupportState.
    final = cast(SupportState, get_graph().invoke(initial))

    log.info("run_end", decision=final.get("decision"), category=final.get("category"))
    return final


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, dispatch, and return a process exit code.

    Returns an int rather than calling ``sys.exit`` so a test can assert on the
    return value instead of catching ``SystemExit``.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Logging is configured once, here, before any other code runs.
    log = get_logger(__name__)

    if args.command is None:
        parser.print_help()
        return 1

    path: Path = args.path
    if not path.exists():
        log.error("path_not_found", path=str(path))
        return 2

    if args.command == "process":
        process_email(path)
        return 0

    emails = sorted(path.glob("*.txt"))
    if not emails:
        log.error("no_emails_found", folder=str(path))
        return 2

    for email in emails:
        process_email(email)

    log.info("folder_complete", folder=str(path), processed=len(emails))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
