"""Nodes and edges wired together. This file contains no business logic of its own.

The two routing functions below read a value another node already decided and
map it to a node name. They make no judgements themselves, which is what keeps
the decisions in the nodes and the shape of the run in one readable place.
"""

from collections.abc import Hashable
from functools import lru_cache
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .agents.classifier import classify
from .agents.composer import compose, escalate, retrieve, send
from .agents.general import handle_general
from .agents.intake import intake
from .agents.refund import handle_refund
from .agents.technical import handle_technical
from .guardrails.gate import evaluate
from .state import SupportState

#: LangGraph parameterises both types on state, context, input and output. We
#: use the same state throughout and carry no context, so this alias keeps the
#: signatures readable.
SupportGraph = CompiledStateGraph[SupportState, Any, SupportState, SupportState]

#: Category to node name. Keeping it as data means an unknown category raises
#: here, at the edge, rather than silently skipping the specialist.
_SPECIALIST_FOR: dict[Hashable, str] = {
    "refund": "refund",
    "technical": "technical",
    "general": "general",
}


def route_by_category(state: SupportState) -> str:
    """Pick the specialist for the category the classifier chose."""
    category = state.get("category")
    if category not in _SPECIALIST_FOR:
        raise ValueError(f"cannot route on category {category!r}")
    return _SPECIALIST_FOR[category]


def route_by_decision(state: SupportState) -> str:
    """Pick the exit for the decision the gate reached."""
    return "send" if state.get("decision") == "auto_reply" else "escalate"


def build_graph() -> SupportGraph:
    """Assemble and compile the graph."""
    builder: StateGraph[SupportState, Any, SupportState, SupportState] = StateGraph(SupportState)

    builder.add_node("intake", intake)
    builder.add_node("classifier", classify)
    builder.add_node("refund", handle_refund)
    builder.add_node("technical", handle_technical)
    builder.add_node("general", handle_general)
    builder.add_node("retrieve", retrieve)
    builder.add_node("compose", compose)
    builder.add_node("gate", evaluate)
    builder.add_node("send", send)
    builder.add_node("escalate", escalate)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "classifier")

    # The one decision that changes the shape of the run.
    builder.add_conditional_edges("classifier", route_by_category, _SPECIALIST_FOR)

    # All three corridors converge again.
    for specialist in ("refund", "technical", "general"):
        builder.add_edge(specialist, "retrieve")

    builder.add_edge("retrieve", "compose")
    builder.add_edge("compose", "gate")

    builder.add_conditional_edges(
        "gate", route_by_decision, {"send": "send", "escalate": "escalate"}
    )

    builder.add_edge("send", END)
    builder.add_edge("escalate", END)

    return builder.compile()


@lru_cache
def get_graph() -> SupportGraph:
    """Return the compiled graph, built once per process."""
    return build_graph()
