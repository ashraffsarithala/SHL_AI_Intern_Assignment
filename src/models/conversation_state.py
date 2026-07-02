"""
Conversation State Domain Model.

Represents the current reasoning state of the SHL Assessment
Recommendation Agent.

The ConversationState is produced by the Analyzer and consumed by the
Decision Engine. It stores only decision-making information and does
not duplicate conversation history or recommendation data.
"""

from pydantic import BaseModel, ConfigDict, Field

from src.core.types import ConversationIntent, ConversationStage
from src.models.search_constraints import SearchConstraints


class ConversationState(BaseModel):
    """
    Represents the current state of the conversation.

    This model contains only information required for routing and
    decision making.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    stage: ConversationStage = Field(
        ...,
        description="Current conversation stage.",
    )

    intent: ConversationIntent = Field(
        ...,
        description="Current user intent.",
    )

    constraints: SearchConstraints = Field(
        default_factory=SearchConstraints,
        description="Normalized search constraints extracted from the conversation.",
    )

    retrieval_limit: int = Field(
        default=10,
        ge=1,
        le=10,
        description="Maximum number of assessments to retrieve.",
    )

    missing_constraints: list[str] = Field(
        default_factory=list,
        description="Required information still missing before recommendation.",
    )

    comparison_targets: list[str] = Field(
        default_factory=list,
        description="Assessment names requested for comparison.",
    )

    ready_to_recommend: bool = Field(
        default=False,
        description="Whether sufficient information exists to recommend assessments.",
    )

    end_of_conversation: bool = Field(
        default=False,
        description="Whether the conversation has reached a natural completion.",
    )