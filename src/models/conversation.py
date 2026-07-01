"""
Conversation Model

Responsibility:
Define the internal representation of an entire conversation.

Implementation added in Phase 2.
"""
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

from pydantic import BaseModel, ConfigDict, Field, field_validator

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

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, messages: list[Message]) -> list[Message]:
        """
        Ensure that a conversation contains at least one message.

        Additional conversation validation (such as alternating roles)
        belongs to the Conversation Manager, not the domain model.
        """
        if not messages:
            raise ValueError("Conversation must contain at least one message.")

        return messages