# Future Improvements

## 1. Indian model integration
- Add support for regional providers such as Gnani and Sarvam.
- Add specific prompt templates and model selection for Indic languages.
- Enable provider routing based on detected document language.

## 2. Better OCR for Indic scripts
- Use Sarvam Vision for scanned PDFs and images in Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, and other scripts.
- Add a stronger fallback strategy for documents with mixed Latin and Indic text.

## 3. Persistent retrieval store
- Replace in-memory TF-IDF with FAISS or ChromaDB for large document collections.
- Improve Q&A scalability and long-document support.

## 4. Local/regional model deployment
- Add an optional local containerized inference path for offline or on-premises compliance use.
- Support private Indian model hosting if cloud API keys are unavailable.

## 5. Role-based access and compliance controls
- Add user authentication and role-based permissions.
- Add encrypted audit log storage for compliance retention.

## 6. Production-grade deployment
- Add CI/CD, end-to-end tests, and regression tests for detection accuracy.
- Add monitoring for API latency, OCR failures, and provider fallback.
