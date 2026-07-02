"""
detectors.py
------------
Rule-based / regex sensitive-data detection engine.

Each detector returns a list of dicts:
    {
        "type": "PAN Number",
        "value": "ABCDE1234F",
        "position": 145,          # char offset in source text
        "context": "...surrounding text..."
    }

Detection is intentionally implemented with regex + validation checksums
(e.g. Luhn for card numbers) rather than an external NLP model so that the
tool works fully offline and deterministically -- this also makes it easy
to explain / defend the approach in an interview.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class Finding:
    type: str
    value: str
    position: int
    context: str
    risk_weight: int  # 1 = low, 2 = medium, 3 = high


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _context(text: str, start: int, end: int, window: int = 40) -> str:
    lo = max(0, start - window)
    hi = min(len(text), end + window)
    snippet = text[lo:hi].replace("\n", " ")
    return f"...{snippet}..."


def _luhn_valid(number: str) -> bool:
    """Validate a card number using the Luhn algorithm."""
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


# --------------------------------------------------------------------------- #
# Individual pattern detectors
# --------------------------------------------------------------------------- #

PATTERNS = {
    # type name -> (regex, risk_weight)
    "Email Address": (
        re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
        2,
    ),
    "Phone Number (India)": (
        re.compile(r"(?<!\d)(?:\+91[-\s]?|0)?[6-9]\d{9}(?!\d)"),
        2,
    ),
    # Requires the standard displayed "XXXX XXXX XXXX" spacing so that a
    # bare 12-digit run (e.g. a bank account number) or a longer digit
    # sequence (e.g. a 16-digit card number) isn't mistaken for an
    # Aadhaar number.
    "Aadhaar Number": (
        re.compile(r"(?<!\d)(?<!\d )\d{4} \d{4} \d{4}(?!\d)(?! ?\d{4})"),
        3,
    ),
    "PAN Number": (
        re.compile(r"(?<![A-Z0-9])[A-Z]{5}[0-9]{4}[A-Z](?![A-Z0-9])"),
        3,
    ),
    "Credit/Debit Card Number": (
        re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
        3,
    ),
    "IFSC Code": (
        re.compile(r"(?<![A-Z0-9])[A-Z]{4}0[A-Z0-9]{6}(?![A-Z0-9])"),
        2,
    ),
    "Bank Account Number": (
        re.compile(r"(?<!\d)\d{9,18}(?!\d)"),
        3,
    ),
    "API Key / Secret Token": (
        re.compile(
            r"(?i)(?:api[_-]?key|secret|access[_-]?token|bearer)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{12,}['\"]?"
        ),
        3,
    ),
    "Password": (
        re.compile(r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]?\S{4,}['\"]?"),
        3,
    ),
    "Employee ID": (
        re.compile(r"(?i)\b(?:EMP|EID|EMPID)[-_ ]?\d{3,8}\b"),
        1,
    ),
    "IP Address": (
        re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)"),
        1,
    ),
}

CONFIDENTIAL_KEYWORDS = [
    "confidential", "internal use only", "do not distribute", "trade secret",
    "proprietary", "nda", "non-disclosure", "restricted", "classified",
    "salary", "compensation", "merger", "acquisition", "unreleased",
]


def _detect_pan(text: str) -> List[Finding]:
    return _run_pattern(text, "PAN Number")


def _detect_card_numbers(text: str) -> List[Finding]:
    """Credit card numbers need Luhn validation to cut down false positives
    (plain 13-19 digit runs are otherwise extremely common: phone numbers,
    account numbers, IDs, etc.)."""
    findings = []
    regex, weight = PATTERNS["Credit/Debit Card Number"]
    for m in regex.finditer(text):
        raw = m.group()
        digits_only = re.sub(r"[ -]", "", raw)
        if 13 <= len(digits_only) <= 19 and _luhn_valid(digits_only):
            findings.append(
                Finding(
                    type="Credit/Debit Card Number",
                    value=raw.strip(),
                    position=m.start(),
                    context=_context(text, m.start(), m.end()),
                    risk_weight=weight,
                )
            )
    return findings


def _detect_bank_account(text: str) -> List[Finding]:
    """Bank account numbers are ambiguous with generic long digit strings.
    We only flag them when a nearby keyword (account/a/c/acct) is present,
    to reduce noise, but keep the raw pattern findable for the summary."""
    findings = []
    regex, weight = PATTERNS["Bank Account Number"]
    keyword_regex = re.compile(r"(?i)a/?c|account\s*(no|number)?")
    for m in regex.finditer(text):
        window = text[max(0, m.start() - 30): m.start()]
        if keyword_regex.search(window):
            findings.append(
                Finding(
                    type="Bank Account Number",
                    value=m.group(),
                    position=m.start(),
                    context=_context(text, m.start(), m.end()),
                    risk_weight=weight,
                )
            )
    return findings


def _run_pattern(text: str, pattern_name: str) -> List[Finding]:
    regex, weight = PATTERNS[pattern_name]
    findings = []
    for m in regex.finditer(text):
        findings.append(
            Finding(
                type=pattern_name,
                value=m.group().strip(),
                position=m.start(),
                context=_context(text, m.start(), m.end()),
                risk_weight=weight,
            )
        )
    return findings


def _detect_confidential_keywords(text: str) -> List[Finding]:
    findings = []
    lower = text.lower()
    for kw in CONFIDENTIAL_KEYWORDS:
        for m in re.finditer(re.escape(kw), lower):
            findings.append(
                Finding(
                    type="Confidential Business Information",
                    value=text[m.start():m.end()],
                    position=m.start(),
                    context=_context(text, m.start(), m.end()),
                    risk_weight=2,
                )
            )
    return findings


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def detect_sensitive_data(text: str, include_ner: bool = False) -> List[Finding]:
    """Run every detector over `text` and return a de-duplicated, sorted
    list of Finding objects.

    include_ner: when True, also runs the optional spaCy-based NER layer
    (ner_detector.py) to catch unstructured PII such as person names and
    addresses that regex patterns cannot express. Imported lazily here to
    avoid a circular import (ner_detector imports Finding from this
    module) and so the regex-only path has zero dependency on spaCy.
    """
    findings: List[Finding] = []

    # Simple regex-driven detectors
    for name in ["Email Address", "Phone Number (India)", "Aadhaar Number",
                 "IFSC Code", "API Key / Secret Token", "Password",
                 "Employee ID", "IP Address"]:
        findings.extend(_run_pattern(text, name))

    # Detectors needing extra validation logic
    findings.extend(_detect_pan(text))
    findings.extend(_detect_card_numbers(text))
    findings.extend(_detect_bank_account(text))
    findings.extend(_detect_confidential_keywords(text))

    if include_ner:
        from ner_detector import detect_ner_entities
        findings.extend(detect_ner_entities(text))

    # De-duplicate identical (type, value, position) triples that might
    # arise from overlapping patterns (e.g. Aadhaar-shaped substrings
    # inside a longer bank account number).
    seen = set()
    deduped = []
    for f in sorted(findings, key=lambda f: f.position):
        key = (f.type, f.value, f.position)
        if key not in seen:
            seen.add(key)
            deduped.append(f)
    return deduped


def summarize_findings(findings: List[Finding]) -> Dict[str, int]:
    """Return counts per sensitive-data type, e.g. {'Email Address': 4, ...}"""
    counts: Dict[str, int] = {}
    for f in findings:
        counts[f.type] = counts.get(f.type, 0) + 1
    return counts
