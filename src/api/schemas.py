"""
API Schemas.

Defines the public request and response contracts for the SHL
Assessment Recommendation Agent.

These schemas are intentionally separate from the internal domain
models to avoid leaking implementation details.
"""

from pydantic import BaseModel, ConfigDict, Field

from src.models.message import Message
from src.models.recommendation import Recommendation


class ChatRequest(BaseModel):
    """
    Request body for POST /chat.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    messages: list[Message] = Field(
        ...,
        min_length=1,
        description="Complete conversation history.",
    )


class ChatResponse(BaseModel):
    """
    Response returned by POST /chat.

    Matches the SHL assignment schema exactly.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    reply: str = Field(
        ...,
        min_length=1,
        description="Assistant reply.",
    )

    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Recommended SHL assessments.",
    )

    end_of_conversation: bool = Field(
        default=False,
        description="Whether the task is complete.",
    )


class HealthResponse(BaseModel):
    """
    Response returned by GET /health.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: str = Field(
        default="ok",
        description="Application health.",
    )