"""Retrieval plus grounded drafting with citations, and the send and escalate exits."""

from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)


def retrieve(state: SupportState) -> SupportState:
    """Placeholder returning one invented chunk with a passing score.

    The real version embeds the question and searches the vector store, so the
    score reflects whether anything relevant was actually found. Until then this
    score is fiction and the gate's retrieval signal cannot fail.
    """
    log.info("node_start", node="retrieve", query_chars=len(state.get("clean_text", "")))

    patch: SupportState = {
        "retrieved_chunks": [{"doc": "returns-policy.md", "score": 0.80}],
        "retrieval_score": 0.80,
    }

    log.info("node_end", node="retrieve", chunks=1, retrieval_score=0.80)
    return patch


def compose(state: SupportState) -> SupportState:
    """Placeholder returning a fixed draft with one citation.

    The real version writes prose grounded in the retrieved passages and cites
    each claim, or states plainly that it cannot answer.
    """
    log.info("node_start", node="compose", category=state.get("category"))

    patch: SupportState = {
        "draft_reply": "stub composer: a grounded reply will be written here.",
        "citations": ["returns-policy.md"],
    }

    log.info("node_end", node="compose", citations=1)
    return patch


def send(state: SupportState) -> SupportState:
    """Exit taken when the gate passes. Sends the reply and records the run."""
    log.info(
        "exit",
        node="send",
        decision=state.get("decision"),
        category=state.get("category"),
    )
    return {}


def escalate(state: SupportState) -> SupportState:
    """Exit taken when the gate fails. Hands a prepared case to a person.

    The packet is what makes this worth more than forwarding the raw email: the
    draft, the sources behind it, the classification, and why it was held back.
    """
    log.info(
        "exit",
        node="escalate",
        decision=state.get("decision"),
        category=state.get("category"),
        gate_reason=state.get("gate_reason"),
        flags=state.get("flags", []),
        citations=len(state.get("citations", [])),
    )
    return {}
