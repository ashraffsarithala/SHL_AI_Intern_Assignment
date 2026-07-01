"""
Shared type definitions for the SHL Assessment Recommendation Agent.

This module contains **only** type aliases, literal unions, TypedDicts, and
lightweight protocols that are used across multiple packages.  It deliberately
imports nothing from other ``src.*`` modules so that it can be imported
anywhere without creating circular dependencies.

Design Decisions
----------------
1. **No runtime logic** – Every definition here is a pure typing construct.
   The module has zero side-effects at import time.

2. **Literal unions mirror the FSM** – ``ConversationStage`` and ``AgentAction``
   encode the exact states and transitions from the frozen architecture.  Using
   ``Literal`` rather than ``enum.Enum`` keeps JSON serialisation trivial and
   avoids the Pydantic v2 enum-coercion dance.

3. **TypedDicts for catalog shape** – ``RawCatalogEntry`` captures the exact
   field names found in ``data/raw/catalog.json`` so that the parser (Phase 3)
   has a single, documented reference for the expected schema.

4. **Protocols for duck-typed subsystems** – ``VectorStoreProtocol`` and
   ``LLMClientProtocol`` define the minimal interfaces that concrete
   implementations must satisfy.  Using ``Protocol`` instead of ABCs avoids
   forcing inheritance and keeps the dependency graph clean.

5. **Aliases for readability** – ``JSONType``, ``Embedding``, ``PathLike``
   prevent repetitive ``Union[...]`` annotations scattered across the codebase.
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    Any,
    Literal,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

# ---------------------------------------------------------------------------
#   Primitive type aliases
# ---------------------------------------------------------------------------

JSONScalar = Union[str, int, float, bool, None]
"""A single JSON-compatible scalar value."""

JSONType = Union[JSONScalar, list[Any], dict[str, Any]]
"""Recursive JSON-compatible type (scalar, array, or object)."""

PathLike = Union[str, Path]
"""Anything that can be passed to ``pathlib.Path()``."""

Embedding = list[float]
"""Dense vector representation of a text chunk."""

# ---------------------------------------------------------------------------
#   Literal unions — FSM states from the frozen architecture
# ---------------------------------------------------------------------------

ConversationStage = Literal[
    "ANALYZE",
    "CLARIFY",
    "RETRIEVE",
    "FILTER",
    "RANK",
    "RECOMMEND",
    "REFINE",
    "COMPARE",
    "REFUSE",
    "FINISH",
]
"""
Every state in the deterministic Finite State Machine defined in the
architecture document.  The Decision Engine uses these to drive transitions.
"""

AgentAction = Literal[
    "clarify",
    "recommend",
    "refine",
    "compare",
    "refuse",
]
"""
High-level action label that the Decision Engine emits after evaluating the
extracted entities.  Maps 1-to-1 onto the behavioural modes required by the
SHL assignment (clarify / recommend / refine / compare / refuse).
"""

MessageRole = Literal["user", "assistant"]
"""Role tag attached to each message in the conversation history."""

# ---------------------------------------------------------------------------
#   TypedDicts — catalog data shape
# ---------------------------------------------------------------------------

class RawCatalogEntry(TypedDict, total=False):
    """Schema of a single entry in ``data/raw/catalog.json``.

    ``total=False`` because some fields (``duration``, ``languages_raw``) can be
    empty strings in the raw data and are therefore treated as optional during
    parsing.

    This definition is the single source of truth for what the parser expects;
    if the catalog schema ever changes, only this TypedDict and the parser need
    updating.
    """

    entity_id: str
    name: str
    link: str
    scraped_at: str
    job_levels: list[str]
    job_levels_raw: str
    languages: list[str]
    languages_raw: str
    duration: str
    duration_raw: str
    status: str
    remote: str
    adaptive: str
    description: str
    keys: list[str]


class RecommendationItem(TypedDict):
    """Shape of a single item in the ``recommendations`` array of the API
    response.  Matches the SHL output schema exactly."""

    name: str
    link: str
    test_type: str
    keys: list[str]
    duration: str
    languages: str


# ---------------------------------------------------------------------------
#   Protocols — structural interfaces for duck-typed subsystems
# ---------------------------------------------------------------------------

@runtime_checkable
class VectorStoreProtocol(Protocol):
    """Minimal interface that any vector-database backend must implement.

    Using a Protocol rather than an abstract base class means concrete
    implementations (FAISS, Chroma, etc.) do not need to inherit from a shared
    parent — they just need to expose these two methods.
    """

    def upsert(
        self,
        ids: list[str],
        embeddings: list[Embedding],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Insert or update vectors identified by their IDs."""
        ...

    def query(
        self,
        embedding: Embedding,
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[str, float]]:
        """Return the ``top_k`` most similar ``(id, score)`` pairs."""
        ...


@runtime_checkable
class LLMClientProtocol(Protocol):
    """Minimal interface that the LLM client wrapper must implement.

    The agent subsystem depends on this protocol, not on a concrete vendor SDK,
    making it straightforward to swap providers or inject a mock during testing.
    """

    def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> str:
        """Return the model's text completion for the given prompt."""
        ...
