"""Returns a validated Classification: category, confidence, reason."""

from ..state import Category, SupportState
from ..utils.logging import get_logger

log = get_logger(__name__)

#: Crude keyword sets, present only so the stub sends the sample emails down all
#: three routes and the wiring can be watched working. Replaced wholesale by a
#: prompted model call returning a validated Classification.
_REFUND_WORDS = ("refund", "return", "money back", "cancel", "send it back")
_TECHNICAL_WORDS = ("not working", "will not", "won't", "broken", "leak", "stuck", "jam")


def classify(state: SupportState) -> SupportState:
    """Placeholder that guesses a category from keywords.

    Deliberately crude, and the confidence it reports is a constant rather than
    a measurement. Its only job is to make the routing edge take all three
    branches so the graph can be exercised end to end.
    """
    log.info("node_start", node="classifier")

    text = state.get("clean_text", "").lower()
    category: Category = "general"
    if any(word in text for word in _REFUND_WORDS):
        category = "refund"
    elif any(word in text for word in _TECHNICAL_WORDS):
        category = "technical"

    patch: SupportState = {
        "category": category,
        "class_confidence": 0.75,
        "class_reason": "stub classifier: keyword match",
    }

    log.info("node_end", node="classifier", category=category, confidence=0.75)
    return patch
