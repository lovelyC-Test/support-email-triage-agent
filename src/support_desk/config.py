"""Loads configuration once, validates it, and exposes a single settings object.

Nothing else in the application reads ``os.environ`` or opens ``settings.yaml``.
When a module needs a new tunable value, add a field here and pass the settings
object down.

``settings.yaml`` is committed and holds anything a person might want to tune.
``.env`` is not committed and holds the secrets. This module merges the two,
validates the result, and hands back one object.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

#: Repository root, resolved from this file's location so the CLI, the tests and
#: the Streamlit app all agree regardless of the directory they were started in.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class AppConfig(BaseModel):
    """Identity and environment."""

    name: str = "support-desk"
    environment: str = "development"  # development | production


class ModelConfig(BaseModel):
    """Everything about which model we call and how.

    Two roles, not one model name. Routing is a cheap structured decision that
    wants repeatability, so it runs at temperature 0. Only the writer produces
    prose, and it gets some warmth.
    """

    provider: str = "openai"
    planner_model: str = "gpt-4o-mini"
    writer_model: str = "gpt-4o"
    planner_temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    writer_temperature: float = Field(default=0.6, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=1200, ge=1)
    request_timeout_seconds: int = Field(default=45, ge=1)


class LimitsConfig(BaseModel):
    """Ceilings that stop one run consuming unbounded time or money.

    Read by ``guardrails.limits`` and ``guardrails.validators``.
    """

    max_tool_calls_per_run: int = Field(default=25, ge=1)
    max_spend_gbp_per_run: float = Field(default=0.40, gt=0)
    # Checked at intake, so an oversized email costs nothing.
    max_email_chars: int = Field(default=20_000, ge=1)


class MemoryConfig(BaseModel):
    """Where retrieval and persistent storage live.

    Both paths are relative to the repository root; pass them through
    :func:`resolve_path` before use.
    """

    vector_store_path: str = "data/index"
    collection_name: str = "help_articles"
    embedding_model: str = "text-embedding-3-small"
    top_k: int = Field(default=5, ge=1)
    # SQLite: orders, tickets and the audit trail.
    database_path: str = "data/support.db"


class GateConfig(BaseModel):
    """Thresholds for the confidence gate, read by ``guardrails.gate``.

    Three of the gate's four signals compare against a number here. The fourth
    is the blocking-flag list, which lives in code.
    """

    min_class_confidence: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Below this, the classifier was not sure enough to trust the route.",
    )
    min_retrieval_score: float = Field(
        default=0.35,
        ge=0.0,
        le=1.0,
        description="Below this, retrieval found nothing relevant enough to answer from.",
    )
    min_citations: int = Field(
        default=1,
        ge=0,
        description="A draft citing fewer sources than this is not grounded.",
    )


class Secrets(BaseSettings):
    """Read from the .env file or the real environment. Never from YAML.

    Defaults are empty strings rather than required values, so the whole system
    can be imported and unit-tested with no credentials present at all.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    tavily_api_key: str = ""


class Settings(BaseModel):
    """The one object the rest of the application is given."""

    app: AppConfig = Field(default_factory=AppConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    limits: LimitsConfig = Field(default_factory=LimitsConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    gate: GateConfig = Field(default_factory=GateConfig)
    log_level: str = "INFO"
    log_format: str = "console"  # console while developing, json in production
    secrets: Secrets = Field(default_factory=Secrets)


def resolve_path(value: str | Path) -> Path:
    """Return ``value`` as an absolute path anchored at the repository root.

    Every path in settings is stored relative to the repo, so this is what lets
    the CLI, the tests and the Streamlit app all find ``data/index`` regardless
    of the directory they were started from.

    Absolute paths should pass through unchanged; relative ones get joined onto
    :data:`PROJECT_ROOT`.
    """
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


@lru_cache
def get_settings(settings_path: Path | None = None) -> Settings:
    """Load the YAML, merge in secrets, validate, and return the settings object.

    Cached, so the file is read once per process. A missing file yields all
    defaults. A file that exists but is not a mapping raises, because silently
    falling back to defaults hides a typo'd config for hours.

    Tests that need different values should build :class:`Settings` directly, or
    call ``get_settings.cache_clear()`` first.

    Raises:
        TypeError: the file exists but does not contain a mapping.
        pydantic.ValidationError: a value is present but out of range.
    """
    path = settings_path or PROJECT_ROOT / "config" / "settings.yaml"

    raw: dict[str, Any] = {}
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle)
        # An empty file is equivalent to no file.
        if loaded is not None:
            if not isinstance(loaded, dict):
                raise TypeError(f"{path} must contain a YAML mapping, got {type(loaded).__name__}")
            raw = loaded

    def section(name: str) -> dict[str, Any]:
        value = raw.get(name) or {}
        if not isinstance(value, dict):
            raise TypeError(f"{path}: '{name}' must be a mapping, got {type(value).__name__}")
        return value

    # The YAML nests these under `logging:`; Settings keeps them flat.
    logging_section = section("logging")

    return Settings(
        app=AppConfig(**section("app")),
        model=ModelConfig(**section("model")),
        limits=LimitsConfig(**section("limits")),
        memory=MemoryConfig(**section("memory")),
        gate=GateConfig(**section("gate")),
        log_level=logging_section.get("level", "INFO"),
        log_format=logging_section.get("format", "console"),
        # Sourced from .env and the environment, never from the YAML.
        secrets=Secrets(),
    )
