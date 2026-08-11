"""Tests for the model gateway.

The phase 2 acceptance test is here: a test replaces the gateway with the fake
and passes offline. Nothing in this file may touch the network or read an API key.
"""

import pytest

from support_desk.models.gateway import FakeGateway
from support_desk.models.schemas import Classification, Draft


def test_fake_gateway_returns_its_canned_classification() -> None:
    """A registered response for Classification comes back unchanged.

    This is the whole basis of testing the graph without a model.
    """
    expected = Classification(
        category="refund",
        confidence=0.94,
        reason="explicit refund request tied to an order id",
    )
    gateway = FakeGateway({Classification: expected})

    assert gateway.structured("any prompt", Classification) is expected


def test_fake_gateway_records_the_prompt_it_was_given() -> None:
    """The prompt is recorded so tests can assert what was actually sent.

    This is how you prove the classifier received the *cleaned* text rather than
    the raw email with its signature and quoted reply chain still attached.
    """
    gateway = FakeGateway(
        {Classification: Classification(category="general", confidence=0.5, reason="unclear")},
        text_response="a drafted reply",
    )

    gateway.structured("cleaned email text", Classification)
    gateway.text("compose from these sources", role="writer")

    assert gateway.prompts == ["cleaned email text", "compose from these sources"]
    assert gateway.roles == ["planner", "writer"]


def test_fake_gateway_raises_for_an_unregistered_schema() -> None:
    """Asking for a schema with no canned response must fail clearly.

    A fake that silently returns a default would let a test pass while proving
    nothing, which is worse than no test at all.
    """
    gateway = FakeGateway(
        {Classification: Classification(category="refund", confidence=0.9, reason="refund")}
    )

    with pytest.raises(KeyError, match="Draft"):
        gateway.structured("a prompt", Draft)


def test_fake_gateway_needs_no_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Constructing and using the fake works with no credentials present.

    If this passes, every later phase can be developed offline and for free.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    draft = Draft(body="You are eligible.", citations=["returns_policy.md"], answered=True)
    gateway = FakeGateway({Draft: draft}, text_response="plain prose")

    assert gateway.structured("ground this", Draft) == draft
    assert gateway.text("write this") == "plain prose"
