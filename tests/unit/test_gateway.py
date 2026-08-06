"""Tests for the model gateway.

The handbook's phase 2 acceptance test is here: *a test replaces the gateway with
the fake and passes offline*. Nothing in this file may touch the network or read
an API key.
"""

import pytest


@pytest.mark.skip(reason="TODO: implement FakeGateway")
def test_fake_gateway_returns_its_canned_classification() -> None:
    """A registered response for Classification comes back unchanged.

    Build a FakeGateway with a Classification response, call structured() asking
    for Classification, and assert you get that object back. This is the whole
    basis of testing the graph without a model.
    """


@pytest.mark.skip(reason="TODO: implement FakeGateway")
def test_fake_gateway_records_the_prompt_it_was_given() -> None:
    """The prompt is recorded so tests can assert what was actually sent.

    This matters more than it looks: it is how you prove the classifier received
    the *cleaned* text rather than the raw email with its signature and quoted
    reply chain still attached.
    """


@pytest.mark.skip(reason="TODO: implement FakeGateway")
def test_fake_gateway_raises_for_an_unregistered_schema() -> None:
    """Asking for a schema with no canned response must fail clearly.

    A fake that silently returns a default would let a test pass while proving
    nothing, which is worse than no test at all.
    """


@pytest.mark.skip(reason="TODO: implement FakeGateway")
def test_fake_gateway_needs_no_api_key() -> None:
    """Constructing and using the fake works with no credentials in the environment.

    Delete any key from the environment with monkeypatch, then run a full
    structured() call. If this passes, every later phase can be developed offline
    and for free.
    """
