# AI/ML Approach

## Core approach

This project uses a hybrid AI/ML architecture combining deterministic detection, optional NER, and LLM reasoning.

### 1. Rule-based detection
- `detectors.py` performs regex-based scans for structured identifiers:
  - Aadhaar
  - PAN
  - credit/debit cards
  - phone numbers
  - emails
  - IFSC codes
  - API keys and tokens
- It includes checksum validation for card and account numbers and context-based keyword anchoring.
- This layer is fast, explainable, and works without external APIs.

### 2. Optional NER
- `ner_detector.py` uses spaCy to detect unstructured PII such as person names and locations.
- It is designed to augment regex detection for free-form text.
- If the spaCy model is missing, the app falls back safely to regex-only detection.

### 3. LLM-based reasoning
- `ai_service.py` generates compliance summaries and answers questions.
- Current provider support includes:
  - OpenAI
  - Groq
  - Gemini
- Q&A is grounded using local TF-IDF retrieval instead of embeddings, making it provider-agnostic.

### 4. Indic language readiness
- The architecture is designed so Indian providers like Gnani and Sarvam can be added later.
- Future work includes model-specific prompts and Indian-language OCR support.

## Why this combination?
- Deterministic detection catches exact-format sensitive items reliably.
- NER fills gaps for unstructured personal data.
- LLMs help produce readable compliance summaries and context-aware answers.

## Safety considerations
- Use AI only for summaries and question answering.
- Keep raw PII detection within local deterministic logic when possible.
- Mask sensitive values in exports and audit logs.
