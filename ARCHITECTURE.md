# Architecture Overview

## High-level architecture

This project is built as a hybrid solution with both Python/Streamlit and React/Node layers.

- `app.py` — Streamlit-based UI for document upload, analysis, OCR, and reporting.
- `document_parser.py` — extracts text from PDFs, images, TXT, CSV, DOCX, XLSX, JSON, and scanned content.
- `ocr_service.py` — OCR layer using Sarvam Vision API and local pytesseract fallback.
- `detectors.py` — rule-based PII detection engine with regex and validation checks.
- `ner_detector.py` — optional spaCy NER layer for unstructured PII detection.
- `risk_classifier.py` — aggregates findings into low/medium/high risk levels.
- `redaction.py` — generates masked redacted output.
- `ai_service.py` — provider-agnostic AI interface for summaries and Q&A.
- `warehouse_export.py` — exports findings and audit logs as Parquet, CSV, or Excel.
- `server.ts` + React frontend — optional modern web app frontend with AI provider key input.

## Data flow

1. User uploads document(s).
2. `document_parser.py` extracts text and/or runs OCR.
3. `detectors.py` scans extracted text for structured PII and confidential terms.
4. `ner_detector.py` optionally runs spaCy to catch names and locations.
5. `risk_classifier.py` scores the document based on findings.
6. `ai_service.py` generates compliance summaries and answers user questions.
7. `redaction.py` creates masked versions of sensitive documents.
8. `warehouse_export.py` exports results for compliance review.

## Provider abstraction

The AI layer is designed to support multiple providers:
- OpenAI
- Groq
- Gemini (via `@google/genai`)
- Future Indian/Indic providers such as Gnani and Sarvam

## Why this architecture

- Keeps deterministic PII detection separate from AI reasoning.
- Allows AI to be used only for summary and context-aware Q&A.
- Enables OCR to handle scanned and multi-language documents.
- Supports both a Python Streamlit experience and a modern React/Node interface.
