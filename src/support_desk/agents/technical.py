"""Technical corridor: maps a described symptom to a known fix."""

from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)


def handle_technical(state: SupportState) -> SupportState:
    """Placeholder returning a fixed finding.

    The real version matches the reported symptom against known fixes and states
    explicitly when nothing matches, rather than offering a plausible guess.
    """
    log.info("node_start", node="technical", symptom_chars=len(state.get("clean_text", "")))

    patch: SupportState = {"findings": "stub technical agent: symptom not yet matched"}

    log.info("node_end", node="technical")
    return patch
