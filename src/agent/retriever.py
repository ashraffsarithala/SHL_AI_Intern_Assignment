"""
Assessment Retriever.

Retrieves the most relevant SHL assessments from the catalog
using deterministic scoring.

Responsibilities
----------------
- Search the catalog repository.
- Score assessment relevance.
- Return the highest scoring assessments.

This module intentionally does NOT:
- generate natural language
- call the LLM
- rank recommendations using AI
"""

from __future__ import annotations

from src.catalog.catalog_repository import CatalogRepository
from src.models.assessment import Assessment
from src.models.conversation_state import ConversationState
from src.models.search_constraints import SearchConstraints


class Retriever:
    def __init__(
        self,
        repository: CatalogRepository,
    ) -> None:
        self._repository = repository

    # ---------------------------------------------------------
    # Keyword score
    # ---------------------------------------------------------

    @staticmethod
       
    def _keyword_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:
        """
        Compute a relevance score using weighted keyword matching.
        """

        score = 0

        name = assessment.name.lower()
        description = assessment.description.lower()
        categories = " ".join(assessment.keys).lower()

        for keyword in constraints.keywords:

            keyword = keyword.lower()

            # Highest priority: exact assessment name
            if keyword == name:
                score += 100

            # Strong match in assessment title
            elif keyword in name:
                score += 50

            # Medium match in categories
            elif keyword in categories:
                score += 20

            # Lowest match in description
            elif keyword in description:
                score += 10

        return score
    # ---------------------------------------------------------
    # Job level score
    # ---------------------------------------------------------

    @staticmethod
    def _job_level_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:

        score = 0

        assessment_levels = {
            level.lower()
            for level in assessment.job_levels
        }

        for level in constraints.job_levels:

            if level.lower() in assessment_levels:
                score += 3

        return score

    # ---------------------------------------------------------
    # Language score
    # ---------------------------------------------------------

    @staticmethod
    def _language_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:

        score = 0

        assessment_languages = {
            language.lower()
            for language in assessment.languages
        }

        for language in constraints.languages:

            if language.lower() in assessment_languages:
                score += 2

        return score
        # ---------------------------------------------------------
    # Category score
    # ---------------------------------------------------------

    @staticmethod
    def _category_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:
        score = 0

        assessment_categories = {
            category.lower()
            for category in assessment.keys
        }

        for category in constraints.categories:
            if category.lower() in assessment_categories:
                score += 2

        return score

    # ---------------------------------------------------------
    # Remote score
    # ---------------------------------------------------------

    @staticmethod
    def _remote_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:
        if (
            constraints.remote is None
            or assessment.remote == constraints.remote
        ):
            return 2 if constraints.remote is not None else 0

        return 0

    # ---------------------------------------------------------
    # Adaptive score
    # ---------------------------------------------------------

    @staticmethod
    def _adaptive_score(
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:
        if (
            constraints.adaptive is None
            or assessment.adaptive == constraints.adaptive
        ):
            return 2 if constraints.adaptive is not None else 0

        return 0

    # ---------------------------------------------------------
    # Total score
    # ---------------------------------------------------------

    def _score(
        self,
        assessment: Assessment,
        constraints: SearchConstraints,
    ) -> int:
        return (
            self._keyword_score(
                assessment,
                constraints,
            )
            + self._job_level_score(
                assessment,
                constraints,
            )
            + self._language_score(
                assessment,
                constraints,
            )
            + self._category_score(
                assessment,
                constraints,
            )
            + self._remote_score(
                assessment,
                constraints,
            )
            + self._adaptive_score(
                assessment,
                constraints,
            )
        )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def retrieve(
        self,
        state: ConversationState,
    ) -> list[Assessment]:
        """
        Retrieve the highest-scoring assessments.
        """

        constraints = state.constraints

        scored: list[tuple[int, Assessment]] = []

        for assessment in self._repository:

            score = self._score(
                assessment,
                constraints,
            )

            # Ignore weak matches
            if score >= 20:
                scored.append(
                    (
                        score,
                        assessment,
                    )
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        limit = min(
            state.retrieval_limit,
            10,
        )

        return [
            assessment
            for _, assessment in scored[:limit]
        ]
