"""
Message analysis service — T-03 implementation.

Uses transparent rule-based detection labelled as "rules".
There is no trained message classifier in this project; the method field
always returns "rules" and the disclaimer makes this explicit.

INVARIANTS (never violated):
  - Raw message text is never stored or logged.
  - No HTTP requests, DNS lookups, or external calls are made.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import NamedTuple

from app.schemas import (
    AnalysisMethod,
    Indicator,
    Language,
    MessageAnalysisResponse,
    RiskCategory,
)

# ── Disclaimer and recommendations ───────────────────────────────────────────

_DISCLAIMER = (
    "This assessment is produced by transparent rule-based pattern matching "
    "and can be wrong. No ML classifier is used for message analysis. "
    "It does not guarantee that a message is safe or a scam. "
    "Always verify communications through official channels independently."
)

_RECOMMENDATIONS_EN = [
    "Do not share OTPs, passwords, Aadhaar numbers, or banking details with anyone.",
    "Verify any job, internship, or scholarship offer on the organisation's official website.",
    "Ignore requests for upfront payment or registration fees from unknown sources.",
    "If a message demands urgent action, slow down — urgency is a common manipulation tactic.",
    "Contact the claimed sender through a known official channel before acting.",
]

_RECOMMENDATIONS_HINGLISH = [
    "Kisi ke saath apna OTP, password, Aadhaar number, ya bank details share mat karein.",
    "Kisi bhi job, internship, ya scholarship offer ko organization ki official website par verify karein.",
    "Anjaan sources se advance payment ya registration fee ke liye bol rahe hain toh ignore karein.",
    "Agar message mein jaldbaazi ho, toh rukein — urgency ek common manipulation tactic hai.",
    "Koi bhi action lene se pehle claimed sender se official channel ke zariye contact karein.",
]


# ── Rule definitions ──────────────────────────────────────────────────────────

class _Rule(NamedTuple):
    code: str
    label: str
    explanation_en: str
    explanation_hinglish: str
    # compiled regex — matched against lowercased message
    pattern: re.Pattern


_RULES: list[_Rule] = [
    _Rule(
        code="otp_request",
        label="OTP or password requested",
        explanation_en=(
            "The message asks for a one-time password (OTP) or account password. "
            "No legitimate bank, government body, or organisation will ever ask for your OTP."
        ),
        explanation_hinglish=(
            "Message mein OTP ya password maanga ja raha hai. "
            "Koi bhi genuine bank, sarkar, ya company kabhi OTP nahi maangti."
        ),
        pattern=re.compile(
            r'\b((otp|one[\s-]?time[\s-]?pass(?:word|code)?|password|passcode|pin)\b[\s\S]{0,60}'
            r'(share|send|give|provide|enter|tell|type|forward)|'
            r'(share|send|give|provide|enter|tell|type|forward)\b[\s\S]{0,60}'
            r'(otp|one[\s-]?time[\s-]?pass(?:word|code)?|password|passcode|pin))\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="prize_lottery_winner",
        label="Prize, lottery, or winner claim",
        explanation_en=(
            "The message claims you have won a prize, lottery, or lucky draw. "
            "These are almost always scams designed to collect fees or personal information."
        ),
        explanation_hinglish=(
            "Message mein prize, lottery, ya lucky draw jeetne ka claim hai. "
            "Aisa lagbhag hamesha ek scam hota hai jo fees ya personal information ikattha karta hai."
        ),
        pattern=re.compile(
            r'\b(congratulations?|congrats|you(?:\'ve|\s+have)\s+won|winner|'
            r'lucky\s+draw|lottery|prize|gift\s+card|reward|jackpot)\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="upfront_payment",
        label="Upfront fee or payment required",
        explanation_en=(
            "The message requests payment, a registration fee, or a security deposit "
            "before delivering a benefit. Legitimate employers and scholarship providers do not "
            "charge fees upfront."
        ),
        explanation_hinglish=(
            "Message mein koi benefit milne se pehle payment, registration fee, "
            "ya security deposit maanga ja raha hai. Genuine employers aur scholarship providers "
            "pehle fee nahi lete."
        ),
        pattern=re.compile(
            r'\b(pay|payment|fee|deposit|charge|registration\s+fee|processing\s+fee|'
            r'security\s+deposit|advance\s+payment|transfer\s+amount)\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="urgency_pressure",
        label="Urgency or time pressure",
        explanation_en=(
            "The message creates urgency — a classic manipulation tactic to prevent "
            "you from verifying the claim. Scammers use deadlines to rush decisions."
        ),
        explanation_hinglish=(
            "Message mein jaldbaazi ka pressure diya ja raha hai — yeh ek classic "
            "manipulation tactic hai. Scammers deadline ka use karke aapko sochne ka time nahi dete."
        ),
        pattern=re.compile(
            r'\b(urgent(?:ly)?|immediately|as\s+soon\s+as\s+possible|asap|'
            r'last\s+(chance|opportunity)|expire[sd]?|'
            r'within\s+\d+\s+(hour|minute|day)|'
            r'do\s+not\s+delay|act\s+now|limited\s+time|response\s+required|'
            r'(final|last|payment|account)\s+deadline)\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="account_block_threat",
        label="Account suspension or block threat",
        explanation_en=(
            "The message threatens to suspend, block, or deactivate your account unless "
            "you take immediate action. This is a common social engineering tactic."
        ),
        explanation_hinglish=(
            "Message mein account suspend, block, ya deactivate karne ki dhamki hai agar aap "
            "turant action nahi lete. Yeh ek common social engineering tactic hai."
        ),
        pattern=re.compile(
            r'\b(account|kyc|profile)\b[\s\S]{0,50}'
            r'\b(block(?:ed)?|suspend(?:ed)?|deactivat(?:e|ed)?|closed?|frozen?|'
            r'restricted?|disabl(?:e|ed)?)\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="kyc_request",
        label="KYC verification request",
        explanation_en=(
            "The message asks you to complete a KYC (Know Your Customer) process. "
            "Fraudsters use fake KYC requests to collect identity documents and banking details."
        ),
        explanation_hinglish=(
            "Message mein KYC complete karne ka request hai. "
            "Fraudsters fake KYC ke zariye identity documents aur banking details collect karte hain."
        ),
        pattern=re.compile(
            r'\b(kyc|know\s+your\s+customer|re[-\s]?verify|update\s+your\s+(details?|records?|'
            r'information|data|document))\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="job_internship_scam",
        label="Suspicious job or internship offer",
        explanation_en=(
            "The message offers a job or internship with high pay and no experience required. "
            "Fake job offers often lure victims into sharing personal details or paying fees."
        ),
        explanation_hinglish=(
            "Message mein high pay aur bina experience ke job ya internship offer hai. "
            "Fake job offers ka use personal details collect karne ya fees lene ke liye hota hai."
        ),
        pattern=re.compile(
            r'\b(work[\s-]from[\s-]home|part[\s-]time|earn\s+\d|'
            r'daily\s+(income|earning)|guaranteed\s+(income|salary|earning)|'
            r'no\s+experience\s+(required|needed)|immediate\s+(joining|vacancy|opening))\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="link_click_request",
        label="Request to click a link",
        explanation_en=(
            "The message asks you to click a link to verify, claim, or complete an action. "
            "Be cautious — the link may lead to a phishing page."
        ),
        explanation_hinglish=(
            "Message mein ek link par click karne ka request hai. "
            "Savdhan rahein — link ek phishing page par le ja sakta hai."
        ),
        pattern=re.compile(
            r'\b(click|tap|visit|open|follow|go\s+to)\b[\s\S]{0,30}'
            r'\b(link|url|button|website|portal|here|below)\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="personal_info_request",
        label="Personal or financial information requested",
        explanation_en=(
            "The message requests sensitive personal or financial details such as Aadhaar, "
            "PAN, bank account number, or credit card information. No legitimate service "
            "requests these via an unsolicited message."
        ),
        explanation_hinglish=(
            "Message mein sensitive personal ya financial details maange ja rahe hain "
            "jaise Aadhaar, PAN, bank account number, ya credit card. Koi bhi legitimate service "
            "aise details ek unsolicited message mein nahi mangti."
        ),
        pattern=re.compile(
            r'\b(aadhaar|aadhar|pan\s+(card|number)|bank\s+account|account\s+number|'
            r'credit\s+card|debit\s+card|cvv|card\s+number|ifsc|upi\s+(id|pin)|'
            r'net[\s-]?banking|mobile\s+(number|no))\b',
            re.IGNORECASE,
        ),
    ),
    _Rule(
        code="impersonation_official",
        label="Impersonation of official authority",
        explanation_en=(
            "The message claims to be from a government body, bank, or well-known "
            "organisation. Scammers often impersonate trusted entities to appear credible."
        ),
        explanation_hinglish=(
            "Message mein sarkar, bank, ya kisi well-known organisation ki taraf se hone ka "
            "claim hai. Scammers trusted entities ki impersonation karte hain."
        ),
        pattern=re.compile(
            r'\b(reserve\s+bank|rbi|income\s+tax|it\s+department|epfo|pf\s+office|'
            r'trai|department\s+of|ministry\s+of|government\s+of\s+india|pmay|pm\s+kisan|'
            r'sbi|hdfc|icici|axis\s+bank|paytm\s+(bank)?|amazon\s+(pay|india)|'
            r'flipkart|google\s+pay|phonepe|neft|imps)\b',
            re.IGNORECASE,
        ),
    ),
]


# ── Scoring and category mapping ──────────────────────────────────────────────

# Rules with higher weight toward High Risk classification
_HIGH_WEIGHT_CODES = frozenset({
    "otp_request",
    "account_block_threat",
    "kyc_request",
    "personal_info_request",
})

def _compute_category(indicators: list[Indicator]) -> RiskCategory:
    if not indicators:
        return RiskCategory.no_obvious_warning_signs
    high_weight_hits = sum(1 for ind in indicators if ind.code in _HIGH_WEIGHT_CODES)
    total_hits = len(indicators)
    if high_weight_hits >= 1 or total_hits >= 3:
        return RiskCategory.high_risk
    if total_hits >= 1:
        return RiskCategory.suspicious
    return RiskCategory.no_obvious_warning_signs


# ── Summary text ──────────────────────────────────────────────────────────────

_SUMMARIES: dict[tuple[RiskCategory, Language], str] = {
    (RiskCategory.high_risk, Language.en): (
        "This message contains strong indicators of a scam or phishing attempt. "
        "Do not share any personal information, click links, or make payments in response to it."
    ),
    (RiskCategory.high_risk, Language.hinglish): (
        "Is message mein scam ya phishing attempt ke strong indicators hain. "
        "Koi bhi personal information share mat karein, links par click mat karein, "
        "ya is message ke jawab mein koi payment mat karein."
    ),
    (RiskCategory.suspicious, Language.en): (
        "This message contains some suspicious patterns. "
        "Verify the sender independently before taking any action."
    ),
    (RiskCategory.suspicious, Language.hinglish): (
        "Is message mein kuch suspicious patterns hain. "
        "Koi bhi action lene se pehle sender ko independently verify karein."
    ),
    (RiskCategory.no_obvious_warning_signs, Language.en): (
        "No obvious scam or phishing indicators were detected in this message. "
        "This does not guarantee it is safe — stay cautious with unexpected messages."
    ),
    (RiskCategory.no_obvious_warning_signs, Language.hinglish): (
        "Is message mein koi obvious scam ya phishing indicators nahi mile. "
        "Yeh safety ki guarantee nahi hai — unexpected messages ke saath savdhan rahein."
    ),
}


def _get_summary(category: RiskCategory, language: Language) -> str:
    return _SUMMARIES.get(
        (category, language),
        _SUMMARIES.get((category, Language.en), ""),
    )


def _get_recommendations(language: Language) -> list[str]:
    if language == Language.hinglish:
        return _RECOMMENDATIONS_HINGLISH
    return _RECOMMENDATIONS_EN


# ── Main analysis function ────────────────────────────────────────────────────

def analyze_message(message: str, language: Language) -> MessageAnalysisResponse:
    """
    Analyze a message string for scam/phishing indicators using rule-based detection.

    No ML classifier is used for message analysis — the method field always
    returns "rules" and the disclaimer makes this explicit.
    Raw message text is never stored or logged.
    """
    indicators: list[Indicator] = []

    for rule in _RULES:
        if rule.pattern.search(message):
            explanation = (
                rule.explanation_hinglish
                if language == Language.hinglish
                else rule.explanation_en
            )
            indicators.append(Indicator(
                code=rule.code,
                label=rule.label,
                explanation=explanation,
            ))

    category = _compute_category(indicators)
    summary = _get_summary(category, language)
    recommendations = _get_recommendations(language)

    return MessageAnalysisResponse(
        category=category,
        method=AnalysisMethod.rules,
        indicators=indicators,
        summary=summary,
        recommendations=recommendations,
        disclaimer=_DISCLAIMER,
        language=language,
    )
