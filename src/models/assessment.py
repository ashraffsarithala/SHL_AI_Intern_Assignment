"""
Assessment Domain Model.

Represents a normalized SHL assessment used throughout the
recommendation pipeline.

This model intentionally contains only business/domain fields required
at runtime. Raw ingestion fields from catalog.json (such as *_raw,
scraped_at, and status) are handled during catalog processing and are
not part of the domain model.
"""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Assessment(BaseModel):
    """
    Represents a single SHL assessment.

    This model is the canonical runtime representation used by retrieval,
    recommendation, comparison, and API response generation.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    entity_id: str = Field(
        ...,
        description="Unique SHL assessment identifier.",
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=250,
        description="Assessment name.",
    )

    link: HttpUrl = Field(
        ...,
        description="Official SHL catalog URL.",
    )

    job_levels: list[str] = Field(
        default_factory=list,
        description="Applicable job levels.",
    )

    languages: list[str] = Field(
        default_factory=list,
        description="Supported assessment languages.",
    )

    duration: str = Field(
        default="",
        description="Approximate completion time.",
    )

    remote: bool = Field(
        ...,
        description="Whether remote delivery is supported.",
    )

    adaptive: bool = Field(
        ...,
        description="Whether the assessment is adaptive.",
    )

    description: str = Field(
        default="",
        description="Assessment description.",
    )

    keys: list[str] = Field(
        default_factory=list,
        description="SHL assessment categories.",
    )