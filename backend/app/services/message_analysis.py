"""
Message analysis service — stub for T-01.

Real rule-based (and optionally ML) implementation is built in T-03.
This stub returns Unable to Assess so that the API is end-to-end testable
before the analysis logic exists.
"""

from __future__ import annotations

from app.schemas import (
    AnalysisMethod,
    Indicator,
    Language,
    MessageAnalysisResponse,
    RiskCategory,
)

_DISCLAIMER = (
    "This assessment is produced by automated rule-based analysis and can be wrong. "
    "It does not guarantee that a message is safe or a scam. "
    "Always verify communications through official channels independently."
)

_RECOMMENDATIONS = [
    "Do not share OTPs, passwords, or financial details with anyone.",
    "Verify any job, internship, or scholarship offer through the organisation's official website.",
    "If a message demands urgent payment, treat it with extra caution.",
    "Contact the claimed sender through a verified official channel before acting.",
]


def analyze_message(message: str, language: Language) -> MessageAnalysisResponse:
    """
    Analyze a message string for scam/phishing indicators.

    STUB — returns Unable to Assess until rule-based logic is implemented in T-03.
    Raw message text is never stored or logged.
    """
    return MessageAnalysisResponse(
        category=RiskCategory.unable_to_assess,
        method=AnalysisMethod.unable_to_assess,
        indicators=[
            Indicator(
                code="analysis_not_ready",
                label="Analysis not yet available",
                explanation=(
                    "Message analysis rules have not been implemented yet. "
                    "This response will be replaced with real analysis in T-03."
                ),
            )
        ],
        summary="Message analysis is not yet available.",
        recommendations=_RECOMMENDATIONS,
        disclaimer=_DISCLAIMER,
        language=language,
    )
