"""Route handler for /health."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Return service liveness.

    Does not expose secrets, internal paths, or filesystem information.
    """
    return HealthResponse(status="ok")
