"""Tests for settings loading and validation.

Run just this file:  .venv/bin/pytest tests/unit/test_config.py -v
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from support_desk.config import PROJECT_ROOT, Settings, get_settings, resolve_path


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    """get_settings is cached, so one test's values must not leak into the next."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def isolated_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Run in an empty directory with no credentials in the environment.

    Secrets are sourced from `.env` relative to the working directory, so
    changing directory is what stops a developer's real `.env` reaching a test.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_relative_paths_resolve_under_the_project_root() -> None:
    """A relative path from settings becomes absolute, anchored at the repo root.

    This is what lets the CLI, the tests and the Streamlit app all find
    data/index regardless of the directory they were started from.
    """
    resolved = resolve_path("data/index")

    assert resolved.is_absolute()
    assert resolved == PROJECT_ROOT / "data" / "index"


def test_absolute_paths_pass_through_unchanged(tmp_path: Path) -> None:
    """An absolute path is already unambiguous and must not be rewritten."""
    absolute = tmp_path / "support-desk-index"

    assert absolute.is_absolute()
    assert resolve_path(absolute) == absolute


def test_loads_gate_thresholds_from_the_yaml_file(tmp_path: Path) -> None:
    """Values in the YAML reach GateConfig."""
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text(
        "gate:\n  min_class_confidence: 0.75\n  min_retrieval_score: 0.5\n  min_citations: 2\n",
        encoding="utf-8",
    )

    settings = get_settings(settings_file)

    assert settings.gate.min_class_confidence == 0.75
    assert settings.gate.min_retrieval_score == 0.5
    assert settings.gate.min_citations == 2


def test_missing_file_falls_back_to_defaults(tmp_path: Path) -> None:
    """A missing settings file is acceptable: every field has a default."""
    settings = get_settings(tmp_path / "does-not-exist.yaml")

    assert settings == Settings()
    assert settings.gate.min_class_confidence == 0.6
    assert settings.limits.max_email_chars == 20_000
    assert settings.log_level == "INFO"


def test_malformed_file_fails_loudly(tmp_path: Path) -> None:
    """A YAML file that is not a mapping must raise, not silently use defaults.

    Silent fallback is the failure mode that leaves you wondering for an hour
    why a new threshold had no effect.
    """
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text("- this is a list\n- not a mapping\n", encoding="utf-8")

    with pytest.raises(TypeError, match="mapping"):
        get_settings(settings_file)


def test_threshold_outside_zero_to_one_is_rejected(tmp_path: Path) -> None:
    """A confidence threshold of 1.5 can never be met, so it must not load.

    Catching it here is what stops it becoming a gate that never escalates.
    """
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text("gate:\n  min_class_confidence: 1.5\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        get_settings(settings_file)


def test_secrets_come_from_the_environment_not_the_yaml(
    monkeypatch: pytest.MonkeyPatch, isolated_env: Path
) -> None:
    """The API key is read from the environment, never from settings.yaml.

    settings.yaml is committed, so a key must never load from it.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-the-environment")
    settings_file = isolated_env / "settings.yaml"
    settings_file.write_text("app:\n  name: support-desk\n", encoding="utf-8")

    assert get_settings(settings_file).secrets.openai_api_key == "sk-from-the-environment"

    # A key placed in the YAML must be ignored entirely.
    get_settings.cache_clear()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    settings_file.write_text("secrets:\n  openai_api_key: sk-from-the-yaml\n", encoding="utf-8")

    assert get_settings(settings_file).secrets.openai_api_key == ""


def test_works_with_no_credentials_present(isolated_env: Path) -> None:
    """Settings load cleanly when no key is set anywhere.

    Every phase before the classifier runs against FakeGateway, so the whole
    system must be importable and testable with an empty environment.
    """
    settings = get_settings(isolated_env / "settings.yaml")

    assert settings.secrets.openai_api_key == ""
    assert settings.secrets.tavily_api_key == ""
    assert settings.model.provider == "openai"
