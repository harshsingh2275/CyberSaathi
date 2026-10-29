"""
End-to-End Smoke Tests for CyberSaathi AI (T-06).

Simulates realistic real-world student workflows:
  - Benign academic & official URLs
  - Realistic banking/phishing and scholarship scam URLs
  - URL shortening services
  - Benign student messages vs. urgent job/internship & OTP scam messages
  - Dual-language support (English and Hinglish)
  - Security headers, CORS enforcement, and error isolation
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ══════════════════════════════════════════════════════════════════════════════
# 1. Health and Liveness Smoke
# ══════════════════════════════════════════════════════════════════════════════


def test_smoke_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"


# ══════════════════════════════════════════════════════════════════════════════
# 2. URL Analysis Realistic Workflows
# ══════════════════════════════════════════════════════════════════════════════


def test_smoke_benign_academic_url() -> None:
    """A standard HTTPS academic/portal URL should be evaluated cleanly."""
    url = "https://www.aicte-india.org/initiatives/internship"
    response = client.post("/api/analyze/url", json={"url": url, "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] in ["No Obvious Warning Signs", "Suspicious"]
    assert "method" in data
    assert isinstance(data["indicators"], list)
    assert len(data["recommendations"]) >= 1
    assert "This assessment is produced by" in data["disclaimer"]
    assert data["language"] == "en"


def test_smoke_phishing_banking_url() -> None:
    """A classic phishing URL imitating banking login over plain HTTP."""
    url = "http://sbi-card-verification.net/update-kyc.php?token=9928"
    response = client.post("/api/analyze/url", json={"url": url, "language": "en"})
    assert response.status_code == 200
    data = response.json()
    # Should be flagged as Suspicious or High Risk
    assert data["category"] in ["Suspicious", "High Risk"]
    indicator_codes = [ind["code"] for ind in data["indicators"]]
    # Rule indicators should detect missing https, hyphen domain, or keywords
    assert "no_https" in indicator_codes
    assert any(c in indicator_codes for c in ["hyphen_in_domain", "phishing_keywords_in_path", "ml_phishing_signal"])


def test_smoke_url_shortener_flagged() -> None:
    """Link shorteners hide the destination and must be flagged as suspicious."""
    url = "http://bit.ly/student-free-laptop"
    response = client.post("/api/analyze/url", json={"url": url})
    assert response.status_code == 200
    data = response.json()
    indicator_codes = [ind["code"] for ind in data["indicators"]]
    assert "url_shortener" in indicator_codes


def test_smoke_url_hinglish_workflow() -> None:
    """Verify Hinglish explanations and summaries for URL analysis."""
    url = "http://fake-internship-portal.xyz/apply"
    response = client.post("/api/analyze/url", json={"url": url, "language": "hinglish"})
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hinglish"
    assert any(keyword in data["summary"].lower() for keyword in ["url", "mein", "phishing", "indicators", "karein"])


# ══════════════════════════════════════════════════════════════════════════════
# 3. Message Analysis Realistic Workflows
# ══════════════════════════════════════════════════════════════════════════════


def test_smoke_benign_student_chat() -> None:
    """A regular message between students should trigger no indicators."""
    msg = "Hi team, please find the slides for our DBMS lab presentation attached. See you tomorrow!"
    response = client.post("/api/analyze/message", json={"message": msg, "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "No Obvious Warning Signs"
    assert data["method"] == "rules"
    assert len(data["indicators"]) == 0


def test_smoke_fake_job_internship_scam() -> None:
    """A classic work-from-home scam targeting college students."""
    msg = (
        "Congratulations! Work from home part-time job offer. "
        "Earn 5000 daily income with no experience required. Immediate joining! "
        "Pay 500 registration fee to book your seat. Click here to apply: http://bit.ly/job123"
    )
    response = client.post("/api/analyze/message", json={"message": msg, "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "High Risk"
    assert data["method"] == "rules"
    indicator_codes = [ind["code"] for ind in data["indicators"]]
    assert "job_internship_scam" in indicator_codes
    assert "upfront_payment" in indicator_codes
    assert "link_click_request" in indicator_codes


def test_smoke_urgent_bank_kyc_threat_message() -> None:
    """An urgent message threatening account suspension to steal OTP/credentials."""
    msg = (
        "URGENT: Your SBI account has been suspended due to pending KYC verification. "
        "Please provide your Aadhaar number and OTP immediately to avoid permanent deactivation."
    )
    response = client.post("/api/analyze/message", json={"message": msg, "language": "en"})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "High Risk"
    assert data["method"] == "rules"
    indicator_codes = [ind["code"] for ind in data["indicators"]]
    assert "account_block_threat" in indicator_codes
    assert "kyc_request" in indicator_codes
    assert "otp_request" in indicator_codes
    assert "urgency_pressure" in indicator_codes


def test_smoke_message_hinglish_workflow() -> None:
    """Verify Hinglish explanations, recommendations, and summaries for messages."""
    msg = "Aapka account block ho gaya hai. Turant KYC update karein aur OTP share karein."
    response = client.post("/api/analyze/message", json={"message": msg, "language": "hinglish"})
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hinglish"
    assert data["category"] == "High Risk"
    # Verify Hinglish recommendations
    assert any("karein" in rec.lower() or "mat" in rec.lower() for rec in data["recommendations"])
    # Verify Hinglish indicator explanations
    for ind in data["indicators"]:
        assert any(word in ind["explanation"].lower() for word in ["mein", "hai", "nahi", "karein", "ka"])


# ══════════════════════════════════════════════════════════════════════════════
# 4. Error and Boundary Smoke
# ══════════════════════════════════════════════════════════════════════════════


def test_smoke_empty_and_whitespace_inputs_rejected() -> None:
    """Empty and whitespace inputs return 422 across both routes."""
    assert client.post("/api/analyze/url", json={"url": ""}).status_code == 422
    assert client.post("/api/analyze/url", json={"url": "   "}).status_code == 422
    assert client.post("/api/analyze/message", json={"message": ""}).status_code == 422
    assert client.post("/api/analyze/message", json={"message": "   "}).status_code == 422


def test_smoke_method_not_allowed() -> None:
    """GET on POST-only analysis routes returns 405 Method Not Allowed."""
    assert client.get("/api/analyze/url").status_code == 405
    assert client.get("/api/analyze/message").status_code == 405


def test_smoke_not_found() -> None:
    """Non-existent route returns 404."""
    assert client.get("/non-existent-endpoint").status_code == 404
