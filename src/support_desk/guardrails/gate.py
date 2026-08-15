"""The confidence gate: four independent signals, pure Python.

No model is consulted here, on purpose. Asking a model whether its own answer is
good enough gets a yes almost every time, including when it should not. The gate
is the safety mechanism, so it is built from measurable signals and is
exhaustively testable.

Thresholds come from ``settings.gate``. The blocking-flag list lives here rather
than in configuration because it is a set of names the code must recognise, not
a number anyone would tune.
"""

from ..config import get_settings
from ..state import SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)

#: Any one of these sends the case to a person whatever the other signals say.
BLOCKING_FLAGS = frozenset(
    {
        "order_not_found",
        "multi_intent",
        "legal_language",
        "angry_tone",
        "oversized_email",
        "empty_email",
    }
)


def evaluate(state: SupportState) -> SupportState:
    """Combine the four signals into one decision.

    All four must pass to auto-reply. A missing signal counts as a failure,
    which is why each lookup defaults to a value that cannot pass rather than to
    something benign.
    """
    settings = get_settings()
    thresholds = settings.gate

    flags = state.get("flags", [])
    blocking = sorted(set(flags) & BLOCKING_FLAGS)
    class_confidence = state.get("class_confidence", 0.0)
    retrieval_score = state.get("retrieval_score", 0.0)
    citation_count = len(state.get("citations", []))

    log.info(
        "node_start",
        node="gate",
        class_confidence=class_confidence,
        retrieval_score=retrieval_score,
        citation_count=citation_count,
        blocking_flags=blocking,
    )

    reasons: list[str] = []
    if blocking:
        reasons.append(f"blocking flags: {', '.join(blocking)}")
    if class_confidence < thresholds.min_class_confidence:
        reasons.append(
            f"class confidence {class_confidence:.2f} below {thresholds.min_class_confidence:.2f}"
        )
    if retrieval_score < thresholds.min_retrieval_score:
        reasons.append(
            f"retrieval score {retrieval_score:.2f} below {thresholds.min_retrieval_score:.2f}"
        )
    if citation_count < thresholds.min_citations:
        reasons.append(f"{citation_count} citations, needs {thresholds.min_citations}")

    patch: SupportState = (
        {"decision": "human_queue", "gate_reason": "; ".join(reasons)}
        if reasons
        else {"decision": "auto_reply", "gate_reason": "all four signals passed"}
    )

    log.info("node_end", node="gate", decision=patch["decision"], reason=patch["gate_reason"])
    return patch
