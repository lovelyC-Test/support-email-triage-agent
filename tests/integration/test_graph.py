"""The whole graph, end to end, offline.

Proves the wiring rather than the intelligence: that the routing edge sends each
category to its own specialist, that all three corridors converge, and that both
exits are reachable. The nodes themselves are still placeholders.

Run just this file:  .venv/bin/pytest tests/integration/test_graph.py -v
"""

from typing import cast

import pytest

from support_desk.graph import build_graph
from support_desk.state import SupportState

pytestmark = pytest.mark.integration


def run(raw_email: str) -> SupportState:
    """Push one email through a freshly built graph and return the final state."""
    initial: SupportState = {"trace_id": "test", "raw_email": raw_email}
    return cast(SupportState, build_graph().invoke(initial))


def test_a_refund_email_takes_the_refund_route() -> None:
    """The routing edge sends a refund email to the refund specialist."""
    final = run("My kettle arrived dented and I would like a refund please.")

    assert final["category"] == "refund"
    assert "refund agent" in final["findings"]


def test_a_technical_email_takes_the_technical_route() -> None:
    """The routing edge sends a fault report to the technical specialist."""
    final = run("My toaster is broken, the lever will not stay down.")

    assert final["category"] == "technical"
    assert "technical agent" in final["findings"]


def test_anything_else_takes_the_general_route() -> None:
    """Email matching neither corridor falls through to general."""
    final = run("How long does delivery take to Inverness, and what does it cost?")

    assert final["category"] == "general"
    assert "general agent" in final["findings"]


def test_a_clean_run_reaches_the_auto_reply_exit() -> None:
    """With every signal passing, the gate sends rather than escalates."""
    final = run("My kettle arrived dented and I would like a refund please.")

    assert final["decision"] == "auto_reply"
    assert final["gate_reason"] == "all four signals passed"
    assert final["draft_reply"]
    assert final["citations"]


def test_an_oversized_email_reaches_the_human_queue_exit() -> None:
    """Rejected at intake, flagged, and escalated by the gate.

    Also proves the flags reducer works: the flag is set by intake and must
    still be present several nodes later when the gate reads it.
    """
    final = run("x" * 20_001)

    assert "oversized_email" in final["flags"]
    assert final["decision"] == "human_queue"
    assert "oversized_email" in final["gate_reason"]
