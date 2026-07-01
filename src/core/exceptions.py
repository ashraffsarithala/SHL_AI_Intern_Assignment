"""
Custom exception hierarchy for the SHL Assessment Recommendation Agent.

This module defines a single-root exception tree rooted at :class:`ApplicationError`.
Every subsystem (catalog loading, retrieval, recommendation, etc.) has its own
exception class so that callers can catch at exactly the granularity they need:

    * ``except ApplicationError``     – any domain error
    * ``except CatalogError``         – catalog-specific errors only
    * ``except LLMError``             – LLM communication failures only

Design Decisions
----------------
1. **Single root** – Every custom exception inherits from ``ApplicationError``
   which itself inherits from ``Exception``.  This gives API-layer error handlers
   a single base class to catch without accidentally swallowing ``KeyboardInterrupt``
   or ``SystemExit``.

2. **Optional ``cause`` parameter** – Each exception accepts an optional ``cause``
   keyword so that low-level exceptions (e.g., ``httpx.ConnectError``) can be
   chained without losing the traceback.

3. **No business logic** – These classes only carry an error message and an
   optional cause.  Formatting, HTTP status mapping, and logging happen in the
   API layer (Phase 2+).

4. **One class per subsystem** – Matches the frozen architecture:
   config, catalog, retrieval, recommendation, comparison, scope guard, LLM,
   JSON formatting, validation, and evaluation each have a dedicated error.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
#   Root
# ---------------------------------------------------------------------------
class ApplicationError(Exception):
    """Base class for every domain exception in the project.

    Parameters
    ----------
    message:
        Human-readable description of what went wrong.
    cause:
        Optional lower-level exception that triggered this error.  Stored via
        the standard ``__cause__`` mechanism so that ``raise X from Y`` style
        chaining is preserved even when the caller uses the keyword form.
    """

    def __init__(
        self,
        message: str = "",
        *,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message or self.__class__.__name__)
        if cause is not None:
            self.__cause__ = cause


# ---------------------------------------------------------------------------
#   Infrastructure errors
# ---------------------------------------------------------------------------
class ConfigurationError(ApplicationError):
    """Raised when a required setting is missing, invalid, or fails validation.

    Typical triggers:
    * A mandatory environment variable (e.g. ``LLM_API_KEY``) is absent.
    * A setting value is outside its permitted range.
    """


# ---------------------------------------------------------------------------
#   Catalog subsystem
# ---------------------------------------------------------------------------
class CatalogError(ApplicationError):
    """Raised when the SHL product catalog cannot be loaded, parsed, or normalised.

    Typical triggers:
    * ``data/raw/catalog.json`` is missing or contains malformed JSON.
    * A catalog entry is missing required fields (``entity_id``, ``name``).
    """


# ---------------------------------------------------------------------------
#   Retrieval subsystem
# ---------------------------------------------------------------------------
class RetrievalError(ApplicationError):
    """Raised when the vector store query or metadata filter fails.

    Typical triggers:
    * The vector index has not been built yet.
    * The embedding API returns an error.
    * No candidates survive the metadata filter.
    """


# ---------------------------------------------------------------------------
#   Recommendation subsystem
# ---------------------------------------------------------------------------
class RecommendationError(ApplicationError):
    """Raised when the recommendation engine cannot produce a valid top-k list.

    Typical triggers:
    * Scoring or deduplication logic encounters an unexpected data shape.
    * The final list violates the 1-10 item constraint required by the SHL schema.
    """


# ---------------------------------------------------------------------------
#   Comparison subsystem
# ---------------------------------------------------------------------------
class ComparisonError(ApplicationError):
    """Raised when two assessments cannot be meaningfully compared.

    Typical triggers:
    * One or both of the requested assessment names are not found in the catalog.
    * The catalog entries lack fields needed for a comparison table.
    """


# ---------------------------------------------------------------------------
#   Scope guard / prompt injection
# ---------------------------------------------------------------------------
class ScopeGuardError(ApplicationError):
    """Raised when the scope guard detects an out-of-scope or adversarial input.

    Typical triggers:
    * Prompt injection attempt.
    * Request for hiring advice, salary information, or legal guidance.
    * Reference to non-SHL assessment products.
    """


# ---------------------------------------------------------------------------
#   LLM communication
# ---------------------------------------------------------------------------
class LLMError(ApplicationError):
    """Raised when the LLM provider returns an unexpected or unusable response.

    Typical triggers:
    * HTTP timeout or connection failure to the provider API.
    * Rate limiting (HTTP 429).
    * The model returns an unparseable response after all retries are exhausted.
    """


# ---------------------------------------------------------------------------
#   Validation
# ---------------------------------------------------------------------------
class ValidationError(ApplicationError):
    """Raised when incoming data fails schema or business-rule validation.

    Typical triggers:
    * The ``POST /chat`` request body is missing required fields.
    * An internal data structure violates a Pydantic model constraint.
    """


# ---------------------------------------------------------------------------
#   JSON formatting
# ---------------------------------------------------------------------------
class JSONFormattingError(ApplicationError):
    """Raised when the final API response cannot be serialized to the SHL schema.

    Typical triggers:
    * The ``recommendations`` array exceeds 10 items.
    * A required key (``reply``, ``recommendations``, ``end_of_conversation``)
      is missing from the assembled response dict.
    """


# ---------------------------------------------------------------------------
#   Evaluation harness
# ---------------------------------------------------------------------------
class EvaluationError(ApplicationError):
    """Raised when the automated evaluation / conversation replay fails.

    Typical triggers:
    * A sample conversation file cannot be parsed.
    * The agent response diverges from the expected golden output.
    """
