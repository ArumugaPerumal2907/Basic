# Challenges Faced

## 1. Mixed technology stack
- The repository includes both a Python Streamlit app and a React/Node frontend.
- This makes deployment planning more complex and requires choosing one delivery path.

## 2. Accurate PII detection
- Structured PII detection is easier with regex, but ambiguous numeric strings can still produce false positives.
- The solution requires checksum validation, context keywords, and careful regex rules.

## 3. Overlapping redactions
- Multiple detectors can match overlapping spans in the same document.
- The redaction layer must merge overlaps cleanly to avoid corrupting text.

## 4. Grounded Q&A without embeddings
- Groq does not support embeddings, so the app uses local TF-IDF retrieval instead.
- This required building a provider-agnostic retrieval pipeline that still stays grounded in document text.

## 5. OCR and multi-language text
- Scanned PDFs and images may contain Indian scripts, which require Sarvam Vision or an Indic-aware OCR path.
- Local fallback with pytesseract is limited to English and simple image formats.

## 6. API key handling
- The UI must allow users to paste keys at runtime without committing secrets.
- The backend must accept per-request provider/API key values and avoid logging sensitive values.
