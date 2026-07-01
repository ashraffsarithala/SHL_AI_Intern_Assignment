"""
Recommendation Domain Model.

Represents a recommendation produced by the recommendation engine.

A Recommendation references an Assessment and provides a concise,
human-readable explanation describing why the assessment was selected.

This model intentionally does not include retrieval metadata.
"""

from pydantic import BaseModel, ConfigDict, Field

from src.models.assessment import Assessment


class Recommendation(BaseModel):
    """
    Represents a recommended SHL assessment.

    Attributes:
        assessment:
            The recommended assessment.

        reason:
            Human-readable explanation describing why this
            assessment was recommended.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    assessment: Assessment = Field(
        ...,
        description="Recommended SHL assessment.",
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Explanation for the recommendation.",
    )