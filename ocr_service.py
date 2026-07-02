"""
ocr_service.py
---------------
OCR / Document Intelligence layer for image files and scanned (image-only)
PDFs.

Primary: Sarvam Vision (https://docs.sarvam.ai) via the `sarvamai` SDK.
Chosen over generic OCR because:
- It's purpose-built for Indian-language documents (22 Indic languages +
  English), which matters directly for this tool: Aadhaar cards, PAN
  cards, bank forms, and HR paperwork in India are very often scanned
  and frequently mix English with a regional script.
- It preserves document structure (tables, reading order) rather than
  returning a flat text blob, which helps the downstream regex/NER
  detectors work against cleanly separated fields instead of jumbled OCR
  text.

Fallback: pytesseract (local, English-focused, no API key or network
required) so plain image uploads still work if no Sarvam key is
configured -- keeping the "upload and scan" flow functional out of the
box, with Sarvam Vision as the opt-in upgrade for scanned PDFs and
Indic-language documents.

API shape (per Sarvam's Document Intelligence docs): create a job,
upload the file, start it, poll until complete, then download a ZIP
containing markdown/JSON output.
"""

import io
import os
import tempfile
import zipfile
from typing import Optional


def extract_text_sarvam(
    file_bytes: bytes,
    filename: str,
    api_key: str,
    language: str = "en-IN",
) -> str:
    """Run a file through Sarvam Vision's Document Intelligence pipeline
    and return the extracted text (markdown)."""
    from sarvamai import SarvamAI

    client = SarvamAI(api_subscription_key=api_key)
    job = client.document_intelligence.create_job(
        language=language, output_format="md"
    )

    suffix = os.path.splitext(filename)[1] or ".pdf"
    tmp_in_path = None
    tmp_out_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        job.upload_file(tmp_in_path)
        job.start()
        status = job.wait_until_complete()

        if getattr(status, "job_state", None) not in ("Completed", None):
            raise RuntimeError(
                f"Sarvam Vision job did not complete successfully "
                f"(state: {status.job_state})."
            )

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name
        job.download_output(tmp_out_path)

        text_parts = []
        with zipfile.ZipFile(tmp_out_path) as zf:
            for name in zf.namelist():
                if name.lower().endswith((".md", ".txt")):
                    text_parts.append(zf.read(name).decode("utf-8", errors="ignore"))
        return "\n\n".join(text_parts)
    finally:
        for p in (tmp_in_path, tmp_out_path):
            if p and os.path.exists(p):
                os.remove(p)


def extract_text_tesseract(file_bytes: bytes) -> str:
    """Local OCR fallback for plain image files (PNG/JPG) using
    pytesseract. No API key or network access required."""
    from PIL import Image
    import pytesseract

    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)


def ocr_extract(
    file_bytes: bytes,
    filename: str,
    sarvam_api_key: Optional[str] = None,
    language: str = "en-IN",
) -> str:
    """Extract text from an image or scanned PDF.

    Prefers Sarvam Vision when an API key is supplied (works for PDFs,
    PNG, JPG, and Indic scripts). Falls back to local pytesseract for
    plain image formats when no key is configured.
    """
    if sarvam_api_key:
        return extract_text_sarvam(file_bytes, filename, sarvam_api_key, language)

    lower = filename.lower()
    if lower.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_tesseract(file_bytes)

    raise RuntimeError(
        "This looks like a scanned/image-based PDF. OCR for scanned PDFs "
        "requires a Sarvam Vision API key (add one in the sidebar). "
        "Plain PNG/JPG images can be OCR'd locally without a key."
    )
