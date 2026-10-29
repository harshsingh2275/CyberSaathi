"""Route handlers for /api/analyze/url and /api/analyze/message."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas import (
    MessageAnalysisRequest,
    MessageAnalysisResponse,
    UrlAnalysisRequest,
    UrlAnalysisResponse,
)
from app.services.message_analysis import analyze_message
from app.services.url_analysis import analyze_url
from app.config import get_settings

router = APIRouter()


def _enforce_url_limit(url: str) -> None:
    settings = get_settings()
    if len(url) > settings.max_url_length:
        raise HTTPException(
            status_code=422,
            detail=f"URL exceeds maximum length of {settings.max_url_length} characters.",
        )


def _enforce_message_limit(message: str) -> None:
    settings = get_settings()
    if len(message) > settings.max_message_length:
        raise HTTPException(
            status_code=422,
            detail=f"Message exceeds maximum length of {settings.max_message_length} characters.",
        )


@router.post("/api/analyze/url", response_model=UrlAnalysisResponse)
@router.post("/analyze/url", response_model=UrlAnalysisResponse, include_in_schema=False)
async def analyze_url_endpoint(body: UrlAnalysisRequest) -> UrlAnalysisResponse:
    """
    Analyze a URL string.

    The submitted URL is NEVER opened, fetched, previewed, resolved, or
    passed to any HTTP client.  Only local string features are examined.
    Raw input is not stored or logged.
    """
    _enforce_url_limit(body.url)
    return analyze_url(body.url, body.language)


@router.post("/api/analyze/message", response_model=MessageAnalysisResponse)
@router.post("/analyze/message", response_model=MessageAnalysisResponse, include_in_schema=False)
async def analyze_message_endpoint(
    body: MessageAnalysisRequest,
) -> MessageAnalysisResponse:
    """
    Analyze a copied message for scam/phishing indicators.

    Raw message text is never stored or logged.
    """
    _enforce_message_limit(body.message)
    return analyze_message(body.message, body.language)
