"""
Conversation Domain Model.

Defines the complete conversation exchanged between the client and the
SHL Assessment Recommendation Agent.

The backend is stateless; therefore, the client sends the entire
conversation history with every POST /chat request.

A Conversation is simply an ordered collection of validated Message
objects. It intentionally contains no business logic, state,
recommendations, or retrieval metadata.
"""

from pydantic import BaseModel, ConfigDict, Field

from src.models.message import Message


class Conversation(BaseModel):
    """
    Represents the full conversation history.

    Attributes:
        messages:
            Chronologically ordered conversation exchanged between
            the user and the assistant.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    messages: list[Message] = Field(
        ...,
        min_length=1,
        description="Chronological list of conversation messages.",
    )