"""
URL analysis service — T-02/T-03 implementation.

Uses the trained RandomForest model from ml/artifacts/url_model.joblib.
Falls back to rule-based analysis with explicit disclosure if the model
artifact is unavailable.

INVARIANTS (never violated):
  - The submitted URL is NEVER opened, fetched, resolved, or previewed.
  - No DNS lookups, WHOIS queries, or HTTP requests are made.
  - Raw user input is never stored or logged.
"""

from __future__ import annotations

import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Artifact paths ────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_DEFAULT_MODEL_PATH = _REPO_ROOT / "ml" / "artifacts" / "url_model.joblib"
_DEFAULT_SCHEMA_PATH = _REPO_ROOT / "ml" / "artifacts" / "feature_schema.json"
_FEATURE_MODULE_PATH = _REPO_ROOT / "ml"

# Ensure ml/ is on sys.path for the feature extractor
if str(_FEATURE_MODULE_PATH) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.schemas import (
    AnalysisMethod,
    Indicator,
    Language,
    RiskCategory,
    UrlAnalysisResponse,
)

_DISCLAIMER = (
    "This assessment is produced by automated analysis of URL structure only "
    "and can be wrong. It does not guarantee that a URL is safe or unsafe. "
    "Always verify through official channels independently. "
    "A low-risk result is not a safety guarantee."
)

_RECOMMENDATIONS = [
    "Do not click the link until you have verified it independently.",
    "Search for the organisation's official website using a trusted search engine.",
    "If you received this URL unexpectedly, treat it with extra caution.",
    "When in doubt, contact the organisation directly through a known official channel.",
]


# ── Model loader (loaded once at startup) ─────────────────────────────────────

class _ModelBundle:
    """Holds the loaded model pipeline and feature schema."""
    def __init__(self, pipeline, feature_names: list[str], schema_version: str) -> None:
        self.pipeline = pipeline
        self.feature_names = feature_names
        self.schema_version = schema_version
        self.n_features = len(feature_names)


@lru_cache(maxsize=1)
def _load_model(model_path: str) -> Optional[_ModelBundle]:
    """
    Load the trained model pipeline and feature schema.
    Returns None if the artifact is unavailable (graceful fallback).
    """
    import json

    path = Path(model_path)
    schema_path = Path(model_path).parent / "feature_schema.json"

    if not path.exists():
        logger.warning("Model artifact not found at %s — using rules fallback.", path)
        return None

    try:
        import joblib
        pipeline = joblib.load(path)
    except Exception as exc:
        logger.error("Failed to load model from %s: %s", path, exc)
        return None

    feature_names: list[str] = []
    schema_version = "unknown"
    if schema_path.exists():
        try:
            with open(schema_path, encoding="utf-8") as f:
                schema = json.load(f)
            feature_names = schema.get("feature_names", [])
            schema_version = schema.get("schema_version", "unknown")
        except Exception as exc:
            logger.error("Failed to read feature schema: %s", exc)

    logger.info(
        "Loaded URL model from %s (schema v%s, %d features)",
        path, schema_version, len(feature_names),
    )
    return _ModelBundle(pipeline, feature_names, schema_version)


# ── Feature extraction ────────────────────────────────────────────────────────

def _extract_url_features(url: str) -> Optional[list[float]]:
    """Extract features using ml/url_features.py. Returns None on failure."""
    try:
        from ml.url_features import extract_features
        return extract_features(url)
    except Exception as exc:
        logger.error("Feature extraction failed: %s", exc)
        return None


# ── Risk indicators from URL string ──────────────────────────────────────────

