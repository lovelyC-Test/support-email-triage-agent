"""Command line entrypoint: process one email, or a whole folder.

Run it with either of:

    python -m support_desk.main --version
    support-desk --version

Today only ``--version`` needs to work. That is the handbook's phase 1 acceptance
test, and it proves the package installs and imports cleanly.
"""

import argparse

# Unused until you implement build_parser(); keep the import.
from . import __version__  # noqa: F401


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser.

    Kept separate from :func:`main` so a test can inspect the parser without
    running the program.

    What this must do:

    1. Create a parser with a short description.
    2. Add ``--version``, printing the package version. The simplest route is
       ``action="version"`` with ``version=__version__``, which makes argparse
       handle printing and exiting for you.
    3. Add a subcommand for processing a single email from a file path.
    4. Add a subcommand for processing every email in a folder.

    Leave the subcommands defined but unimplemented for now; they need the graph,
    which does not exist yet.
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, dispatch, and return a process exit code.

    Returning an int rather than calling ``sys.exit`` keeps this testable: a test
    can assert on the return value instead of catching ``SystemExit``.

    What this must do:

    1. Build the parser and parse ``argv`` (None means read ``sys.argv``).
    2. Configure logging once, here, before anything else runs.
    3. Dispatch to the chosen subcommand.
    4. Return 0 on success and non-zero on failure.
    """
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
