"""
risk_classifier.py
-------------------
Turns a list of Finding objects into an overall document risk rating
(Low / Medium / High) plus a per-type breakdown.

Scoring approach
-----------------
Each Finding already carries a `risk_weight` (1=low, 2=medium, 3=high)
assigned by the detector that produced it. We aggregate:

    score = sum(risk_weight for each finding)

Then map the total score to a bucket using thresholds that scale with
document size implicitly (a single high-risk item is enough to push a
short document into "High", while the same item in a long document with
little else present still causes concern -- absolute counts of
high-severity categories matter more than density for compliance
purposes).
"""

from typing import List, Dict
from detectors import Finding

HIGH_RISK_TYPES = {
    "Aadhaar Number", "PAN Number", "Credit/Debit Card Number",
    "Bank Account Number", "API Key / Secret Token", "Password",
}
MEDIUM_RISK_TYPES = {
    "Email Address", "Phone Number (India)", "IFSC Code",
    "Confidential Business Information", "Person Name", "Location / Address",
}


def classify_risk(findings: List[Finding]) -> Dict:
    high_count = sum(1 for f in findings if f.type in HIGH_RISK_TYPES)
    medium_count = sum(1 for f in findings if f.type in MEDIUM_RISK_TYPES)
    low_count = len(findings) - high_count - medium_count

    score = sum(f.risk_weight for f in findings)

    if high_count >= 1 or score >= 12:
        level = "High Risk"
    elif medium_count >= 1 or score >= 4:
        level = "Medium Risk"
    else:
        level = "Low Risk"

    return {
        "level": level,
        "score": score,
        "high_count": high_count,
        "medium_count": medium_count,
        "low_count": max(low_count, 0),
        "total_findings": len(findings),
    }


def risk_color(level: str) -> str:
    return {
        "High Risk": "#e74c3c",
        "Medium Risk": "#f39c12",
        "Low Risk": "#27ae60",
    }.get(level, "#7f8c8d")