def _detect_rule_indicators(url: str) -> list[Indicator]:
    """
    Detect URL-string-based warning indicators without any network request.
    Used as supplementary information alongside the ML prediction,
    and as the sole method when the model is unavailable.
    """
    from urllib.parse import urlparse
    import re

    indicators: list[Indicator] = []

    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path or ""
        scheme = parsed.scheme or ""
    except Exception:
        return indicators

    # IP address in hostname
    ip_pattern = re.compile(
        r'\b(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])\b'
    )
    if ip_pattern.search(hostname):
        indicators.append(Indicator(
            code="ip_in_hostname",
            label="IP address used instead of domain name",
            explanation=(
                "The URL uses a numeric IP address instead of a regular website name. "
                "Legitimate services rarely ask you to visit a raw IP address."
            ),
        ))

    # @ symbol in URL
    if '@' in url:
        indicators.append(Indicator(
            code="at_symbol_in_url",
            label="@ symbol found in URL",
            explanation=(
                "The @ symbol in a URL can redirect your browser to a different address "
                "than what appears before the @. This is a common trick in phishing links."
            ),
        ))

    # URL shortening service
    shorteners = [
        'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'tiny.cc',
        'is.gd', 'tr.im', 'adf.ly', 'bitly.com', 'cutt.us',
    ]
    if any(s in url.lower() for s in shorteners):
        indicators.append(Indicator(
            code="url_shortener",
            label="URL shortening service detected",
            explanation=(
                "This URL uses a link-shortening service that hides the real destination. "
                "You cannot see where the link actually leads without following it."
            ),
        ))

    # HTTP (not HTTPS)
    if scheme == 'http':
        indicators.append(Indicator(
            code="no_https",
            label="Not using HTTPS",
            explanation=(
                "This URL uses HTTP instead of HTTPS, meaning the connection is not "
                "encrypted. However, note that HTTPS alone does not make a site safe — "
                "phishing sites can also use HTTPS."
            ),
        ))

    # Suspicious TLD
    suspicious_tlds = {
        'tk', 'ml', 'ga', 'cf', 'gq', 'xyz', 'top', 'work', 'date', 'wang',
        'men', 'icu', 'online', 'click', 'faith', 'zip', 'cricket', 'win',
    }
    tld = hostname.split('.')[-1] if '.' in hostname else ''
    if tld in suspicious_tlds:
        indicators.append(Indicator(
            code="suspicious_tld",
            label=f"Suspicious top-level domain (.{tld})",
            explanation=(
                f"The .{tld} domain extension is frequently associated with free or "
                "low-cost domains used in phishing and spam campaigns."
            ),
        ))

    # Excessive subdomains
    dot_count = hostname.count('.')
    if dot_count >= 3:
        indicators.append(Indicator(
            code="many_subdomains",
            label="Many subdomains (possible brand impersonation)",
            explanation=(
                "The URL has many subdomain levels. Phishing sites sometimes add "
                "a trusted brand name as a subdomain (e.g., paypal.evil.com) to "
                "make the URL look legitimate at a quick glance."
            ),
        ))

    # Hyphen in domain (prefix-suffix attack)
    domain_part = hostname.split('.')[0] if hostname else ''
    if '-' in domain_part:
        indicators.append(Indicator(
            code="hyphen_in_domain",
            label="Hyphen in domain name",
            explanation=(
                "Legitimate organisations rarely use hyphens in their main domain name. "
                "Hyphens can be used to imitate well-known brands (e.g., paypal-secure.com)."
            ),
        ))

    # Suspicious path keywords
    phish_hints = ['login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm', 'password', 'credential']
    found_hints = [h for h in phish_hints if h in path.lower()]
    if found_hints:
        indicators.append(Indicator(
            code="phishing_keywords_in_path",
            label="Phishing-related keywords in path",
            explanation=(
                f"The URL path contains words like {', '.join(found_hints[:3])}, "
                "which are commonly found in phishing pages designed to steal "
                "login credentials or personal information."
            ),
        ))

    # Punycode / IDN homoglyph
    if 'xn--' in url.lower():
        indicators.append(Indicator(
            code="punycode_domain",
            label="Internationalised domain (punycode detected)",
            explanation=(
                "This URL uses an internationalised domain name. Attackers sometimes "
                "use characters from other scripts that look similar to English letters "
                "to create fake versions of trusted websites."
            ),
        ))

    return indicators


# ── Category mapping ──────────────────────────────────────────────────────────

def _map_probability_to_category(phishing_prob: float, rule_count: int) -> RiskCategory:
    """
    Map model probability to risk category.
    Thresholds are conservative — err toward caution.
    """
    if phishing_prob >= 0.75:
        return RiskCategory.high_risk
    elif phishing_prob >= 0.45:
        return RiskCategory.suspicious
    elif phishing_prob >= 0.25 or rule_count >= 2:
        return RiskCategory.suspicious
    else:
        return RiskCategory.no_obvious_warning_signs


def _rules_only_category(rule_count: int) -> RiskCategory:
    if rule_count >= 3:
        return RiskCategory.high_risk
    elif rule_count >= 1:
        return RiskCategory.suspicious
    else:
        return RiskCategory.no_obvious_warning_signs


# ── Summary text ──────────────────────────────────────────────────────────────

