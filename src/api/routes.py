"""
API Routes.

Implements the SHL Assessment Recommendation Agent API.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.agent.analyzer import Analyzer
from src.agent.recommendation_engine import RecommendationEngine
from src.agent.response_generator import ResponseGenerator
from src.agent.retriever import Retriever
from src.agent.scope_guard import ScopeGuard

from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
)

from src.catalog.catalog_loader import CatalogLoader
from src.models.conversation import Conversation


router = APIRouter()

# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

catalog_loader = CatalogLoader(
    Path("data/raw/catalog.json")
)

repository = catalog_loader.load()

analyzer = Analyzer()

retriever = Retriever(repository)

recommendation_engine = RecommendationEngine()

response_generator = ResponseGenerator()

# ---------------------------------------------------------
# Health
# ---------------------------------------------------------


@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    """
    Health endpoint.
    """

    return HealthResponse()


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Main conversational endpoint.
    """

    try:

        conversation = Conversation(
            messages=request.messages,
        )
        latest_message = conversation.messages[-1].content

        if not ScopeGuard.is_allowed(latest_message):
            return ChatResponse(
                reply=ScopeGuard.refusal_message(),
                recommendations=[],
                end_of_conversation=True,
            )

        state = analyzer.analyze(
            conversation,
        )
                # -------------------------------------------------
        # Clarification
        # -------------------------------------------------

        if not state.ready_to_recommend:

            return ChatResponse(
                reply=(
                    "I need a little more information before I can "
                    "recommend SHL assessments. "
                    "Could you tell me the job role, seniority level, "
                    "required skills, or assessment type?"
                ),
                recommendations=[],
                end_of_conversation=False,
            )

        # -------------------------------------------------
        # Retrieval
        # -------------------------------------------------

        assessments = retriever.retrieve(
            state,
        )

        # -------------------------------------------------
        # Recommendation generation
        # -------------------------------------------------

        recommendations = recommendation_engine.recommend(
            assessments,
            state.constraints,
        )

        # -------------------------------------------------
        # Natural language response
        # -------------------------------------------------

        reply = response_generator.generate(
            recommendations,
        )

        return ChatResponse(
            reply=reply,
            recommendations=recommendations,
            end_of_conversation=(
                len(recommendations) > 0
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc