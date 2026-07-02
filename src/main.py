"""
Main application entry point.
"""

from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="SHL Assessment Recommendation Agent",
    description="AI-powered recommendation service for SHL assessments.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "SHL Assessment Recommendation Agent is running."
    }