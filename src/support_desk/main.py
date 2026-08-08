"""Command line entrypoint: process one email, or a whole folder.

Run it with either of:

    python -m support_desk.main --version
    support-desk --version

Only ``--version`` works today. The two subcommands are declared so the
interface is settled, but both need the graph, which does not exist yet.
"""

import argparse
from pathlib import Path

from . import __version__
from .utils.logging import get_logger


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

    log.error("command_not_implemented", command=args.command, path=str(args.path))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
