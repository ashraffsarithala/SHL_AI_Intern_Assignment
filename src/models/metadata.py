"""
Retrieval Metadata Domain Model.

Represents internal metadata generated during retrieval and ranking.

This model is intentionally NOT part of the public API schema.
It exists solely to support retrieval, recommendation ranking,
evaluation, debugging, and failure analysis.

No fields from the SHL catalog belong here.
"""

from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    """
    Internal retrieval metadata associated with a recommended assessment.

    Attributes:
        retrieval_score:
            Normalized similarity score assigned by the retrieval engine.

        retrieval_rank:
            Rank of the retrieved assessment after retrieval/reranking.

        matched_catalog_fields:
            Catalog fields that contributed to the retrieval match.

        matched_constraints:
            User constraints successfully matched by this assessment.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    retrieval_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized retrieval similarity score.",
    )

    retrieval_rank: int = Field(
        ...,
        ge=1,
        description="Rank assigned after retrieval.",
    )

    matched_catalog_fields: list[str] = Field(
        default_factory=list,
        description="Catalog fields contributing to retrieval.",
    )

    matched_constraints: list[str] = Field(
        default_factory=list,
        description="User constraints satisfied by this assessment.",
    )