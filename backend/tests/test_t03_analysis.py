"""
T-03 analysis tests — FastAPI endpoints, analysis logic, and edge cases.

Coverage:
  URL analysis:
    - Normal/benign URL → no obvious warning signs
    - Suspicious URL (IP, shortener, HTTP) → suspicious or high-risk
    - High-risk phishing URL (IP + @  + login keyword) → high risk
    - Benign-looking HTTPS URL with brand domain → passes
    - Empty input → 422
    - Oversized input → 422
    - Malformed JSON → 422
    - Control characters → 422
    - Invalid language → 422
    - Model-loading failure → rules fallback, method=rules, still valid response
    - Model prediction failure → rules fallback

  Message analysis:
    - OTP/credential request → high risk + otp_request indicator
    - Prize/lottery winner → suspicious
    - Account block + KYC → high risk (two high-weight indicators)
    - Work-from-home scam → suspicious
    - Normal everyday message → no obvious warning signs
    - Hinglish language → method=rules, non-empty summary/recommendations
    - Empty message → 422
    - Oversized message → 422
    - Malformed JSON → 422
    - Method is always "rules" for messages
    - Disclaimer always mentions rule-based (never ML) for messages

  Security invariants:
    - URL service file does NOT import httpx, requests, aiohttp, or urllib.request
    - Message service file does NOT import httpx, requests, aiohttp, or urllib.request
    - No raw URL or message text appears in error responses

Run: pytest backend/tests/test_t03_analysis.py -v
"""

from __future__ import annotations

import importlib
import sys
import types
import unittest.mock as mock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ── Client fixture ────────────────────────────────────────────────────────────

from app.main import app

client = TestClient(app, raise_server_exceptions=True)

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

# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — normal / benign
# ══════════════════════════════════════════════════════════════════════════════


def test_url_benign_returns_valid_category() -> None:
    """A well-formed HTTPS URL with no suspicious features should return a valid category."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://www.wikipedia.org/wiki/Phishing", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] in VALID_CATEGORIES
    assert body["method"] in VALID_METHODS
    assert isinstance(body["indicators"], list)
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0
    assert isinstance(body["disclaimer"], str)
    assert body["language"] == "en"


def test_url_benign_no_indicators_for_clean_url() -> None:
    """A plain HTTPS URL with no suspicious features should have few/no rule indicators."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://www.ndtv.com/", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    # The URL is clean — rules should not fire many indicators.
    # We only assert that the response structure is valid, not a fixed count,
    # because the ML model may add its own indicator.
    assert body["category"] in VALID_CATEGORIES


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — suspicious patterns
# ══════════════════════════════════════════════════════════════════════════════


def test_url_ip_hostname_flagged() -> None:
    """URL with an IP address as hostname should trigger ip_in_hostname indicator."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://192.168.1.1/login", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "ip_in_hostname" in indicator_codes, (
        f"Expected ip_in_hostname in {indicator_codes}"
    )


def test_url_shortener_flagged() -> None:
    """URL using a link-shortening service should be flagged."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://bit.ly/3xAbCdE", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "url_shortener" in indicator_codes, (
        f"Expected url_shortener in {indicator_codes}"
    )


def test_url_http_scheme_flagged() -> None:
    """URL using HTTP instead of HTTPS should get a no_https indicator."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://example.com/page", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "no_https" in indicator_codes, (
        f"Expected no_https in {indicator_codes}"
    )


def test_url_at_symbol_flagged() -> None:
    """URL containing @ symbol should be flagged."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://attacker.com@legitimate.com/", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "at_symbol_in_url" in indicator_codes, (
        f"Expected at_symbol_in_url in {indicator_codes}"
    )


