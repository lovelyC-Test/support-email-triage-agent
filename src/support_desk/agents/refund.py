"""Refund corridor: order and returns policy. Drafts a reply, never issues a refund."""

from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)


def handle_refund(state: SupportState) -> SupportState:
    """Placeholder returning a fixed finding.

    The real version looks the order up through a tool, checks eligibility
    against the delivery date, and sets ``order_not_found`` rather than
    inventing an order that is not there.
    """
    log.info("node_start", node="refund", order_id=state.get("order_id"))

    patch: SupportState = {"findings": "stub refund agent: eligibility not yet checked"}

    log.info("node_end", node="refund")
    return patch
