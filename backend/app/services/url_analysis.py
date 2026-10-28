"""
URL analysis service — stub for T-01.

The real implementation (feature extraction + model loading) is built in T-02/T-03.
This stub returns a clearly labeled Unable to Assess response so that the API
endpoints are testable end-to-end before the model exists.
"""

from __future__ import annotations

from app.schemas import (
    AnalysisMethod,
    Indicator,
    Language,
    RiskCategory,
    UrlAnalysisResponse,
)

_DISCLAIMER = (
    "This assessment is produced by automated analysis and can be wrong. "
    "It does not guarantee that a URL is safe or unsafe. "
    "Always verify through official channels independently."
)

_RECOMMENDATIONS = [
    "Do not click the link until you have verified it independently.",
    "Search for the organisation's official website using a search engine rather than using the submitted link.",
    "If you received this URL unexpectedly, treat it with extra caution.",
]


def analyze_url(url: str, language: Language) -> UrlAnalysisResponse:
    """
    Analyze a URL string using local features only.

    STUB — returns Unable to Assess until the trained model artifact is
    available (T-02).  The URL is never opened, fetched, resolved, or previewed.
    """
    return UrlAnalysisResponse(
        category=RiskCategory.unable_to_assess,
        method=AnalysisMethod.unable_to_assess,
        indicators=[
            Indicator(
                code="model_not_ready",
                label="Analysis not yet available",
                explanation=(
                    "The URL classification model has not been trained yet. "
                    "This response will be replaced with real analysis in T-02/T-03."
                ),
            )
        ],
        summary="URL analysis is not yet available. The model is being built.",
        recommendations=_RECOMMENDATIONS,
        disclaimer=_DISCLAIMER,
        language=language,
    )
