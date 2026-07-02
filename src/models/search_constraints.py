"""
Search Constraints Domain Model.

Represents the normalized constraints extracted from the user's
conversation.

These constraints are produced by the Analyzer and consumed by the
Retriever and Recommendation Engine.

This model intentionally contains only structured search information.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SearchConstraints(BaseModel):
    """
    Normalized constraints extracted from the conversation.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords extracted from the user's request.",
    )

    job_levels: list[str] = Field(
        default_factory=list,
        description="Requested SHL job levels.",
    )

    languages: list[str] = Field(
        default_factory=list,
        description="Requested assessment languages.",
    )

    categories: list[str] = Field(
        default_factory=list,
        description="Requested SHL assessment categories.",
    )

    duration: str | None = Field(
        default=None,
        description="Requested assessment duration.",
    )

    remote: bool | None = Field(
        default=None,
        description="Whether remote testing is required.",
    )

    adaptive: bool | None = Field(
        default=None,
        description="Whether adaptive testing is required.",
    )