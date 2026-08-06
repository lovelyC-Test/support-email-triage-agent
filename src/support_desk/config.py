"""Loads configuration once, validates it, and exposes a single settings object.

Nothing else in the application reads ``os.environ`` or opens ``settings.yaml``.
If you find yourself wanting to, add a field here instead. That is rule 6 of the
seven rules in Part 1 section 1.4.

Two files, one job between them: the YAML holds anything a person might want to
tune, and this module loads it, merges in the secrets from the environment,
validates the result, and hands back one object.

Structure follows Part 1 section 1.6, with an extra ``gate`` section that is
specific to Project 1.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Your implementation of get_settings() will also need:  import yaml

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
    """The guardrail numbers. Every cap in the system reads its limit from here.

    Section 1.9 requires an attempt cap, a spend ceiling and input validation.
    All three read their thresholds from this object.
    """

    max_tool_calls_per_run: int = Field(default=25, ge=1)
    max_spend_gbp_per_run: float = Field(default=0.40, gt=0)
    # Project 1: an oversized email must be rejected before any model call.
    max_email_chars: int = Field(default=20_000, ge=1)


class MemoryConfig(BaseModel):
    """Where retrieval and persistent storage live."""

    vector_store_path: str = "data/index"
    collection_name: str = "help_articles"
    embedding_model: str = "text-embedding-3-small"
    top_k: int = Field(default=5, ge=1)
    # Project 1: SQLite holds orders, tickets and the audit trail.
    database_path: str = "data/support.db"


class GateConfig(BaseModel):
    """Thresholds for the confidence gate. Specific to Project 1.

    These are the numbers the marking rubric expects to see justified, so they
    live together and are documented rather than scattered through the code.
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
    raise NotImplementedError


@lru_cache
def get_settings(settings_path: Path | None = None) -> Settings:
    """Load the YAML, merge in secrets, validate, and return the settings object.

    Cached so it is built once and reused everywhere, which is rule 6: config is
    loaded once at start-up and passed down.

    What this must do:

    1. Default to ``PROJECT_ROOT / 'config' / 'settings.yaml'`` when no path is
       given.
    2. Read it with ``yaml.safe_load``, never ``yaml.load``.
    3. Treat a missing file as acceptable and return ``Settings()`` — every field
       has a default, so the system runs out of the box.
    4. Treat a malformed file as an error and fail loudly. Silently falling back
       to defaults is what leaves someone wondering for an hour why their new
       threshold had no effect.
    5. Build each section from its slice of the YAML, letting pydantic validate.
       Note the YAML nests the level under ``logging:``, so ``log_level`` has to
       be pulled out of that sub-mapping rather than read from the top level.
    6. Construct ``Secrets()`` with no arguments — pydantic-settings reads
       ``.env`` by itself.

    Because this is cached, tests that need different values should build
    ``Settings(...)`` directly, or call ``get_settings.cache_clear()`` first.
    """
    raise NotImplementedError
