"""The typed object that flows through the graph. Defined once, here.

Every field carries a comment saying who writes it and who reads it, because in
six months that comment is the documentation.

``total=False`` because nodes fill this in progressively: at entry only
``trace_id`` and ``raw_email`` exist, and each node returns a *patch* rather
than a whole state.
"""

import operator
from typing import Annotated, Literal, TypedDict

Category = Literal["refund", "technical", "general"]
Decision = Literal["auto_reply", "human_queue"]


class SupportState(TypedDict, total=False):
    """State passed between graph nodes. Nodes return patches, never mutate."""

    # ---- set by the entry layer -------------------------------------
    trace_id: str  # written: entry.  read: everything that logs
    raw_email: str  # written: entry.  read: intake

    # ---- set by the intake node -------------------------------------
    clean_text: str  # written: intake. read: classifier, all agents
    order_id: str | None  # written: intake. read: refund agent
    customer_id: str | None  # written: intake. read: memory lookup, audit

    # ---- set by the classifier --------------------------------------
    category: Category  # written: classifier. read: the routing edge
    class_confidence: float  # written: classifier. read: confidence gate
    class_reason: str  # written: classifier. read: humans, in review

    # ---- set by whichever specialist agent ran ----------------------
    findings: str  # written: specialist. read: composer

    # Several nodes add flags, so this one merges rather than replaces. Without
    # the reducer the last writer wins and an earlier flag is silently dropped
    # before the gate ever sees it. A node returning {"flags": [...]} appends.
    flags: Annotated[list[str], operator.add]  # written: any node. read: gate

    # ---- set by retrieval and the composer --------------------------
    retrieved_chunks: list[dict[str, object]]  # written: retriever. read: composer, gate
    retrieval_score: float  # written: retriever. read: gate
    draft_reply: str  # written: composer. read: gate, both exits
    citations: list[str]  # written: composer. read: gate, both exits

    # ---- set by the gate --------------------------------------------
    decision: Decision  # written: gate. read: the final routing edge
    gate_reason: str  # written: gate. read: the human who picks this up

    # ---- bookkeeping --------------------------------------------------
    tool_calls: int  # incremented by every tool. read: the spend guard
    cost_gbp: float  # accumulated by the gateway. read: the spend guard