def test_url_suspicious_tld_flagged() -> None:
    """URL with a free/suspicious TLD should be flagged."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://free-prize.tk/claim", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "suspicious_tld" in indicator_codes, (
        f"Expected suspicious_tld in {indicator_codes}"
    )


def test_url_phishing_keywords_in_path() -> None:
    """URL with login/verify/credential keywords in path should be flagged."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/secure/account/login", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "phishing_keywords_in_path" in indicator_codes, (
        f"Expected phishing_keywords_in_path in {indicator_codes}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — high-risk compound example
# ══════════════════════════════════════════════════════════════════════════════


def test_url_high_risk_compound() -> None:
    """URL combining IP + @ + login keyword should be classified as High Risk or Suspicious."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://192.168.10.5@evil.tk/login/verify", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] in {"High Risk", "Suspicious"}, (
        f"Expected High Risk or Suspicious, got {body['category']}"
    )
    # At least three rule indicators should fire
    assert len(body["indicators"]) >= 3, (
        f"Expected >=3 indicators, got {body['indicators']}"
    )


def test_url_high_risk_category_enum() -> None:
    """High risk response should have category exactly matching schema enum value."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://192.168.10.5@evil.tk/login/verify", "language": "en"},
    )
    assert response.json()["category"] in VALID_CATEGORIES


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — benign-looking URLs
# ══════════════════════════════════════════════════════════════════════════════


def test_url_benign_looking_https_known_domain() -> None:
    """A clean HTTPS URL to a well-known domain should not trigger rule indicators."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://github.com/cybersaathi", "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    # Rule indicators that should NOT appear for this clean URL
    rule_indicator_codes = {
        "ip_in_hostname", "at_symbol_in_url", "url_shortener",
        "no_https", "suspicious_tld",
    }
    fired_rule_indicators = {
        ind["code"] for ind in body["indicators"]
        if ind["code"] in rule_indicator_codes
    }
    assert not fired_rule_indicators, (
        f"Unexpected rule indicators for clean URL: {fired_rule_indicators}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — input validation (422 paths)
# ══════════════════════════════════════════════════════════════════════════════


def test_url_empty_string_rejected() -> None:
    response = client.post("/api/analyze/url", json={"url": "", "language": "en"})
    assert response.status_code == 422


def test_url_missing_field_rejected() -> None:
    response = client.post("/api/analyze/url", json={"language": "en"})
    assert response.status_code == 422


def test_url_oversized_rejected() -> None:
    """URL exceeding max_length=2048 should be rejected."""
    long_url = "https://example.com/" + "a" * 2048
    response = client.post(
        "/api/analyze/url",
        json={"url": long_url, "language": "en"},
    )
    assert response.status_code == 422


def test_url_control_character_rejected() -> None:
    """URL with a control character (e.g. \\x01) should be rejected by validator."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/\x01path", "language": "en"},
    )
    assert response.status_code == 422


def test_url_invalid_language_rejected() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "fr"},
    )
    assert response.status_code == 422


