"""Tests for settings loading and validation.

Each test is skipped until you implement the thing it covers. Remove the skip as
you go — the file doubles as your checklist.

Run just this file:  .venv/bin/pytest tests/unit/test_config.py -v
"""

import pytest


@pytest.mark.skip(reason="TODO: implement resolve_path")
def test_relative_paths_resolve_under_the_project_root() -> None:
    """A relative path from settings becomes absolute, anchored at the repo root.

    This is what lets the CLI, the tests and the Streamlit app all find
    data/index regardless of the directory they were started from.
    """


@pytest.mark.skip(reason="TODO: implement resolve_path")
def test_absolute_paths_pass_through_unchanged() -> None:
    """An absolute path is already unambiguous and must not be rewritten."""


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_loads_gate_thresholds_from_the_yaml_file() -> None:
    """Values in the YAML reach GateConfig.

    Write a small settings file to tmp_path, load it, and assert the three gate
    thresholds match. Do not assert against the real config/settings.yaml, or
    this test breaks every time you tune a threshold.
    """


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_missing_file_falls_back_to_defaults() -> None:
    """A missing settings file is acceptable: every field has a default.

    Point get_settings at a path that does not exist and assert you get the
    documented defaults rather than an exception.
    """


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_malformed_file_fails_loudly() -> None:
    """A YAML file that is not a mapping must raise, not silently use defaults.

    Silent fallback is the failure mode that leaves you wondering for an hour
    why a new threshold had no effect.
    """


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_threshold_outside_zero_to_one_is_rejected() -> None:
    """A confidence threshold of 1.5 can never be met, so it must not load.

    Catching it here is what stops it becoming a gate that never escalates.
    """


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_secrets_come_from_the_environment_not_the_yaml() -> None:
    """The API key is read from the environment, never from settings.yaml.

    Set OPENAI_API_KEY with monkeypatch and assert it arrives on
    settings.secrets. Then assert that putting a key in the YAML does *not*
    populate it — settings.yaml is committed, so a key must never load from it.
    """


@pytest.mark.skip(reason="TODO: implement get_settings")
def test_works_with_no_credentials_present() -> None:
    """Settings load cleanly when no key is set anywhere.

    Every phase before the classifier runs against FakeGateway, so the whole
    system must be importable and testable with an empty environment.
    """
