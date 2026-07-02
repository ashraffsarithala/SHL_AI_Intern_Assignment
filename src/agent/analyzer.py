"""
Conversation Analyzer.

Analyzes the latest user message and produces a structured
ConversationState consumed by the Decision Engine.

Responsibilities
----------------
- Detect conversation intent.
- Extract normalized search constraints.
- Detect missing information.
- Determine the next conversation stage.

This module contains deterministic logic only.
"""

from __future__ import annotations

import re

from src.agent.conversation_manager import ConversationManager
from src.core.types import ConversationIntent, ConversationStage
from src.models.conversation import Conversation
from src.models.conversation_state import ConversationState
from src.models.search_constraints import SearchConstraints


class Analyzer:
    """
    Deterministic conversation analyzer.
    """

    JOB_LEVELS = (
        "entry-level",
        "graduate",
        "general population",
        "professional individual contributor",
        "mid-professional",
        "front line manager",
        "manager",
        "director",
        "executive",
        "supervisor",
    )

    LANGUAGES = (
        "english",
        "english (usa)",
        "french",
        "german",
        "spanish",
        "italian",
        "portuguese",
        "japanese",
        "chinese",
    )

    CATEGORIES = (
        "knowledge & skills",
        "ability & aptitude",
        "competencies",
        "personality & behavior",
        "development & 360",
        "assessment exercises",
        "biodata & situational judgment",
    )

    RECOMMEND_KEYWORDS = (
        "recommend",
        "assessment",
        "test",
        "looking for",
        "need",
        "find",
        "suggest",
    )

    COMPARE_KEYWORDS = (
        "compare",
        "difference",
        "vs",
        "versus",
    )

    REMOTE_KEYWORDS = (
        "remote",
        "online",
        "virtual",
    )

    ADAPTIVE_KEYWORDS = (
        "adaptive",
    )

    def __init__(self) -> None:
        self._conversation_manager = ConversationManager()

    # ---------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize(
        text: str,
    ) -> str:
        """
        Normalize free text.
        """

        text = text.lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    # ---------------------------------------------------------
    # Intent detection
    # ---------------------------------------------------------

    def _detect_intent(
        self,
        text: str,
    ) -> ConversationIntent:
        """
        Detect conversation intent.
        """

        normalized = self._normalize(text)

        if any(
            keyword in normalized
            for keyword in self.COMPARE_KEYWORDS
        ):
            return "compare"

        if any(
            keyword in normalized
            for keyword in self.RECOMMEND_KEYWORDS
        ):
            return "recommend"

        return "clarify"

    # ---------------------------------------------------------
    # Generic extractor
    # ---------------------------------------------------------

    def _extract_matches(
        self,
        text: str,
        vocabulary: tuple[str, ...],
    ) -> list[str]:
        """
        Extract matching values from a vocabulary.
        """

        normalized = self._normalize(text)

        matches: list[str] = []

        for value in vocabulary:

            if value in normalized:
                matches.append(value)

        return matches

    # ---------------------------------------------------------
    # Keyword extraction
    # ---------------------------------------------------------

    def _extract_keywords(
        self,
        text: str,
    ) -> list[str]:
        """
        Extract remaining free-form keywords.
        """

        normalized = self._normalize(text)

        words = re.findall(
            r"[a-zA-Z0-9.+#]+",
            normalized,
        )

        stop_words = {
            "recommend",
            "assessment",
            "assessments",
            "test",
            "tests",
            "need",
            "find",
            "looking",
            "for",
            "with",
            "the",
            "a",
            "an",
            "to",
            "of",
            "and",
            "or",
            "please",
            "me",
        }

        keywords: list[str] = []

        for word in words:

            if len(word) < 2:
                continue

            if word in stop_words:
                continue

            if word not in keywords:
                keywords.append(word)

        return keywords

    # ---------------------------------------------------------
    # Boolean extraction
    # ---------------------------------------------------------

    def _extract_remote(
        self,
        text: str,
    ) -> bool | None:
        """
        Detect remote testing requirement.
        """

        normalized = self._normalize(text)

        if any(
            keyword in normalized
            for keyword in self.REMOTE_KEYWORDS
        ):
            return True

        return None

    def _extract_adaptive(
        self,
        text: str,
    ) -> bool | None:
        """
        Detect adaptive testing requirement.
        """

        normalized = self._normalize(text)

        if any(
            keyword in normalized
            for keyword in self.ADAPTIVE_KEYWORDS
        ):
            return True

        return None
    # ---------------------------------------------------------
    # Constraint construction
    # ---------------------------------------------------------

    def _build_constraints(
        self,
        text: str,
    ) -> SearchConstraints:
        """
        Build normalized search constraints from the
        latest user message.
        """

        return SearchConstraints(
            keywords=self._extract_keywords(text),
            job_levels=self._extract_matches(
                text,
                self.JOB_LEVELS,
            ),
            languages=self._extract_matches(
                text,
                self.LANGUAGES,
            ),
            categories=self._extract_matches(
                text,
                self.CATEGORIES,
            ),
            duration=None,
            remote=self._extract_remote(text),
            adaptive=self._extract_adaptive(text),
        )

    # ---------------------------------------------------------
    # Missing information
    # ---------------------------------------------------------

    @staticmethod
    def _missing_constraints(
        constraints: SearchConstraints,
    ) -> list[str]:
        """
        Determine whether additional clarification is required.
        """

        missing: list[str] = []

        if not constraints.keywords:
            missing.append("assessment or skill")

        return missing

    # ---------------------------------------------------------
    # Stage selection
    # ---------------------------------------------------------

    @staticmethod
    def _determine_stage(
        intent: ConversationIntent,
        missing_constraints: list[str],
    ) -> ConversationStage:
        """
        Select the next FSM stage.
        """

        if intent == "compare":
            return "COMPARE"

        if intent == "clarify":
            return "CLARIFY"

        if missing_constraints:
            return "CLARIFY"

        return "RETRIEVE"

    # ---------------------------------------------------------
    # Comparison targets
    # ---------------------------------------------------------



    @staticmethod
    def _extract_comparison_targets(
        text: str,
    ) -> list[str]:
        """
        Extract two assessment names from comparison requests.

        Examples
        --------
        Compare Python (New) and Java (New)
        Compare OPQ with Verify Interactive
        Difference between Java and Python
        """

        normalized = text.strip()

        lower = normalized.lower()

        separators = [
            " and ",
            " vs ",
            " versus ",
            " with ",
        ]

        for separator in separators:

            if separator in lower:

                index = lower.index(separator)

                left = normalized[:index]
                right = normalized[
                    index + len(separator):
                ]

                prefixes = (
                    "compare",
                    "difference between",
                    "compare between",
                )

                for prefix in prefixes:

                    if left.lower().startswith(prefix):

                        left = left[
                            len(prefix):
                        ]

                return [
                    left.strip(),
                    right.strip(),
                ]

        return []
        # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def analyze(
        self,
        conversation: Conversation,
    ) -> ConversationState:
        """
        Analyze the conversation and produce the current ConversationState.
        """

        text = (
            self._conversation_manager
            .merged_user_text(conversation)
        )

        intent = self._detect_intent(text)

        constraints = self._build_constraints(text)

        missing_constraints = self._missing_constraints(
            constraints
        )

        stage = self._determine_stage(
            intent,
            missing_constraints,
        )

        return ConversationState(
            stage=stage,
            intent=intent,
            constraints=constraints,
            missing_constraints=missing_constraints,
            comparison_targets=self._extract_comparison_targets(
                text,
            ),
            ready_to_recommend=(
                stage == "RETRIEVE"
            ),
            end_of_conversation=False,
            retrieval_limit=10,
        )