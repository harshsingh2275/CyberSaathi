"""
Pydantic request and response schemas.

These define the stable JSON contracts for every public endpoint.
Changing a field name or removing a required field is a breaking change.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ── Shared enums ──────────────────────────────────────────────────────────────


class Language(str, Enum):
    en = "en"
    hinglish = "hinglish"


class RiskCategory(str, Enum):
    high_risk = "High Risk"
    suspicious = "Suspicious"
    no_obvious_warning_signs = "No Obvious Warning Signs"
    unable_to_assess = "Unable to Assess"


class AnalysisMethod(str, Enum):
    ml_model = "ml_model"
    rules = "rules"
    ml_model_and_rules = "ml_model_and_rules"
    unable_to_assess = "unable_to_assess"


# ── Indicator ─────────────────────────────────────────────────────────────────


class Indicator(BaseModel):
    """A single detected warning indicator."""

    code: str = Field(..., description="Machine-readable identifier for this indicator.")
    label: str = Field(..., description="Short human-readable label.")
    explanation: str = Field(..., description="Beginner-friendly explanation.")


# ── URL analysis ──────────────────────────────────────────────────────────────


class UrlAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    language: Language = Language.en

    @field_validator("url")
    @classmethod
    def no_control_characters(cls, v: str) -> str:
        if any(ord(c) < 32 for c in v):
            raise ValueError("URL must not contain control characters.")
        stripped = v.strip()
        if not stripped:
            raise ValueError("URL must not be empty or whitespace only.")
        return stripped


class UrlAnalysisResponse(BaseModel):
    category: RiskCategory
    method: AnalysisMethod
    indicators: list[Indicator]
    summary: str
    recommendations: list[str]
    disclaimer: str
    language: Language


# ── Message analysis ──────────────────────────────────────────────────────────


class MessageAnalysisRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    language: Language = Language.en

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message must not be empty or whitespace only.")
        return stripped


class MessageAnalysisResponse(BaseModel):
    category: RiskCategory
    method: AnalysisMethod
    indicators: list[Indicator]
    summary: str
    recommendations: list[str]
    disclaimer: str
    language: Language


# ── Health ────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
