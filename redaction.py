"""
redaction.py
------------
Bonus feature: produce a redacted copy of the document text with every
detected sensitive value masked out, so it can be safely shared/reviewed
without exposing the underlying data.
"""

from typing import List
from detectors import Finding


def redact_text(text: str, findings: List[Finding]) -> str:
    """Replace each finding's exact span with a masked placeholder like
    [REDACTED:PAN Number]. Overlapping spans (e.g. two detectors matching
    the same or overlapping substrings) are merged into a single
    redaction so the surrounding text is never corrupted."""
    if not findings:
        return text

    spans = []
    for f in findings:
        start = f.position
        end = start + len(f.value)
        spans.append((start, end, f.type))
    spans.sort(key=lambda s: s[0])

    merged = []
    for start, end, ftype in spans:
        if merged and start < merged[-1][1]:
            # Overlaps the previous span -> extend it and combine labels
            prev_start, prev_end, prev_types = merged[-1]
            new_end = max(prev_end, end)
            if ftype not in prev_types:
                prev_types = prev_types + [ftype]
            merged[-1] = (prev_start, new_end, prev_types)
        else:
            merged.append((start, end, [ftype]))

    # Rebuild the string using the merged, non-overlapping spans,
    # processed back-to-front so offsets stay valid while editing.
    redacted = text
    for start, end, ftypes in sorted(merged, key=lambda s: s[0], reverse=True):
        placeholder = f"[REDACTED:{'/'.join(ftypes)}]"
        redacted = redacted[:start] + placeholder + redacted[end:]
    return redacted
