"""
Response Generator.

Generates the assistant reply returned by POST /chat.
"""

from __future__ import annotations

from src.models.recommendation import Recommendation


class ResponseGenerator:
    """
    Generates assistant responses.
    """

    @staticmethod
    def generate(
        recommendations: list[Recommendation],
    ) -> str:
        """
        Generate the assistant reply.
        """

        if not recommendations:
            return (
                "I couldn't find any SHL assessments matching your request. "
                "Please provide more details such as job role, skills, "
                "seniority level, or assessment category."
            )

        lines: list[str] = [
            (
                f"I found {len(recommendations)} assessment(s) "
                "matching your request."
            ),
            "",
            "Recommended assessments:",
        ]

        for recommendation in recommendations:
            lines.append(
                f"- {recommendation.name}"
            )

        return "\n".join(lines)