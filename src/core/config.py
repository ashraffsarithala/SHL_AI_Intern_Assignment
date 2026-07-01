"""
Centralised application settings for the SHL Assessment Recommendation Agent.

This module reads environment variables (optionally from a ``.env`` file at the
project root) and exposes them as a single, validated, **immutable** object.

Design Decisions
----------------
1. **pydantic-settings ``BaseSettings``** – Provides automatic type coercion,
   validation, and ``.env`` loading out of the box.  This is the recommended
   Pydantic v2 approach for environment-driven configuration.

2. **``frozen = True``** – After the settings object is created during startup,
   no attribute can be changed.  This satisfies the "immutable settings after
   startup" requirement and prevents accidental mutation in a stateless FastAPI
   service.

3. **``@lru_cache`` on ``get_settings()``** – Ensures the ``.env`` file and
   environment are read exactly once per process.  Every module that calls
   ``get_settings()`` receives the same cached instance.

4. **Sensible defaults** – Every field has a default so the application can
   start in development mode with *zero* environment variables configured.
   Secrets (``LLM_API_KEY``) default to ``None`` and are validated lazily when
   they are actually needed (in the LLM client), not at import time, so that
   catalog-only workflows (e.g., offline index building) do not require an
   API key.

5. **No hardcoded secrets** – API keys and connection strings are always read
   from the environment.

Usage
-----
::

    from src.core.config import get_settings

    settings = get_settings()
    print(settings.LOG_LEVEL)       # "INFO"
    print(settings.RETRIEVAL_TOP_K) # 10
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated, immutable application settings.

    Fields are grouped by subsystem.  Every field has a type annotation, a
    default, and a description so that ``Settings.model_json_schema()`` can
    serve as self-documenting configuration reference.
    """

    # ------------------------------------------------------------------
    #   LLM provider
    # ------------------------------------------------------------------
    LLM_PROVIDER: str = Field(
        default="openai",
        description="Identifier for the LLM vendor (e.g. openai, anthropic, gemini).",
    )
    LLM_API_KEY: Optional[str] = Field(
        default=None,
        description=(
            "API key for the selected LLM provider. "
            "Must be supplied via the environment; never hardcoded."
        ),
    )
    LLM_MODEL_NAME: str = Field(
        default="gpt-4o-mini",
        description="Specific model name to use for LLM calls.",
    )
    LLM_TEMPERATURE: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for LLM generation.",
    )
    LLM_MAX_TOKENS: PositiveInt = Field(
        default=1024,
        description="Maximum number of tokens the LLM may generate per call.",
    )

    # ------------------------------------------------------------------
    #   Embedding model
    # ------------------------------------------------------------------
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="Name of the embedding model used for dense vector search.",
    )

    # ------------------------------------------------------------------
    #   Vector database
    # ------------------------------------------------------------------
    VECTOR_DB: str = Field(
        default="local_faiss",
        description="Vector store backend (e.g. local_faiss, chroma, pinecone).",
    )

    # ------------------------------------------------------------------
    #   Retrieval parameters
    # ------------------------------------------------------------------
    RETRIEVAL_TOP_K: PositiveInt = Field(
        default=10,
        description=(
            "Number of nearest-neighbour candidates to retrieve from the "
            "vector store before metadata filtering and re-ranking."
        ),
    )
    RETRIEVAL_SCORE_THRESHOLD: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum similarity score (0-1) a candidate must reach to be "
            "considered.  0.0 disables the threshold."
        ),
    )

    # ------------------------------------------------------------------
    #   Logging
    # ------------------------------------------------------------------
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Root log level for the application.",
    )

    # ------------------------------------------------------------------
    #   Environment tag
    # ------------------------------------------------------------------
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment.  Can be used for feature flags.",
    )

    # ------------------------------------------------------------------
    #   Pydantic-settings configuration
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton :class:`Settings` instance.

    The ``@lru_cache`` decorator guarantees the environment is parsed exactly
    once per process lifetime.  All callers receive the same immutable object.

    Raises
    ------
    src.core.exceptions.ConfigurationError
        Wraps any ``pydantic.ValidationError`` so that upstream code can catch
        a domain-specific exception instead of a Pydantic internal.
    """
    from src.core.exceptions import ConfigurationError

    try:
        return Settings()
    except Exception as exc:
        raise ConfigurationError(
            f"Failed to load application settings: {exc}",
            cause=exc,
        ) from exc
