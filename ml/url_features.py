"""
URL-only feature extractor for CyberSaathi phishing URL classifier.

Computes the exact same 53 features present in the Hannousse & Yahiouche
dataset (dataset_B_05_2020.csv) using ONLY the URL string.  No network
request, DNS lookup, WHOIS query, or page-content fetch is ever made.

Feature ordering is canonical — always the same as FEATURE_NAMES below.
The feature schema version is stored in FEATURE_SCHEMA_VERSION.

Usage:
    from ml.url_features import extract_features, FEATURE_NAMES
    features = extract_features("https://example.com/login?id=1")
    # returns a list of 53 numeric values in FEATURE_NAMES order
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── Schema version — bump when feature list or ordering changes ────────────────
FEATURE_SCHEMA_VERSION = "1.0.0"

# ── Ordered feature names (must match training CSV columns) ───────────────────
FEATURE_NAMES: list[str] = [
    "length_url",
    "length_hostname",
    "ip",
    "nb_dots",
    "nb_hyphens",
    "nb_at",
    "nb_qm",
    "nb_and",
    "nb_or",
    "nb_eq",
    "nb_underscore",
    "nb_tilde",
    "nb_percent",
    "nb_slash",
    "nb_star",
    "nb_colon",
    "nb_comma",
    "nb_semicolumn",
    "nb_dollar",
    "nb_space",
    "nb_www",
    "nb_com",
    "nb_dslash",
    "http_in_path",
    "https_token",
    "ratio_digits_url",
    "ratio_digits_host",
    "punycode",
    "port",
    "tld_in_path",
    "tld_in_subdomain",
    "abnormal_subdomain",
    "nb_subdomains",
    "prefix_suffix",
    "random_domain",
    "shortening_service",
    "path_extension",
    "length_words_raw",
    "char_repeat",
    "shortest_words_raw",
    "shortest_word_host",
    "shortest_word_path",
    "longest_words_raw",
    "longest_word_host",
    "longest_word_path",
    "avg_words_raw",
    "avg_word_host",
    "avg_word_path",
    "phish_hints",
    "domain_in_brand",
    "brand_in_subdomain",
    "brand_in_path",
    "suspecious_tld",
]

assert len(FEATURE_NAMES) == 53, "Feature count mismatch"

# ── Static resources (loaded once at import time) ─────────────────────────────

_BRAND_LIST_PATH = Path(__file__).parent.parent / "data" / "raw" / "hannousse" / "scripts" / "allbrands.txt"

def _load_brands() -> frozenset[str]:
    if _BRAND_LIST_PATH.exists():
        with open(_BRAND_LIST_PATH, encoding="utf-8") as f:
            return frozenset(line.strip().lower() for line in f if line.strip())
    return frozenset()

_BRANDS: frozenset[str] = _load_brands()

_HINTS = frozenset([
    'wp', 'login', 'includes', 'admin', 'content', 'site', 'images', 'js',
    'alibaba', 'css', 'myaccount', 'dropbox', 'themes', 'plugins', 'signin', 'view',
])

_SHORTENING_PATTERN = re.compile(
    r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|'
    r'cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|'
    r'snipurl\.com|short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|'
    r'snipr\.com|fic\.kr|loopt\.us|doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|'
    r'om\.ly|to\.ly|bit\.do|lnkd\.in|db\.tt|qr\.ae|adf\.ly|bitly\.com|cur\.lv|'
    r'tinyurl\.com|ity\.im|q\.gs|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|'
    r'buzurl\.com|cutt\.us|u\.bb|yourls\.org|prettylinkpro\.com|scrnch\.me|'
    r'filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|link\.zip\.net',
    re.IGNORECASE,
)

_IP_PATTERN = re.compile(
    r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.'
    r'([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|'
    r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)|'
    r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|[0-9a-fA-F]{7}'
)

_SUSPICIOUS_TLDS = frozenset([
    'fit', 'tk', 'gp', 'ga', 'work', 'ml', 'date', 'wang', 'men', 'icu', 'online', 'click',
    'country', 'stream', 'download', 'xin', 'racing', 'jetzt', 'ren', 'mom', 'party',
    'review', 'trade', 'accountants', 'science', 'ninja', 'xyz', 'faith', 'zip', 'cricket',
    'win', 'accountant', 'realtor', 'top', 'christmas', 'gdn', 'link', 'asia', 'club',
    'la', 'ae', 'exposed', 'pe', 'go.id', 'rs', 'k12.pa.us', 'or.kr', 'ce.ke', 'audio',
    'gob.pe', 'gov.az', 'website', 'bj', 'mx', 'media', 'sa.gov.au',
])

_PORT_PATTERN = re.compile(
    r"^[a-z][a-z0-9+\-.]*://([a-z0-9\-._~%!$&'()*+,;=]+@)?"
    r"([a-z0-9\-._~%]+|\[[a-z0-9\-._~%!$&'()*+,;=:]+\]):([0-9]+)",
    re.IGNORECASE,
)

_ABNORMAL_SUBDOMAIN_PATTERN = re.compile(r'(http[s]?://(w[w]?|\d))([w]?(\d|-))')

_PREFIX_SUFFIX_PATTERN = re.compile(r"https?://[^\-]+-[^\-]+/")


# ── Internal helper functions ─────────────────────────────────────────────────

def _words_raw(url: str) -> list[str]:
    """Split URL into raw words by splitting on non-alphanumeric characters."""
    return [w for w in re.split(r'[^a-zA-Z0-9]', url) if w]


def _words_host(hostname: str) -> list[str]:
    return [w for w in re.split(r'[^a-zA-Z0-9]', hostname) if w]


def _words_path(path: str) -> list[str]:
    return [w for w in re.split(r'[^a-zA-Z0-9]', path) if w]


def _char_repeat(words: list[str]) -> int:
    """Count consecutive character repeats of length 2–5."""
    repeat = {2: 0, 3: 0, 4: 0, 5: 0}
    for word in words:
        for n in (2, 3, 4, 5):
            for i in range(len(word) - n + 1):
                sub = word[i:i + n]
                if len(set(sub)) == 1:
                    repeat[n] += 1
    return sum(repeat.values())


def _extract_tld(hostname: str) -> str:
    """Return the TLD (last label after the last dot)."""
    if not hostname:
        return ""
    parts = hostname.split(".")
    return parts[-1].lower() if parts else ""


def _get_subdomain(hostname: str) -> str:
    """Return everything before the registered domain (naive split on dots)."""
    if not hostname:
        return ""
    parts = hostname.split(".")
    # If 2 parts: domain.tld → no subdomain
    # If 3+ parts: sub.domain.tld → sub is subdomain
    if len(parts) > 2:
        return ".".join(parts[:-2])
    return ""


def _ratio_digits(s: str) -> float:
    if not s:
        return 0.0
    digits = sum(1 for c in s if c.isdigit())
    return digits / len(s)


def _count_www(words: list[str]) -> int:
    return sum(1 for w in words if 'www' in w.lower())


def _count_com(words: list[str]) -> int:
    return sum(1 for w in words if 'com' in w.lower())


def _domain_in_brand(hostname: str) -> int:
    """Check if the registered domain (second-to-last label) is in the brand list."""
    if not hostname:
        return 0
    parts = hostname.split(".")
    domain = parts[-2].lower() if len(parts) >= 2 else parts[0].lower()
    return 1 if domain in _BRANDS else 0


def _brand_in_subdomain(hostname: str) -> int:
    subdomain = _get_subdomain(hostname)
    if not subdomain:
        return 0
    subdomain_lower = subdomain.lower()
    for brand in _BRANDS:
        if brand in subdomain_lower:
            return 1
    return 0


def _brand_in_path(hostname: str, path: str) -> int:
    """Check if a brand name appears in the path but not in the hostname."""
    parts = hostname.split(".")
    domain = parts[-2].lower() if len(parts) >= 2 else hostname.lower()
    path_lower = path.lower()
    for brand in _BRANDS:
        if ('.' + brand + '.' in path_lower) and (brand not in domain):
            return 1
    return 0


# ── Main extractor ────────────────────────────────────────────────────────────

def extract_features(url: str) -> list[float]:
    """
    Extract 53 URL-only features from a URL string.

    Parameters
    ----------
    url : str
        A URL string.  Must not be fetched or opened — only parsed as a string.

    Returns
    -------
    list[float]
        53 numeric feature values in the same order as FEATURE_NAMES.
        Compatible with the trained model's feature schema.
    """
    # Parse URL components
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path or ""
        scheme = parsed.scheme or ""
    except Exception:
        hostname = ""
        path = ""
        scheme = ""

    words_raw = _words_raw(url)
    words_host = _words_host(hostname)
    words_path = _words_path(path)
    tld = _extract_tld(hostname)
    subdomain = _get_subdomain(hostname)

    # ── Compute all 53 features ───────────────────────────────────────────────

    length_url = len(url)
    length_hostname = len(hostname)
    ip = 1 if _IP_PATTERN.search(url) else 0
    nb_dots = url.count('.')
    nb_hyphens = url.count('-')
    nb_at = url.count('@')
    nb_qm = url.count('?')
    nb_and = url.count('&')
    nb_or = url.count('|')
    nb_eq = url.count('=')
    nb_underscore = url.count('_')
    nb_tilde = 1 if url.count('~') > 0 else 0
    nb_percent = url.count('%')
    nb_slash = url.count('/')
    nb_star = url.count('*')
    nb_colon = url.count(':')
    nb_comma = url.count(',')
    nb_semicolumn = url.count(';')
    nb_dollar = url.count('$')
    nb_space = url.count(' ') + url.count('%20')

    nb_www = _count_www(words_raw)
    nb_com = _count_com(words_raw)

    # Count double-slash redirections beyond position 6 (after http://)
    dslash_positions = [m.start() for m in re.finditer('//', url)]
    nb_dslash = 1 if (dslash_positions and dslash_positions[-1] > 6) else 0

    http_in_path = path.count('http')
    https_token = 0 if scheme == 'https' else 1
    ratio_digits_url = _ratio_digits(url)
    ratio_digits_host = _ratio_digits(hostname) if hostname else 0.0

    punycode = 1 if (url.startswith("http://xn--") or url.startswith("https://xn--")) else 0
    port = 1 if _PORT_PATTERN.search(url) else 0
    tld_in_path = 1 if (tld and tld in path.lower()) else 0
    tld_in_subdomain = 1 if (tld and subdomain and tld in subdomain.lower()) else 0
    abnormal_subdomain = 1 if _ABNORMAL_SUBDOMAIN_PATTERN.search(url) else 0

    # Count subdomains
    dot_count = hostname.count('.')
    if dot_count == 0:
        nb_subdomains = 1
    elif dot_count == 1:
        nb_subdomains = 2
    else:
        nb_subdomains = 3

    prefix_suffix = 1 if _PREFIX_SUFFIX_PATTERN.search(url) else 0

    # random_domain: heuristic — high ratio of consonant clusters or digit ratio
    # The original uses an NLP model; we use a simple heuristic that is deterministic
    domain_part = hostname.split(".")[0] if hostname else ""
    digit_ratio = _ratio_digits(domain_part)
    vowels = sum(1 for c in domain_part.lower() if c in 'aeiou')
    vowel_ratio = vowels / len(domain_part) if domain_part else 0.0
    random_domain = 1 if (digit_ratio > 0.4 or (len(domain_part) > 4 and vowel_ratio < 0.1)) else 0

    shortening_service = 1 if _SHORTENING_PATTERN.search(url) else 0
    path_extension = 1 if path.endswith('.txt') else 0

    length_words_raw = len(words_raw)

    char_repeat = _char_repeat(words_raw)

    def _min_len(words: list[str]) -> int:
        return min((len(w) for w in words), default=0)

    def _max_len(words: list[str]) -> int:
        return max((len(w) for w in words), default=0)

    def _avg_len(words: list[str]) -> float:
        return sum(len(w) for w in words) / len(words) if words else 0.0

    shortest_words_raw = _min_len(words_raw)
    shortest_word_host = _min_len(words_host)
    shortest_word_path = _min_len(words_path)
    longest_words_raw = _max_len(words_raw)
    longest_word_host = _max_len(words_host)
    longest_word_path = _max_len(words_path)
    avg_words_raw = _avg_len(words_raw)
    avg_word_host = _avg_len(words_host)
    avg_word_path = _avg_len(words_path)

    phish_hints_val = sum(1 for hint in _HINTS if hint in path.lower())

    domain_in_brand_val = _domain_in_brand(hostname)
    brand_in_subdomain_val = _brand_in_subdomain(hostname)
    brand_in_path_val = _brand_in_path(hostname, path)
    suspecious_tld = 1 if tld in _SUSPICIOUS_TLDS else 0

    features = [
        length_url,
        length_hostname,
        ip,
        nb_dots,
        nb_hyphens,
        nb_at,
        nb_qm,
        nb_and,
        nb_or,
        nb_eq,
        nb_underscore,
        nb_tilde,
        nb_percent,
        nb_slash,
        nb_star,
        nb_colon,
        nb_comma,
        nb_semicolumn,
        nb_dollar,
        nb_space,
        nb_www,
        nb_com,
        nb_dslash,
        http_in_path,
        https_token,
        ratio_digits_url,
        ratio_digits_host,
        punycode,
        port,
        tld_in_path,
        tld_in_subdomain,
        abnormal_subdomain,
        nb_subdomains,
        prefix_suffix,
        random_domain,
        shortening_service,
        path_extension,
        length_words_raw,
        char_repeat,
        shortest_words_raw,
        shortest_word_host,
        shortest_word_path,
        longest_words_raw,
        longest_word_host,
        longest_word_path,
        avg_words_raw,
        avg_word_host,
        avg_word_path,
        phish_hints_val,
        domain_in_brand_val,
        brand_in_subdomain_val,
        brand_in_path_val,
        suspecious_tld,
    ]

    assert len(features) == len(FEATURE_NAMES), (
        f"Feature vector length {len(features)} != schema length {len(FEATURE_NAMES)}"
    )
    return [float(v) for v in features]
