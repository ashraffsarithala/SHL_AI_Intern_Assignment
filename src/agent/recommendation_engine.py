"""
Recommendation Engine.

Converts retrieved assessments into API Recommendation models.
"""

from __future__ import annotations

from src.models.assessment import Assessment
from src.models.recommendation import Recommendation
from src.models.search_constraints import SearchConstraints


class RecommendationEngine:
    """
    Builds API recommendations from retrieved assessments.
    """

    @staticmethod
    def recommend(
        assessments: list[Assessment],
        constraints: SearchConstraints,
    ) -> list[Recommendation]:
        """
        Convert assessments into Recommendation models.
        """

        recommendations: list[Recommendation] = []

        for assessment in assessments:

            # NOTE:
            # The provided SHL catalog does not expose an explicit
            # "test_type" field. Until one exists, return an empty
            # string instead of inventing values.
            recommendations.append(
                Recommendation(
                    name=assessment.name,
                    url=str(assessment.link),
                    test_type="",
                )
            )

        return recommendations