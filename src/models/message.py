"""
Message Model

Responsibility:
Define the internal representation of a chat message.

Implementation added in Phase 2.
"""
"""
Message Domain Model

Defines the fundamental unit of a conversation exchanged between the user
and the SHL Assessment Recommendation Agent.

A Message represents a single conversational turn and is intentionally kept
minimal. It is reused throughout the application by the conversation manager,
state machine, API schemas, evaluation framework, and replay utilities.

This model is immutable and validated using Pydantic.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MessageRole = Literal["user", "assistant"]


class Message(BaseModel):
    """
    Represents a single message exchanged during a conversation.

    Attributes:
        role:
            Identifies who produced the message.

        content:
            The natural language content of the message.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    role: MessageRole = Field(
        ...,
        description="Originator of the message."
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Natural language message content."
        )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        """
        Ensure message content is not empty after stripping whitespace.
        """
        if not value.strip():
            raise ValueError("Message content cannot be empty.")

        return value