_SUMMARIES = {
    (RiskCategory.high_risk, Language.en): (
        "Multiple indicators suggest this URL may be associated with phishing or fraud. "
        "Exercise strong caution and do not enter any credentials or personal information."
    ),
    (RiskCategory.high_risk, Language.hinglish): (
        "Is URL mein kai suspicious indicators hain jo phishing ya fraud ka sanket dete hain. "
        "Kripya koi bhi password ya personal information enter mat karein."
    ),
    (RiskCategory.suspicious, Language.en): (
        "This URL has some indicators that warrant caution. "
        "Verify the source independently before clicking or entering any information."
    ),
    (RiskCategory.suspicious, Language.hinglish): (
        "Is URL mein kuch suspicious indicators hain. "
        "Kisi bhi link par click karne se pehle source ko verify karein."
    ),
    (RiskCategory.no_obvious_warning_signs, Language.en): (
        "No obvious warning signs were detected in this URL's structure. "
        "This is not a guarantee of safety — phishing sites can look legitimate."
    ),
    (RiskCategory.no_obvious_warning_signs, Language.hinglish): (
        "Is URL ki structure mein koi obvious warning signs nahi mile. "
        "Lekin yeh safety ki guarantee nahi hai — phishing sites bhi legitimate lag sakti hain."
    ),
    (RiskCategory.unable_to_assess, Language.en): (
        "The URL could not be assessed. Please check that the input is a valid URL."
    ),
    (RiskCategory.unable_to_assess, Language.hinglish): (
        "URL assess nahi ho saka. Kripya check karein ki input ek valid URL hai."
    ),
}


def _get_summary(category: RiskCategory, language: Language) -> str:
    return _SUMMARIES.get((category, language), _SUMMARIES.get((category, Language.en), ""))


# ── Main analysis function ─────────────────────────────────────────────────────

def analyze_url(url: str, language: Language) -> UrlAnalysisResponse:
    """
    Analyze a URL string using local features only.

    The URL is NEVER opened, fetched, resolved, or previewed.
    Uses the trained ML model when available; falls back to rules with disclosure.
    """
    from app.config import get_settings
    import numpy as np

    settings = get_settings()
    model_bundle = _load_model(settings.model_path)

    # Always compute rule-based indicators (supplementary)
    rule_indicators = _detect_rule_indicators(url)

    if model_bundle is not None:
        # ── ML prediction path ─────────────────────────────────────────────────
        features = _extract_url_features(url)

        if features is not None and len(features) == model_bundle.n_features:
            X = np.array([features])
            try:
                pred = int(model_bundle.pipeline.predict(X)[0])
                proba = model_bundle.pipeline.predict_proba(X)[0]
                phishing_prob = float(proba[1])  # probability of phishing class

                category = _map_probability_to_category(phishing_prob, len(rule_indicators))
                method = AnalysisMethod.ml_model_and_rules if rule_indicators else AnalysisMethod.ml_model

                # Add a model score indicator
                all_indicators = list(rule_indicators)
                if phishing_prob >= 0.5:
                    all_indicators.insert(0, Indicator(
                        code="ml_phishing_signal",
                        label="ML model flagged phishing patterns",
                        explanation=(
                            f"The trained classifier assigned a {phishing_prob:.0%} probability "
                            "of phishing based on URL structure features. "
                            "This is based on patterns learned from a labelled dataset "
                            "and may not reflect current phishing techniques."
                        ),
                    ))
                elif phishing_prob >= 0.25:
                    all_indicators.insert(0, Indicator(
                        code="ml_borderline_signal",
                        label="ML model found some phishing patterns",
                        explanation=(
                            f"The trained classifier assigned a {phishing_prob:.0%} probability "
                            "of phishing — in an uncertain range. Exercise normal caution."
                        ),
                    ))

                return UrlAnalysisResponse(
                    category=category,
                    method=method,
                    indicators=all_indicators,
                    summary=_get_summary(category, language),
                    recommendations=_RECOMMENDATIONS,
                    disclaimer=_DISCLAIMER,
                    language=language,
                )
            except Exception as exc:
                logger.error("Model prediction failed: %s", exc)
                # Fall through to rules

    # ── Rules-only fallback ────────────────────────────────────────────────────
    # Model was unavailable (None) or prediction failed (fell through).
    # Use rule-based category; never mark unable_to_assess unless the URL
    # could not be parsed at all (rule_indicators raised an exception).
    category = _rules_only_category(len(rule_indicators))

    disclaimer = _DISCLAIMER
    if model_bundle is None:
        disclaimer = (
            _DISCLAIMER + " Note: ML model is unavailable; this result is based on "
            "deterministic rule checks only."
        )

    return UrlAnalysisResponse(
        category=category,
        method=AnalysisMethod.rules,
        indicators=rule_indicators,
        summary=_get_summary(category, language),
        recommendations=_RECOMMENDATIONS,
        disclaimer=disclaimer,
        language=language,
    )
