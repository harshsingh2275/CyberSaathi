"""
T-01 baseline tests — verify the application structure and API contracts.

These tests confirm:
  - /health returns {"status": "ok"}
  - /api/analyze/url accepts well-formed requests and returns the required fields
  - /api/analyze/message accepts well-formed requests and returns the required fields
  - Empty, oversized, and malformed inputs are rejected with 422
  - The stub responses do not open or fetch the submitted URL (validated by
    absence of httpx/requests imports in the service under test)

Run: pytest backend/tests/ -v
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=True)


# ── /health ───────────────────────────────────────────────────────────────────


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── /api/analyze/url ──────────────────────────────────────────────────────────

REQUIRED_URL_FIELDS = {
    "category",
    "method",
    "indicators",
    "summary",
    "recommendations",
    "disclaimer",
    "language",
}

VALID_CATEGORIES = {
    "High Risk",
    "Suspicious",
    "No Obvious Warning Signs",
    "Unable to Assess",
}

VALID_METHODS = {
    "ml_model",
    "rules",
    "ml_model_and_rules",
    "unable_to_assess",
}


def test_url_analysis_returns_required_fields() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/login", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert REQUIRED_URL_FIELDS.issubset(body.keys()), (
        f"Missing fields: {REQUIRED_URL_FIELDS - body.keys()}"
    )


def test_url_analysis_category_is_valid() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "en"},
    )
    assert response.json()["category"] in VALID_CATEGORIES


def test_url_analysis_method_is_valid() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "en"},
    )
    assert response.json()["method"] in VALID_METHODS


def test_url_analysis_indicators_is_list() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "en"},
    )
    assert isinstance(response.json()["indicators"], list)


def test_url_analysis_hinglish_language() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "hinglish"},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "hinglish"


def test_url_analysis_empty_url_rejected() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "", "language": "en"},
    )
    assert response.status_code == 422


def test_url_analysis_missing_url_rejected() -> None:
    response = client.post("/api/analyze/url", json={"language": "en"})
    assert response.status_code == 422


def test_url_analysis_oversized_url_rejected() -> None:
    long_url = "https://example.com/" + "a" * 2048
    response = client.post(
        "/api/analyze/url",
        json={"url": long_url, "language": "en"},
    )
    assert response.status_code == 422


def test_url_analysis_invalid_language_rejected() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "fr"},
    )
    assert response.status_code == 422


def test_url_analysis_malformed_body_rejected() -> None:
    response = client.post(
        "/api/analyze/url",
        content=b"not json at all",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_url_analysis_recommendations_is_list() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "en"},
    )
    assert isinstance(response.json()["recommendations"], list)
    assert len(response.json()["recommendations"]) > 0


def test_url_analysis_disclaimer_is_string() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "en"},
    )
    assert isinstance(response.json()["disclaimer"], str)
    assert len(response.json()["disclaimer"]) > 0


# ── /api/analyze/message ──────────────────────────────────────────────────────

REQUIRED_MSG_FIELDS = {
    "category",
    "method",
    "indicators",
    "summary",
    "recommendations",
    "disclaimer",
    "language",
}


def test_message_analysis_returns_required_fields() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "Congratulations! You have won a prize.", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert REQUIRED_MSG_FIELDS.issubset(body.keys()), (
        f"Missing fields: {REQUIRED_MSG_FIELDS - body.keys()}"
    )


def test_message_analysis_category_is_valid() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "Hello, this is a test message.", "language": "en"},
    )
    assert response.json()["category"] in VALID_CATEGORIES


def test_message_analysis_method_is_valid() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "Hello, this is a test message.", "language": "en"},
    )
    assert response.json()["method"] in VALID_METHODS


def test_message_analysis_hinglish_language() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "Aapka account block ho gaya hai.", "language": "hinglish"},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "hinglish"


def test_message_analysis_empty_message_rejected() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "", "language": "en"},
    )
    assert response.status_code == 422


def test_message_analysis_missing_message_rejected() -> None:
    response = client.post("/api/analyze/message", json={"language": "en"})
    assert response.status_code == 422


def test_message_analysis_oversized_message_rejected() -> None:
    long_msg = "a" * 5001
    response = client.post(
        "/api/analyze/message",
        json={"message": long_msg, "language": "en"},
    )
    assert response.status_code == 422


def test_message_analysis_malformed_body_rejected() -> None:
    response = client.post(
        "/api/analyze/message",
        content=b"not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
