"""General corridor: policy questions, and the one most likely to say it does not know."""

from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)


def handle_general(state: SupportState) -> SupportState:
    """Placeholder returning a fixed finding.

    The real version answers policy questions and defaults to marking the
    request unanswerable rather than guessing.
    """
    log.info("node_start", node="general", question_chars=len(state.get("clean_text", "")))

    patch: SupportState = {"findings": "stub general agent: question type not yet decided"}

    log.info("node_end", node="general")
    return patch
