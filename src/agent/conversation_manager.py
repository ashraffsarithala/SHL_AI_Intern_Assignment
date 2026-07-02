"""
Conversation Manager.

Provides utility operations over a Conversation.

Responsibilities
----------------
- Retrieve the latest user message.
- Retrieve the latest assistant message.
- Validate conversation ordering.

This class intentionally contains no business logic.
"""

from __future__ import annotations

from src.models.conversation import Conversation
from src.models.message import Message


class ConversationManager:
    """
    Utility class for working with Conversation objects.
    """

    @staticmethod
    def latest_user_message(
        conversation: Conversation,
    ) -> Message:
        """
        Return the latest user message.

        Raises
        ------
        ValueError
            If no user message exists.
        """

        for message in reversed(conversation.messages):

            if message.role == "user":
                return message

        raise ValueError(
            "Conversation contains no user message."
        )

    @staticmethod
    def latest_assistant_message(
        conversation: Conversation,
    ) -> Message | None:
        """
        Return the latest assistant message.

        Returns
        -------
        Message | None
        """

        for message in reversed(conversation.messages):

            if message.role == "assistant":
                return message

        return None

    @staticmethod
    def user_messages(
        conversation: Conversation,
    ) -> list[Message]:
        """
        Return all user messages.
        """

        return [
            message
            for message in conversation.messages
            if message.role == "user"
        ]

    @staticmethod
    def assistant_messages(
        conversation: Conversation,
    ) -> list[Message]:
        """
        Return all assistant messages.
        """

        return [
            message
            for message in conversation.messages
            if message.role == "assistant"
        ]

    @staticmethod
    def message_count(
        conversation: Conversation,
    ) -> int:
        """
        Return the total number of messages.
        """

        return len(conversation.messages)

    @staticmethod
    def is_empty(
        conversation: Conversation,
    ) -> bool:
        """
        Determine whether the conversation is empty.
        """

        return len(conversation.messages) == 0