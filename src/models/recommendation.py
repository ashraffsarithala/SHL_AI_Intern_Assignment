"""
Recommendation Domain Model.

Represents a recommendation returned to the client.

Matches the SHL API specification exactly.
"""

from pydantic import BaseModel, ConfigDict, Field


class Recommendation(BaseModel):
    """
    Recommendation returned by the API.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,
        description="Assessment name.",
    )

    url: str = Field(
        ...,
        description="Official SHL catalog URL.",
    )

    test_type: str = Field(
        ...,
        description="Assessment type.",
    )