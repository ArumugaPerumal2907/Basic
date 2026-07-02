# Future Plan: Multi-Provider & Indic Model Integration

## Goal
Enhance the current compliance assistant by adding broader multi-model support, especially for Indian AI providers and multimodal Indic-language context understanding. The primary objective is to support improved regional language quality, better OCR+NLP handling for Indian documents, and flexible provider selection in both the frontend and backend.

## Target Providers and Models
- **Gnani**
  - Indian LLM provider focused on Indic language models
  - Use-case: compliance summaries, extractive reasoning, language-specific contextual understanding
- **Sarvam**
  - Vision + document intelligence API with strong multi-lingual OCR support
  - Use-case: scanned documents, PDF images, regional scripts, and multimodal text extraction
- **OpenAI / Groq**
  - Existing generic provider support should remain as fallback and baseline
- **Future Indian models**
  - Add local or cloud-based models such as `ai4bharat`, `IndicTrans`, or similar regional LLMs when APIs are available

## Why this matters
- Indian enterprises and government documents often contain:
  - Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, Marathi, Gujarati, Punjabi, Odia, Assamese, and more
  - Mixed-language text (English + local script) in the same document
  - Formal legal/compliance phrasing with regional terms
- Existing generic LLM providers may not preserve nuance in Indic languages, especially for hallucination-sensitive compliance/risk summaries.
- Better Indic model integration increases accuracy for:
  - OCR extraction of scanned documents
  - PII detection in local-language contexts
  - Compliance recommendation generation for Indian regulations

## Proposed Architecture Additions

### 1. Provider abstraction layer
Create or extend `ai_service.py` and/or server-side provider routing with a generic interface:
- `provider: 'openai' | 'groq' | 'gnani' | 'sarvam'`
- `apiKey` / `apiSecret` passed securely from frontend
- `model` selection mapped per provider
- `generateSummary(text, provider, model, mode)` returns consistent `{result, provider, model}`

### 2. Sarvam multimodal OCR + text pipeline
Add a document parser flow that supports:
- `sarvam_vision` as OCR source for image/PDF text extraction
- `sarvam_document` or equivalent multimodal API for scanned forms and Hindi/Indic script detection
- fallback to `pytesseract` for unsupported inputs
- output normalization for downstream detectors and AI prompts

### 3. Indic-aware prompt templates
Introduce provider-specific prompts for Indian compliance context:
- `Hindi`, `Tamil`, `Telugu`, etc. prompt fallback based on detected language
- prompt templates for: summary, risk analysis, Q&A, redaction review
- add explicit instructions to preserve confidentiality and avoid exposing raw PII

### 4. Language detection and routing
Add a lightweight language detection stage before AI calls:
- detect primary document language using heuristic or compact library
- if Indic language detected, prioritize Gnani / Sarvam models
- otherwise use OpenAI/Groq as fallback

### 5. Model selection UI enhancements
Update frontend to support:
- provider dropdown: `OpenAI`, `Groq`, `Gnani`, `Sarvam`
- provider-specific key input fields
- model selector for each provider
- language hint / detected language display
- status badges such as `Indic model enabled`, `OCR provider active`

## Implementation Roadmap

### Phase 1: API provider plumbing
- Add provider enum and typed state in frontend context
- Add provider-specific API key fields and model selectors in Sidebar
- Update `/api/ai` route to support `gnani` and `sarvam` provider values
- Add `apiKey` and provider routing to backend AI call logic

### Phase 2: Sarvam OCR / multimodal support
- Add Sarvam integration to `ocr_service.py`
- Detect scanned PDFs/images and call Sarvam OCR first
- Normalize returned text for downstream detection
- Add metadata to results showing OCR provider used

### Phase 3: Gnani completion support
- Add Gnani provider support in `ai_service.py` or server route
- Map provider-specific endpoints/headers, e.g. `Authorization: Bearer <key>` and model names
- Add provider-specific prompt templates for compliance summaries
- Validate Gnani output with a small prompt and fallback to OpenAI if model fails

### Phase 4: Indic language tuning
- Add language detection on extracted text and OCR output
- Choose the best provider/model based on detected language
- Add localized prompt templates and optional translation layer
- Optionally add a post-processing module to verify output contains the right language style and compliance tokens

### Phase 5: QA + validation
- Add end-to-end tests for each provider route
- Add small sample documents in multiple Indic languages
- Validate OCR+AI summary pipeline on at least 3 language samples
- Add regression tests for provider fallback, API-key behavior, and no-key fallback paths

## Detailed Enhancements

### A. API integration for Gnani
- Add a new provider mapping in `server.ts` or `ai_service.py`
- Use `fetch` or provider SDK for Gnani endpoint
- Keep request/response shape consistent with existing OpenAI/Groq handling
- Add a small `gnani` provider client to encapsulate request signing and error handling

### B. Sarvam multimodal OCR enhancement
- Add `ocr_service.py` functions:
  - `extract_text_sarvam(fileBuffer, fileType, languageHint)`
  - `extract_text_fallback(fileBuffer, fileType)`
- Add support for image+PDF page detection pipeline
- Update `document_parser.py` to optionally call Sarvam first based on file type or content heuristic

### C. Indic model prompt engineering
- Summary prompt example:
  - `"You are a compliance assistant for Indian regulations. Review this document and summarize the sensitive data, compliance issues, and high-risk areas. Use simple Hindi / Marathi / Tamil language if the input is primarily in that language."`
- Question prompt example:
  - `"Answer the following question using only the provided document text. If the document is in an Indic language, respond in the same language while preserving confidentiality."`
- Use explicit instructions to avoid leaking the raw text of sensitive fields

## Risks and Mitigations
- **Provider-specific API breaking changes**: keep provider clients isolated and versioned in separate modules
- **Quality drift across languages**: prefer local OCR + regional models for Indic text; fallback to generic models only when needed
- **Credential leakage**: never log API key values; only persist provider names and model selections
- **Inconsistent results**: expose `provider` + `model` metadata in the audit log for traceability
- **Latency for OCR + LLM**: cache Sarvam OCR results and reuse extracted text for multiple analysis steps

## Success Criteria
- User can choose `Gnani` or `Sarvam` as provider in the UI
- App accepts per-provider API keys and uses them for AI/OCR requests
- Scanned Indic-language docs are successfully extracted with Sarvam OCR
- Compliance summary and Q&A preserve Indic language context and show improved regional accuracy
- No-key mode still works for basic PII/risk detection and summary suppression

## Notes for future expansion
- Add a separate `provider_registry` module to make new providers pluggable
- Add support for offline Indic models via local containerized inference if SaaS APIs are unavailable
- Consider a hybrid fallback chain: `Sarvam OCR -> Gnani summary -> OpenAI fallback` for maximum reliability
- Expose a `language` field in the audit log to support regional compliance reporting
