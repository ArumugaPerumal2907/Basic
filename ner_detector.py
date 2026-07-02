"""
ner_detector.py
----------------
Optional ML-based detection layer for *unstructured* PII that fixed
regex patterns cannot reliably catch -- primarily person names and
locations/addresses. Uses spaCy's statistical NER model as a
lightweight, fully local, CPU-friendly alternative to a large
transformer pipeline (e.g. the DeBERTa-v3 approach used by tools like
PII Masker: https://github.com/HydroXai/pii-masker).

Design rationale
-----------------
- Regex is great for *fixed-format* identifiers (Aadhaar, PAN, cards,
  emails...) but structurally cannot catch a bare name like "Ravi Kumar"
  or a free-text address -- there's no pattern to match against.
- A full transformer NER model (DeBERTa/Longformer) would catch these
  more accurately, but adds a multi-hundred-MB model download, GPU/CPU
  inference cost, and a hard runtime dependency. For a prototype meant
  to run anywhere with `pip install`, spaCy's small English pipeline
  (~13MB) gives a good accuracy/footprint tradeoff while staying fully
  swappable -- the DeBERTa/Longformer route documented in PII Masker's
  README would be a natural upgrade path (see README "Future
  Improvements").

This layer is optional and additive: if the spaCy model isn't
installed, the app continues to work with regex-only detection and
surfaces a clear message explaining how to enable it, rather than
crashing.
"""

from typing import List, Optional

from detectors import Finding, _context

_NLP = None
_LOAD_ERROR: Optional[str] = None
_LOAD_ATTEMPTED = False


def _get_nlp():
    """Lazily load the spaCy model exactly once per process."""
    global _NLP, _LOAD_ERROR, _LOAD_ATTEMPTED
    if _LOAD_ATTEMPTED:
        return _NLP
    _LOAD_ATTEMPTED = True
    try:
        import spacy
        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError:
            _LOAD_ERROR = (
                "spaCy is installed but the 'en_core_web_sm' model isn't "
                "downloaded yet. Run: python -m spacy download en_core_web_sm"
            )
    except ImportError:
        _LOAD_ERROR = (
            "spaCy is not installed. Run: pip install spacy && "
            "python -m spacy download en_core_web_sm"
        )
    return _NLP


def ner_available() -> bool:
    """Whether the NER layer is ready to use."""
    _get_nlp()
    return _NLP is not None


def ner_status_message() -> Optional[str]:
    """Human-readable reason the NER layer is unavailable, or None if
    it's ready."""
    _get_nlp()
    return _LOAD_ERROR


# Entity labels we care about for PII purposes, mapped to a Finding
# "type" name and a risk weight consistent with detectors.py's scale.
_ENTITY_MAP = {
    "PERSON": ("Person Name", 2),
    "GPE": ("Location / Address", 2),   # countries, cities, states
    "LOC": ("Location / Address", 2),   # non-GPE locations
    "FAC": ("Location / Address", 1),   # buildings, airports, etc.
    "ORG": ("Organization Name", 1),
}

# Cap on characters processed per call; spaCy's small pipeline handles
# long documents fine, but we bound latency on very large uploads.
_MAX_CHARS = 50_000


def detect_ner_entities(text: str) -> List[Finding]:
    """Run spaCy NER over `text` and return Finding objects for
    person/location/organization entities. Returns an empty list (never
    raises) if the model isn't available -- callers should use
    ner_available()/ner_status_message() to surface *why* separately."""
    nlp = _get_nlp()
    if nlp is None:
        return []

    findings: List[Finding] = []
    truncated = text[:_MAX_CHARS]
    doc = nlp(truncated)
    for ent in doc.ents:
        mapped = _ENTITY_MAP.get(ent.label_)
        if not mapped:
            continue
        ftype, weight = mapped
        findings.append(
            Finding(
                type=ftype,
                value=ent.text,
                position=ent.start_char,
                context=_context(truncated, ent.start_char, ent.end_char),
                risk_weight=weight,
            )
        )
    return findings
