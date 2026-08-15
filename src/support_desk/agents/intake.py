"""Cleans the email: strips signatures, quoted chains, disclaimers. No model involved."""

from ..config import get_settings
from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)


def intake(state: SupportState) -> SupportState:
    """Placeholder that passes the raw text through, but does enforce the size cap.

    The size and emptiness checks are here rather than deferred because they
    must happen before anything downstream spends money, and they are the one
    part of intake that needs no cleverness at all.

    Still to come: stripping signatures, quoted reply chains and disclaimers,
    and extracting the order id and sender.
    """
    raw = state.get("raw_email", "")
    limits = get_settings().limits
    log.info("node_start", node="intake", raw_chars=len(raw))

    if not raw.strip():
        log.warning("node_end", node="intake", rejected="empty_email")
        return {"clean_text": "", "flags": ["empty_email"]}

    if len(raw) > limits.max_email_chars:
        log.warning(
            "node_end",
            node="intake",
            rejected="oversized_email",
            raw_chars=len(raw),
            limit=limits.max_email_chars,
        )
        return {"clean_text": "", "flags": ["oversized_email"]}

    patch: SupportState = {"clean_text": raw, "order_id": None, "customer_id": None}

    log.info("node_end", node="intake", clean_chars=len(raw))
    return patch
