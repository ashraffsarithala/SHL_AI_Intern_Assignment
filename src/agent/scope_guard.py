"""
Scope Guard.

Determines whether a user request is within the supported scope of the
SHL Assessment Recommendation Agent.

Responsibilities
----------------
- Detect prompt injection attempts.
- Detect off-topic questions.
- Produce deterministic refusal responses.

This module intentionally contains no LLM calls.
"""

from __future__ import annotations


class ScopeGuard:
    """
    Determines whether a request is allowed.
    """

    _PROMPT_INJECTION_PATTERNS = (
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "reveal your prompt",
        "show your prompt",
        "act as",
        "jailbreak",
        "pretend you are",
        "bypass",
    )

    _OFF_TOPIC_PATTERNS = (
        "weather",
        "ipl",
        "cricket",
        "football",
        "movie",
        "recipe",
        "politics",
        "prime minister",
        "president",
        "stock market",
        "bitcoin",
        "python code",
        "write code",
        "leetcode",
        "tell me a joke",
    )

    @staticmethod
    def is_allowed(
        message: str,
    ) -> bool:
        """
        Determine whether the message is within scope.
        """

        text = message.lower()

        for pattern in ScopeGuard._PROMPT_INJECTION_PATTERNS:
            if pattern in text:
                return False

        for pattern in ScopeGuard._OFF_TOPIC_PATTERNS:
            if pattern in text:
                return False

        return True

    @staticmethod
    def refusal_message() -> str:
        """
        Return the standard refusal response.
        """

        return (
            "I'm designed to help recommend SHL assessments based on "
            "job roles, skills, seniority levels, languages, and related "
            "assessment requirements. I can't assist with requests that "
            "fall outside that scope."
        )