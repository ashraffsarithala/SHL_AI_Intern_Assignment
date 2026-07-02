"""
Comparison Engine.

Provides catalog-grounded comparison between two SHL assessments.
"""

from __future__ import annotations

from src.catalog.catalog_repository import CatalogRepository


class ComparisonEngine:
    """
    Compare two SHL assessments using catalog data only.
    """

    def __init__(
        self,
        repository: CatalogRepository,
    ) -> None:
        self._repository = repository

    def compare(
        self,
        first_name: str,
        second_name: str,
    ) -> str:
        """
        Compare two assessments.
        """

        first = self._repository.get_by_name(first_name)
        second = self._repository.get_by_name(second_name)

        if first is None:
            return (
                f"I couldn't find '{first_name}' in the SHL catalog."
            )

        if second is None:
            return (
                f"I couldn't find '{second_name}' in the SHL catalog."
            )

        lines = [
            f"Comparison between {first.name} and {second.name}",
            "",
            "Job Levels:",
            f"• {first.name}: {', '.join(first.job_levels) or 'Not specified'}",
            f"• {second.name}: {', '.join(second.job_levels) or 'Not specified'}",
            "",
            "Languages:",
            f"• {first.name}: {', '.join(first.languages) or 'Not specified'}",
            f"• {second.name}: {', '.join(second.languages) or 'Not specified'}",
            "",
            "Duration:",
            f"• {first.name}: {first.duration or 'Not specified'}",
            f"• {second.name}: {second.duration or 'Not specified'}",
            "",
            "Remote Delivery:",
            f"• {first.name}: {'Yes' if first.remote else 'No'}",
            f"• {second.name}: {'Yes' if second.remote else 'No'}",
            "",
            "Adaptive:",
            f"• {first.name}: {'Yes' if first.adaptive else 'No'}",
            f"• {second.name}: {'Yes' if second.adaptive else 'No'}",
            "",
            "Assessment Categories:",
            f"• {first.name}: {', '.join(first.keys)}",
            f"• {second.name}: {', '.join(second.keys)}",
        ]

        return "\n".join(lines)