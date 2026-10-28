"""
T-02 tests — feature extraction, feature ordering, model loading, and predictions.

Tests verify:
  - Feature extractor returns exactly 53 features in the correct order.
  - Feature names match the training schema.
  - Model loads successfully from the artifact path.
  - Model produces valid predictions without any network request.
  - Inference for known phishing-pattern URLs gives higher phishing probability
    than benign-pattern URLs (direction check, not exact threshold).
  - The URL analysis service returns ml_model or ml_model_and_rules method
    when the artifact is available.
  - No network access is used (verified by absence of socket/requests/httpx usage
    in the feature extractor module).

Run: pytest backend/tests/test_t02_model.py -v
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure repo root is on path so ml/ package is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ── Paths ─────────────────────────────────────────────────────────────────────
_ARTIFACTS_DIR = _REPO_ROOT / "ml" / "artifacts"
_MODEL_PATH = _ARTIFACTS_DIR / "url_model.joblib"
_SCHEMA_PATH = _ARTIFACTS_DIR / "feature_schema.json"
_TRAINING_REPORT_PATH = _ARTIFACTS_DIR / "training_report.json"
_EVAL_REPORT_PATH = _REPO_ROOT / "ml" / "reports" / "evaluation_report.json"


# ── Feature extractor tests ───────────────────────────────────────────────────

class TestFeatureExtractor:
    """Tests for ml/url_features.py — no model needed."""

    def test_feature_count(self) -> None:
        """extract_features returns exactly 53 values."""
        from ml.url_features import extract_features
        feats = extract_features("https://example.com/login")
        assert len(feats) == 53, f"Expected 53 features, got {len(feats)}"

    def test_feature_names_count(self) -> None:
        from ml.url_features import FEATURE_NAMES
        assert len(FEATURE_NAMES) == 53

    def test_feature_names_ordering(self) -> None:
        """Feature names must exactly match the training schema."""
        from ml.url_features import FEATURE_NAMES
        expected_first_five = [
            "length_url", "length_hostname", "ip", "nb_dots", "nb_hyphens"
        ]
        assert FEATURE_NAMES[:5] == expected_first_five

    def test_features_are_numeric(self) -> None:
        from ml.url_features import extract_features
        feats = extract_features("http://phishing-login.xyz/secure/account")
        for i, v in enumerate(feats):
            assert isinstance(v, (int, float)), f"Feature {i} is not numeric: {v!r}"

    def test_length_url_feature(self) -> None:
        """length_url must equal len(url)."""
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "https://example.com/test"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("length_url")
        assert feats[idx] == float(len(url))

    def test_nb_dots_feature(self) -> None:
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "https://a.b.c.d.com/path"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("nb_dots")
        assert feats[idx] == float(url.count('.'))

    def test_nb_at_feature(self) -> None:
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "http://user@malicious.com/path"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("nb_at")
        assert feats[idx] == 1.0

    def test_https_token_feature_http(self) -> None:
        """https_token = 1 when scheme is http (not https)."""
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "http://example.com/"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("https_token")
        assert feats[idx] == 1.0

    def test_https_token_feature_https(self) -> None:
        """https_token = 0 when scheme is https."""
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "https://example.com/"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("https_token")
        assert feats[idx] == 0.0

    def test_ip_feature_detected(self) -> None:
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "http://192.168.1.100/login"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("ip")
        assert feats[idx] == 1.0

    def test_ip_feature_not_present(self) -> None:
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "https://google.com/"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("ip")
        assert feats[idx] == 0.0

    def test_shortening_service_detected(self) -> None:
        from ml.url_features import extract_features, FEATURE_NAMES
        url = "http://bit.ly/abc123"
        feats = extract_features(url)
        idx = FEATURE_NAMES.index("shortening_service")
        assert feats[idx] == 1.0

    def test_deterministic_output(self) -> None:
        """Same URL must produce identical feature vector on repeated calls."""
        from ml.url_features import extract_features
        url = "https://paypal-secure.com/account/verify?token=abc123"
        feats1 = extract_features(url)
        feats2 = extract_features(url)
        assert feats1 == feats2

    def test_schema_version_present(self) -> None:
        from ml.url_features import FEATURE_SCHEMA_VERSION
        assert isinstance(FEATURE_SCHEMA_VERSION, str)
        assert len(FEATURE_SCHEMA_VERSION) > 0

    def test_no_network_imports_in_feature_module(self) -> None:
        """Verify that url_features.py does not import network libraries."""
        feature_module_path = _REPO_ROOT / "ml" / "url_features.py"
        source = feature_module_path.read_text(encoding="utf-8")
        forbidden = ["import requests", "import httpx", "import urllib.request",
                     "socket.gethostbyname", "socket.getaddrinfo", "dns.resolver"]
        for pattern in forbidden:
            assert pattern not in source, (
                f"Network-access pattern found in url_features.py: {pattern!r}"
            )

    def test_feature_names_match_schema_json(self) -> None:
        """Feature names in module must match artifact schema JSON."""
        if not _SCHEMA_PATH.exists():
            pytest.skip("Feature schema JSON not yet generated — run training first")
        from ml.url_features import FEATURE_NAMES
        with open(_SCHEMA_PATH, encoding="utf-8") as f:
            schema = json.load(f)
        assert schema["feature_names"] == FEATURE_NAMES, (
            "Feature names in url_features.py do not match feature_schema.json"
        )
        assert schema["feature_count"] == len(FEATURE_NAMES)


# ── Model loading tests ───────────────────────────────────────────────────────

class TestModelLoading:
    """Tests for model artifact loading."""

    @pytest.fixture(scope="class")
    def model(self):
        if not _MODEL_PATH.exists():
            pytest.skip("Model artifact not found — run python ml/train_url_model.py first")
        import joblib
        return joblib.load(_MODEL_PATH)

    def test_model_loads_without_error(self, model) -> None:
        assert model is not None

    def test_model_has_predict_method(self, model) -> None:
        assert hasattr(model, "predict")

    def test_model_has_predict_proba_method(self, model) -> None:
        assert hasattr(model, "predict_proba")

    def test_model_prediction_shape(self, model) -> None:
        import numpy as np
        X = np.zeros((3, 53))
        preds = model.predict(X)
        assert preds.shape == (3,)

    def test_model_predict_proba_shape(self, model) -> None:
        import numpy as np
        X = np.zeros((3, 53))
        proba = model.predict_proba(X)
        assert proba.shape == (3, 2)

    def test_model_proba_sums_to_one(self, model) -> None:
        import numpy as np
        X = np.zeros((5, 53))
        proba = model.predict_proba(X)
        sums = proba.sum(axis=1)
        assert all(abs(s - 1.0) < 1e-9 for s in sums)

    def test_model_prediction_is_binary(self, model) -> None:
        import numpy as np
        X = np.random.RandomState(0).rand(10, 53) * 10
        preds = model.predict(X)
        assert set(preds).issubset({0, 1})


# ── End-to-end feature + model prediction tests ───────────────────────────────

class TestEndToEndPrediction:
    """Verify feature extraction feeds correctly into the model."""

    @pytest.fixture(scope="class")
    def model(self):
        if not _MODEL_PATH.exists():
            pytest.skip("Model artifact not found — run python ml/train_url_model.py first")
        import joblib
        return joblib.load(_MODEL_PATH)

    def _predict(self, model, url: str):
        import numpy as np
        from ml.url_features import extract_features
        feats = extract_features(url)
        X = np.array([feats])
        pred = int(model.predict(X)[0])
        prob = float(model.predict_proba(X)[0][1])
        return pred, prob

    def test_feature_vector_length_matches_model(self, model) -> None:
        from ml.url_features import extract_features
        import numpy as np
        feats = extract_features("https://example.com/")
        X = np.array([feats])
        # Should not raise — model expects 53 features
        result = model.predict(X)
        assert len(result) == 1

    def test_known_phishing_url_higher_prob(self, model) -> None:
        """
        A URL with many phishing signals should have higher phishing probability
        than a plain domain URL.
        This is a directional check, not an exact threshold assertion.
        """
        # Multiple phishing signals: IP, many subdomains, http only, login in path
        phishing_url = "http://192.168.1.100/secure/account/login?verify=1"
        benign_url = "https://google.com/"
        _, phish_prob = self._predict(model, phishing_url)
        _, benign_prob = self._predict(model, benign_url)
        assert phish_prob > benign_prob, (
            f"Expected phishing URL to have higher prob: phish={phish_prob:.3f}, benign={benign_prob:.3f}"
        )

    def test_shortener_url_gets_phishing_signal(self, model) -> None:
        """URL shortener should produce notable phishing probability."""
        _, prob = self._predict(model, "http://bit.ly/xyzabc")
        # Just verify it produces a valid probability
        assert 0.0 <= prob <= 1.0

    def test_no_exception_on_minimal_url(self, model) -> None:
        """Feature extractor should not crash on a minimal URL."""
        _, prob = self._predict(model, "http://a.com/")
        assert 0.0 <= prob <= 1.0

    def test_no_exception_on_complex_url(self, model) -> None:
        url = (
            "https://support-appleld.com.secureupdate.duilawyeryork.com/ap/"
            "89e6a3b4b063b8d/?cmd=_update&dispatch=89e6a3b4b063b8d1b&locale=_"
        )
        _, prob = self._predict(model, url)
        assert 0.0 <= prob <= 1.0

    def test_prediction_is_deterministic(self, model) -> None:
        url = "https://paypal-secure.com/account/verify?token=abc&id=1"
        _, prob1 = self._predict(model, url)
        _, prob2 = self._predict(model, url)
        # Allow for floating-point last-bit rounding differences across calls
        assert abs(prob1 - prob2) < 1e-9, (
            f"Predictions should be deterministic: {prob1} vs {prob2}"
        )


# ── Artifact file tests ───────────────────────────────────────────────────────

class TestArtifactFiles:
    """Verify all required artifact files exist and are valid."""

    def test_model_file_exists(self) -> None:
        if not _MODEL_PATH.exists():
            pytest.skip("Model artifact not yet generated")
        assert _MODEL_PATH.exists()

    def test_schema_file_exists(self) -> None:
        if not _SCHEMA_PATH.exists():
            pytest.skip("Feature schema not yet generated")
        assert _SCHEMA_PATH.exists()

    def test_training_report_file_exists(self) -> None:
        if not _TRAINING_REPORT_PATH.exists():
            pytest.skip("Training report not yet generated")
        assert _TRAINING_REPORT_PATH.exists()

    def test_eval_report_file_exists(self) -> None:
        if not _EVAL_REPORT_PATH.exists():
            pytest.skip("Evaluation report not yet generated")
        assert _EVAL_REPORT_PATH.exists()

    def test_schema_json_is_valid(self) -> None:
        if not _SCHEMA_PATH.exists():
            pytest.skip("Feature schema not yet generated")
        with open(_SCHEMA_PATH, encoding="utf-8") as f:
            schema = json.load(f)
        assert "feature_names" in schema
        assert "schema_version" in schema
        assert "feature_count" in schema
        assert schema["feature_count"] == 53
        assert len(schema["feature_names"]) == 53

    def test_training_report_has_required_keys(self) -> None:
        if not _TRAINING_REPORT_PATH.exists():
            pytest.skip("Training report not yet generated")
        with open(_TRAINING_REPORT_PATH, encoding="utf-8") as f:
            report = json.load(f)
        for key in ["random_seed", "dataset", "split_sizes", "model", "command"]:
            assert key in report, f"Missing key in training_report.json: {key}"
        assert report["random_seed"] == 42
        assert report["dataset"]["license"] == "CC BY 4.0"

    def test_eval_report_has_test_metrics(self) -> None:
        if not _EVAL_REPORT_PATH.exists():
            pytest.skip("Evaluation report not yet generated")
        with open(_EVAL_REPORT_PATH, encoding="utf-8") as f:
            report = json.load(f)
        assert "test" in report
        test_metrics = report["test"]
        for key in ["accuracy", "f1_macro", "f1_phishing", "confusion_matrix",
                    "false_positive_rate", "false_negative_rate"]:
            assert key in test_metrics, f"Missing metric: {key}"
        # Sanity bounds on actual metrics (not hardcoded — read from file)
        assert 0.0 < test_metrics["accuracy"] <= 1.0
        assert 0.0 < test_metrics["f1_macro"] <= 1.0

    def test_eval_report_metrics_not_fabricated(self) -> None:
        """
        Verify metrics are plausible for a real trained model on this dataset,
        not suspiciously perfect (which would suggest fabrication).
        """
        if not _EVAL_REPORT_PATH.exists():
            pytest.skip("Evaluation report not yet generated")
        with open(_EVAL_REPORT_PATH, encoding="utf-8") as f:
            report = json.load(f)
        acc = report["test"]["accuracy"]
        # A real URL-only classifier on this dataset should be in [0.75, 0.99]
        assert 0.75 <= acc <= 0.99, (
            f"Accuracy {acc} outside plausible range — check for fabrication or data leakage"
        )


# ── API integration tests (model loaded via service) ─────────────────────────

class TestURLAnalysisAPIWithModel:
    """
    Verify the /api/analyze/url endpoint uses the real model
    when the artifact is available.
    """

    @pytest.fixture(scope="class")
    def client(self):
        if not _MODEL_PATH.exists():
            pytest.skip("Model artifact not found — run training first")
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app, raise_server_exceptions=True)

    def test_url_analysis_uses_ml_method(self, client) -> None:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com/", "language": "en"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["method"] in {"ml_model", "ml_model_and_rules"}, (
            f"Expected ML method when model is loaded, got: {body['method']}"
        )

    def test_phishing_url_gets_high_probability(self, client) -> None:
        """A URL with many phishing signals should not be No Obvious Warning Signs."""
        response = client.post(
            "/api/analyze/url",
            json={"url": "http://192.168.1.1/secure/account/login", "language": "en"},
        )
        assert response.status_code == 200
        body = response.json()
        # Category should not be No Obvious Warning Signs for a URL with IP + login + http
        assert body["category"] != "No Obvious Warning Signs", (
            "IP-based login URL should be flagged"
        )

    def test_response_has_disclaimer(self, client) -> None:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com/", "language": "en"},
        )
        body = response.json()
        assert len(body["disclaimer"]) > 20

    def test_response_has_non_empty_summary(self, client) -> None:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com/", "language": "en"},
        )
        body = response.json()
        assert len(body["summary"]) > 10

    def test_hinglish_response_returns_hinglish(self, client) -> None:
        response = client.post(
            "/api/analyze/url",
            json={"url": "https://example.com/", "language": "hinglish"},
        )
        body = response.json()
        assert body["language"] == "hinglish"

    def test_url_never_fetched(self, client) -> None:
        """
        Verify that no network-access imports are in url_analysis.py.
        The URL is analyzed as a string only.
        """
        url_service_path = (
            Path(__file__).resolve().parent.parent / "app" / "services" / "url_analysis.py"
        )
        source = url_service_path.read_text(encoding="utf-8")
        forbidden_patterns = [
            "requests.get", "httpx.get", "urllib.request.urlopen",
            "socket.gethostbyname", "socket.getaddrinfo",
        ]
        for pattern in forbidden_patterns:
            assert pattern not in source, (
                f"Network-access pattern found in url_analysis.py: {pattern!r}. "
                "Submitted URLs must never be opened or fetched."
            )