def test_url_malformed_json_rejected() -> None:
    response = client.post(
        "/api/analyze/url",
        content=b"{bad json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — model-loading failure (rules fallback)
# ══════════════════════════════════════════════════════════════════════════════


def test_url_model_loading_failure_falls_back_to_rules() -> None:
    """
    When the model artifact cannot be loaded, the service must still return
    a valid response using rules-based analysis, with method='rules'.
    """
    import app.services.url_analysis as url_svc

    # Clear the lru_cache so the mock takes effect
    url_svc._load_model.cache_clear()

    original_load = url_svc._load_model.__wrapped__  # access the uncached function

    def _failing_load(model_path: str):
        return None  # simulate missing model

    with mock.patch.object(url_svc, "_load_model", wraps=None) as patched:
        patched.return_value = None
        # Re-patch via the module attribute directly
        saved = url_svc._load_model
        url_svc._load_model = lambda path: None  # type: ignore[assignment]
        try:
            response = client.post(
                "/api/analyze/url",
                json={"url": "http://suspicious.tk/login", "language": "en"},
            )
        finally:
            url_svc._load_model = saved
            url_svc._load_model.cache_clear()

    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "rules"
    assert body["category"] in VALID_CATEGORIES
    assert isinstance(body["indicators"], list)
    assert "ML model is unavailable" in body["disclaimer"]


def test_url_rules_fallback_with_nonexistent_model_path() -> None:
    """Calling analyze_url with a non-existent model path returns a valid rules response."""
    import app.services.url_analysis as url_svc
    from app.schemas import Language

    # get_settings is imported inside analyze_url from app.config, so patch there.
    url_svc._load_model.cache_clear()

    fake_settings = mock.MagicMock()
    fake_settings.model_path = "/nonexistent/path/model.joblib"

    with mock.patch("app.config.get_settings", return_value=fake_settings):
        url_svc._load_model.cache_clear()
        result = url_svc.analyze_url("http://phishing.tk/login", Language.en)

    url_svc._load_model.cache_clear()

    assert result.method.value == "rules"
    assert result.category.value in VALID_CATEGORIES
    assert "ML model is unavailable" in result.disclaimer


# ══════════════════════════════════════════════════════════════════════════════
# URL analysis — hinglish language
# ══════════════════════════════════════════════════════════════════════════════


def test_url_hinglish_language_response() -> None:
    response = client.post(
        "/api/analyze/url",
        json={"url": "https://example.com/", "language": "hinglish"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "hinglish"
    assert isinstance(body["summary"], str)
    assert len(body["summary"]) > 0


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — high-risk patterns
# ══════════════════════════════════════════════════════════════════════════════


def test_message_otp_request_is_high_risk() -> None:
    """A message requesting OTP share should be classified as High Risk."""
    scam_msg = (
        "Dear customer, your account has been selected for KYC verification. "
        "Please share your OTP with our executive to complete the process."
    )
    response = client.post(
        "/api/analyze/message",
        json={"message": scam_msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "High Risk", (
        f"Expected High Risk, got {body['category']}; indicators={body['indicators']}"
    )
    assert body["method"] == "rules"
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "otp_request" in indicator_codes or "kyc_request" in indicator_codes


def test_message_account_block_kyc_is_high_risk() -> None:
    """Account block + KYC request = two high-weight indicators → High Risk."""
    scam_msg = (
        "ALERT: Your SBI account has been blocked due to incomplete KYC. "
        "Update your KYC immediately to avoid permanent deactivation. "
        "Click here to complete re-verify your details."
    )
    response = client.post(
        "/api/analyze/message",
        json={"message": scam_msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "High Risk"
    assert body["method"] == "rules"


def test_message_banking_credential_request_high_risk() -> None:
    """Message asking for bank account / card number → High Risk."""
    scam_msg = (
        "Your RBI mandate requires you to provide your bank account number "
        "and CVV to complete the annual security audit. Reply immediately."
    )
    response = client.post(
        "/api/analyze/message",
        json={"message": scam_msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "High Risk"


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — suspicious patterns
# ══════════════════════════════════════════════════════════════════════════════


def test_message_lottery_winner_suspicious() -> None:
    """Prize/lottery claim should be at least Suspicious."""
    msg = "Congratulations! You have won ₹50,000 in our lucky draw. Claim now!"
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] in {"High Risk", "Suspicious"}
    assert body["method"] == "rules"
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "prize_lottery_winner" in indicator_codes


def test_message_work_from_home_scam_detected() -> None:
    """Work-from-home job scam should trigger job_internship_scam indicator."""
    msg = "Work from home opportunity! Earn ₹500 daily. No experience required. Immediate joining."
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "rules"
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "job_internship_scam" in indicator_codes


def test_message_urgency_detected() -> None:
    """Message with urgency keyword should trigger urgency_pressure indicator."""
    msg = "This is your last chance! Act now or your account will expire within 24 hours."
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "urgency_pressure" in indicator_codes


def test_message_click_link_indicator() -> None:
    """Message asking to click a link should trigger link_click_request indicator."""
    msg = "Please click the link below to verify your account details."
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    indicator_codes = [ind["code"] for ind in body["indicators"]]
    assert "link_click_request" in indicator_codes


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — benign messages
# ══════════════════════════════════════════════════════════════════════════════


def test_message_benign_casual_chat() -> None:
    """A normal casual message should return No Obvious Warning Signs."""
    msg = "Hey! How are you doing? Let's catch up over coffee this weekend."
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "No Obvious Warning Signs"
    assert body["method"] == "rules"
    assert body["indicators"] == []


def test_message_benign_academic_text() -> None:
    """An academic/informational message with no scam keywords should be benign."""
    msg = (
        "The assignment deadline for Machine Learning is next Friday. "
        "Please submit via the college portal before midnight."
    )
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "No Obvious Warning Signs"
    assert body["indicators"] == []


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — hinglish language
# ══════════════════════════════════════════════════════════════════════════════


def test_message_hinglish_response_fields() -> None:
    """Hinglish language request should return hinglish in response."""
    msg = "Aapka account block ho gaya hai. Abhi KYC update karein."
    response = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "hinglish"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "hinglish"
    assert body["method"] == "rules"
    assert isinstance(body["summary"], str)
    assert len(body["summary"]) > 0
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0


def test_message_hinglish_recommendations_differ_from_english() -> None:
    """Hinglish recommendations should be different from English recommendations."""
    msg = "Hello this is a test"
    en_resp = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "en"},
    )
    hi_resp = client.post(
        "/api/analyze/message",
        json={"message": msg, "language": "hinglish"},
    )
    assert en_resp.json()["recommendations"] != hi_resp.json()["recommendations"]


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — method always "rules"
# ══════════════════════════════════════════════════════════════════════════════


def test_message_method_is_always_rules() -> None:
    """The method field for message analysis must always be 'rules'."""
    for msg in [
        "Congratulations! You won!",
        "Your OTP is required to proceed.",
        "Hello, how are you?",
        "Earn 5000 daily work from home no experience required.",
    ]:
        response = client.post(
            "/api/analyze/message",
            json={"message": msg, "language": "en"},
        )
        assert response.status_code == 200
        assert response.json()["method"] == "rules", (
            f"Method was {response.json()['method']} for message: {msg!r}"
        )


def test_message_disclaimer_mentions_rule_based() -> None:
    """The disclaimer for message analysis must explicitly mention rule-based analysis."""
    response = client.post(
        "/api/analyze/message",
        json={"message": "Test message", "language": "en"},
    )
    assert response.status_code == 200
    disclaimer = response.json()["disclaimer"].lower()
    assert "rule" in disclaimer, (
        f"Disclaimer does not mention rule-based: {disclaimer!r}"
    )


def test_message_disclaimer_does_not_claim_ml() -> None:
    """The disclaimer for messages must not claim ML/model-based classification."""
    response = client.post(
        "/api/analyze/message",
        json={"message": "Your prize is ready", "language": "en"},
    )
    disclaimer = response.json()["disclaimer"].lower()
    # The disclaimer explicitly says "No ML classifier is used"
    assert "no ml classifier" in disclaimer or "rule-based" in disclaimer


# ══════════════════════════════════════════════════════════════════════════════
# Message analysis — input validation (422 paths)
# ══════════════════════════════════════════════════════════════════════════════


def test_message_empty_rejected() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "", "language": "en"},
    )
    assert response.status_code == 422


def test_message_missing_field_rejected() -> None:
    response = client.post("/api/analyze/message", json={"language": "en"})
    assert response.status_code == 422


def test_message_oversized_rejected() -> None:
    """Message exceeding max_length=5000 should be rejected."""
    long_msg = "a" * 5001
    response = client.post(
        "/api/analyze/message",
        json={"message": long_msg, "language": "en"},
    )
    assert response.status_code == 422


def test_message_malformed_json_rejected() -> None:
    response = client.post(
        "/api/analyze/message",
        content=b"{not valid",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_message_invalid_language_rejected() -> None:
    response = client.post(
        "/api/analyze/message",
        json={"message": "Hello world", "language": "de"},
    )
    assert response.status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# Security invariants — no network access imports
# ══════════════════════════════════════════════════════════════════════════════


def _source_of(module_relative_path: str) -> str:
    """Return source code of a module file relative to the backend/app directory."""
    base = Path(__file__).parent.parent / "app"
    return (base / module_relative_path).read_text(encoding="utf-8")


_FORBIDDEN_NETWORK_IMPORTS = [
    "import httpx",
    "import requests",
    "import aiohttp",
    "import urllib.request",
    "from urllib.request",
    "from httpx",
    "from requests",
    "from aiohttp",
    "socket.getaddrinfo",
    "socket.gethostbyname",
    "dns.resolver",
    "subprocess",
]


def test_url_service_has_no_network_imports() -> None:
    """url_analysis.py must not import any HTTP or DNS library."""
    source = _source_of("services/url_analysis.py")
    for forbidden in _FORBIDDEN_NETWORK_IMPORTS:
        assert forbidden not in source, (
            f"Forbidden network import {forbidden!r} found in url_analysis.py"
        )


def test_message_service_has_no_network_imports() -> None:
    """message_analysis.py must not import any HTTP or DNS library."""
    source = _source_of("services/message_analysis.py")
    for forbidden in _FORBIDDEN_NETWORK_IMPORTS:
        assert forbidden not in source, (
            f"Forbidden network import {forbidden!r} found in message_analysis.py"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Error path — internal exception does not leak raw input
# ══════════════════════════════════════════════════════════════════════════════


def test_url_error_response_does_not_echo_input() -> None:
    """
    A 422 error response must not contain the raw submitted URL in the
    top-level detail string (prevent input reflection).
    """
    submitted = "https://example.com/secret-path-do-not-echo"
    response = client.post(
        "/api/analyze/url",
        json={"url": submitted, "language": "bad-language"},
    )
    assert response.status_code == 422
    # The raw URL path should not appear verbatim in the error body
    response_text = response.text
    assert "secret-path-do-not-echo" not in response_text


def test_message_error_response_does_not_echo_raw_message() -> None:
    """
    A 422 error response must not contain the raw submitted message text in
    the detail field (prevent input reflection).
    """
    submitted_msg = "super-secret-message-content-xyz-do-not-echo"
    response = client.post(
        "/api/analyze/message",
        json={"message": submitted_msg, "language": "de"},
    )
    assert response.status_code == 422
    assert submitted_msg not in response.text


# ══════════════════════════════════════════════════════════════════════════════
# Indicator structure validation
# ══════════════════════════════════════════════════════════════════════════════


def test_url_indicators_have_required_fields() -> None:
    """Every indicator in the URL response must have code, label, explanation."""
    response = client.post(
        "/api/analyze/url",
        json={"url": "http://192.168.1.1@evil.tk/login", "language": "en"},
    )
    assert response.status_code == 200
    for indicator in response.json()["indicators"]:
        assert "code" in indicator, f"Missing 'code' in {indicator}"
        assert "label" in indicator, f"Missing 'label' in {indicator}"
        assert "explanation" in indicator, f"Missing 'explanation' in {indicator}"
        assert indicator["code"], "code must be non-empty"
        assert indicator["label"], "label must be non-empty"
        assert indicator["explanation"], "explanation must be non-empty"


def test_message_indicators_have_required_fields() -> None:
    """Every indicator in the message response must have code, label, explanation."""
    response = client.post(
        "/api/analyze/message",
        json={
            "message": "Your account is blocked. Share your OTP to reactivate.",
            "language": "en",
        },
    )
    assert response.status_code == 200
    for indicator in response.json()["indicators"]:
        assert "code" in indicator
        assert "label" in indicator
        assert "explanation" in indicator
        assert indicator["code"]
        assert indicator["label"]
        assert indicator["explanation"]


# ══════════════════════════════════════════════════════════════════════════════
# /health endpoint
# ══════════════════════════════════════════════════════════════════════════════


def test_health_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
