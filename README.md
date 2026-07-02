# Sensitive Data Detection & Compliance Assistant

An AI-powered Streamlit application that scans uploaded documents for sensitive and confidential information, classifies risk, and generates compliance reports. Built as an assignment submission for the AI Innovation Internship at Proteccio Data.

**Key differentiators:**
- **Multi-provider LLM support** — switch between OpenAI and Groq with a single radio button; no code changes needed
- **Multi-document upload** — scan dozens of files in one session, aggregate results in a cross-document Dashboard
- **Rich multi-format support** — PDF (including scanned via OCR), TXT, MD, CSV, DOCX, XLSX, JSON, PNG, JPG
- **OCR for scanned documents** — Sarvam Vision API (22 Indian languages + English) with local pytesseract fallback
- **Three-layer detection** — regex+Luhn (structured PII) → optional spaCy NER (names/addresses) → LLM-grounded Q&A
- **Data warehouse export** — findings & audit log as Parquet (Apache Spark/Hive/Presto/Snowflake/BigQuery), Excel, or CSV, with sensitive values masked
- **Audit trail** — every action timestamped and searchable, exportable for compliance/SOX/internal review

---

## ✨ Features

- **Multi-format document upload**: PDF, TXT, MD, CSV, DOCX, XLSX, XLS, JSON, PNG, JPG, JPEG
- **Sensitive data detection**: Aadhaar numbers, PAN numbers, emails, phone numbers, credit/debit card numbers (Luhn-validated), bank account numbers, IFSC codes, API keys/tokens, passwords, employee IDs, IP addresses, and confidential-business-language keywords
- **Optional AI/NER detection**: toggle on a spaCy-powered layer to also catch unstructured PII — person names, locations/addresses — that regex alone can't express
- **Risk classification**: Low / Medium / High, with per-finding severity weighting
- **AI-generated compliance summary**: observations, security risks, and suggested remediation steps via OpenAI or Groq
- **Grounded Q&A chat**: ask natural-language questions about any document; answers use local TF-IDF retrieval (no embeddings API call) to stay grounded in the actual text
- **Bonus — Data redaction**: downloadable, automatically masked version of any document
- **Bonus — Multi-document Dashboard**: cross-document risk metrics, aggregated findings by type, charts
- **Bonus — Data warehouse export**: Parquet, Excel, CSV with sensitive values masked; lands directly in Spark/Hive/Presto/Snowflake/BigQuery external tables
- **Bonus — Audit log**: every scan, summary, question, and error timestamped and searchable; export to Excel/Parquet/CSV
- **Bonus — OCR support**: Sarvam Vision (Document Intelligence) for scanned PDFs and images, with 22-language Indic support; pytesseract fallback for local English-only OCR
- **Bonus — Dockerized**: ready-to-run `Dockerfile` included

---

## � Documentation
- [`SETUP.md`](SETUP.md) — setup and local environment instructions
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — architecture overview and module responsibilities
- [`AI_ML_APPROACH.md`](AI_ML_APPROACH.md) — AI/ML strategy and model reasoning
- [`CHALLENGES.md`](CHALLENGES.md) — technical challenges and how they were solved
- [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md) — planned enhancements and next features
- [`DEPLOYMENT.md`](DEPLOYMENT.md) — deployment steps and Streamlit rollout

---

## �🚀 Setup Instructions

### Option A — Run locally

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd sensitive-data-compliance-assistant

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Enable NER for unstructured PII detection
python -m spacy download en_core_web_sm

# 5. (Optional) Enable Sarvam Vision OCR for scanned PDFs
pip install git+https://github.com/sarvamai/python-sdk.git

# 6. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

**API keys at runtime (no files):**
- Paste your OpenAI or Groq API key into the "AI Provider" sidebar box
- (Optional) Paste your Sarvam Vision API key into the "OCR" sidebar box
- (Environment variables) Set `OPENAI_API_KEY`, `GROQ_API_KEY`, or `SARVAM_API_KEY` in your shell if preferred

**Detection and risk scoring work without any API key.** Only the AI-generated summary, Q&A chat, and OCR for scanned PDFs require keys.

### Option B — Run with Docker

```bash
docker build -t compliance-assistant .
docker run -p 8501:8501 compliance-assistant
```

Then open `http://localhost:8501`. (To pass API keys to the container, use `-e` flags or a `.env` file volume-mounted to `/app`.)

### Try it quickly

A synthetic sample file with fictitious sensitive data is included at `sample_data/sample_document.txt` — upload it to see the full pipeline in action without needing real documents or API keys.

---

## 🏗️ Architecture Overview

```
┌────────────────┐      ┌────────────────────┐      ┌─────────────────────┐
│  File Upload    │─────▶│  document_parser.py │─────▶│  Plain text output   │
│ (PDF/TXT/CSV    │      │  (pypdf / pandas /  │      │ (may be OCR'd via    │
│  /DOCX/XLSX/    │      │   python-docx /     │      │ Sarvam/pytesseract)  │
│  JSON/PNG/JPG)  │      │   ocr_service.py)   │      │                     │
└────────────────┘      └────────────────────┘      └─────────┬───────────┘
                                                                 │
                          ┌──────────────────────────────────────┴─────────┐
                          ▼                                                ▼
                ┌──────────────────┐                          ┌───────────────────┐
                │  detectors.py     │◀───optional───┐          │  redaction.py      │
                │  regex + Luhn     │                │          │  masks findings    │
                │  rule engine      │      ┌─────────┴────────┐ └───────────────────┘
                └────────┬──────────┘      │  ner_detector.py   │
                         │                  │  spaCy NER: names,  │
                         │                  │  addresses           │
                         │                  └─────────────────────┘
                         ▼
                ┌──────────────────────┐
                │  risk_classifier.py   │
                │  Low/Medium/High score │
                └────────┬──────────────┘
                         ▼
        ┌────────────────────────────────────────┐
        │  ai_service.py (OpenAI / Groq)          │
        │  • Compliance summary generation         │
        │  • RAG-lite Q&A (TF-IDF + LLM response) │
        └─────────────┬──────────────────────────┘
                      ▼
        ┌────────────────────────────────────────┐
        │  warehouse_export.py                     │
        │  Parquet / Excel / CSV export            │
        │  (Findings + Summary + Audit Log)        │
        └────────────────────────────────────────┘
                      ▲
                      │
        ┌──────────────────────────────────────┐
        │  app.py (Streamlit)                    │
        │  • Multi-doc upload & management       │
        │  • Provider selection (OpenAI/Groq)    │
        │  • OCR key management                  │
        │  • 7 tabs: Overview/Findings/Summary/  │
        │    Q&A/Redacted/Dashboard/Audit Log   │
        └──────────────────────────────────────┘
```

**Module responsibilities**

| Module | Responsibility |
|---|---|
| `document_parser.py` | Extracts plain text from PDF (pypdf), scanned PDF (Sarvam/pytesseract), TXT, MD, CSV (pandas), DOCX (python-docx), XLSX (pandas), JSON (json), PNG/JPG (PIL + OCR). Scanned-PDF auto-detection via heuristic (very little text per page). |
| `detectors.py` | Rule-based/regex detection engine with checksum validation (Luhn) for cards, plus keyword-based confidential-language detection. Entry point: `detect_sensitive_data(text, include_ner=False)`. |
| `ner_detector.py` | Optional spaCy NER layer for unstructured PII (person names, locations) that regex can't express; degrades gracefully if the model isn't installed. |
| `risk_classifier.py` | Aggregates findings into a Low/Medium/High risk rating and score. |
| `redaction.py` | Produces a masked copy of the document, safely merging overlapping matches from multiple detectors. |
| `ocr_service.py` | OCR extraction layer. Primary: Sarvam Vision API (via `sarvamai` SDK) for scanned PDFs and images. Fallback: pytesseract for local English-only OCR on plain images. |
| `ai_service.py` | Provider-agnostic LLM wrapper (OpenAI, Groq). Compliance summary generation. RAG-lite Q&A using local TF-IDF vectorizer (sklearn) for retrieval, so it works without an embeddings API. |
| `warehouse_export.py` | Converts findings and audit log DataFrames into Parquet (Apache Spark/Hive/Presto native), Excel (openpyxl), or CSV formats, with sensitive values masked. |
| `app.py` | Streamlit UI — multi-document upload, provider/key management, 7 tabs, cross-document dashboard, audit log, warehouse export. |

---

## 🤖 AI/ML Approach

This project combines **three complementary approaches** rather than relying on a single model:

1. **Deterministic rule-based detection (`detectors.py`)**
   - Structured PII with well-defined formats (Aadhaar, PAN, cards) are detected with regex + format-specific validation (Luhn for cards, keyword-anchoring for accounts)
   - Fast, free (no API cost), fully explainable, deterministic/testable
   - Weakness: structurally cannot catch bare names or free-text addresses

2. **Optional statistical NER layer (`ner_detector.py`)**
   - Catches unstructured PII (person names, locations) that regex can't express
   - Uses spaCy's lightweight `en_core_web_sm` pipeline
   - Gracefully optional: if the model isn't installed, the app degrades to regex-only detection with a clear message
   - Weakness: English-focused; lower accuracy on ambiguous/rare names. Upgrade path documented (use DeBERTa/Longformer as in reference tool [PII Masker](https://github.com/HydroXai/pii-masker))

3. **LLM-based reasoning (`ai_service.py`)**
   - Compliance summary generation: takes detected-entity counts + risk level, produces human-readable observations/risks/remediation
   - Grounded Q&A via RAG-lite: local TF-IDF chunking + retrieval (no embeddings API) + chat model generation
   - **Why TF-IDF instead of embeddings?** Groq's API has no embeddings endpoint; TF-IDF runs locally, instantly, costs nothing, and works identically on any LLM provider — a deliberate simplicity/portability choice

**Why not a single end-to-end LLM call?** Sending raw sensitive data to a third-party LLM API purely to detect it is itself a compliance smell. Regex+checksums are strictly more reliable for fixed-format identifiers. The LLM is reserved for the parts that genuinely need language understanding.

---

## 📊 Multi-Document & Warehouse Features

**Dashboard tab:**
- Aggregated risk counts, average risk score across all uploaded documents
- Bar chart of sensitive data types found across all documents
- One table row per document showing risk level, total findings, breakdown by severity

**Warehouse export:**
- **Parquet**: read natively by Apache Spark, Hive, Presto/Trino, DuckDB, Snowflake, BigQuery, Redshift Spectrum. Drop the file into an S3/ADLS/GCS landing zone and point an external table at it.
- **Excel**: for ad-hoc analysis or sharing with non-technical stakeholders (compliance/legal)
- **CSV**: universal fallback, importable everywhere

**Sensitive values are masked in every export** (type, position, risk weight are included; the actual PII value is redacted) — a compliance tool should not be the one leaking raw PII into a downstream warehouse.

---

## 🧩 Challenges Faced

- **False positives / ambiguous formats**: a bare 12-digit number could be Aadhaar, bank account, or part of a card number. Addressed by requiring Aadhaar's standard spaced `XXXX XXXX XXXX` format with lookaround guards, anchoring bank-account detection to nearby "account" keywords, and validating card numbers with Luhn.
- **Overlapping matches corrupting redaction**: when two detectors matched overlapping spans, naively replacing each span independently could corrupt surrounding text. Solved by merging overlapping spans before masking.
- **Balancing detection recall vs. noise**: broad patterns (e.g., any 13-19 digit run for card numbers) produced too many false positives. Adding Luhn check brought precision back up.
- **Keeping Q&A grounded without embeddings API**: naive Q&A either truncated long documents or answered from general knowledge instead of the file. Local TF-IDF chunking + retrieval solved this while staying lightweight.
- **Multi-provider LLM support**: OpenAI and Groq expose slightly different APIs (Groq has no embeddings). Solved by abstracting the chat API (`openai.OpenAI` handles both via OpenAI-compatible endpoints) and using local TF-IDF for retrieval.
- **Scanned PDF detection**: how to know if a PDF is image-based vs. text-based without manual inspection? Simple heuristic: if extractable text is very sparse relative to page count, it's likely scanned → route through OCR.

---

## 🔮 Future Improvements

- Upgrade the NER layer from spaCy's small pipeline to a fine-tuned transformer (DeBERTa-v3 or Longformer, as in PII Masker) for higher precision/recall on unstructured PII, especially in non-English or informally-written text
- Persistent vector store (FAISS/ChromaDB) instead of in-memory TF-IDF for Q&A over very large document collections
- Multi-language support for the NER layer and compliance summaries (Sarvam Translate API)
- Role-based access control and encrypted storage for uploaded documents
- Configurable detection rules per organization/jurisdiction (e.g., GDPR vs. India's DPDP Act presets)
- Automated deployment (Streamlit Community Cloud / Render / AWS) with CI for regression-testing detection accuracy on a labeled test set
- Advanced data masking/tokenization for structured PII (preserve entity relationships for analytics)
- Export to common SIEM/data governance platforms (Collibra, Apache Atlas, Alation)

---

## 📁 Project Structure

```
sensitive-data-compliance-assistant/
├── app.py                     # Streamlit UI
├── detectors.py               # Regex + validation detection engine
├── ner_detector.py             # Optional spaCy NER layer
├── risk_classifier.py         # Risk scoring logic
├── document_parser.py         # Multi-format document parsing
├── ocr_service.py              # Sarvam Vision + pytesseract OCR
├── ai_service.py               # Provider-agnostic LLM (OpenAI/Groq)
├── warehouse_export.py         # Parquet/Excel/CSV export for BI
├── redaction.py                # Sensitive-data masking
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container config
├── .env.example                # Environment variable template
├── sample_data/
│   └── sample_document.txt    # Synthetic test document
└── README.md
```

---

## ⚠️ Important Notes

- **Sample data**: `sample_data/sample_document.txt` contains entirely fictitious names, numbers, and keys generated for demo/testing purposes only.
- **API keys**: Never commit real API keys to git. Use the sidebar text boxes or environment variables at runtime.
- **Sarvam Vision SDK**: Optional but recommended for production OCR. Install separately: `pip install git+https://github.com/sarvamai/python-sdk.git`. Without it, scanned PDFs return whatever text pypdf can extract, and you can only OCR plain PNG/JPG images locally via pytesseract.
- **Performance**: The app is designed for single-session document batches (tens of files). For persistent, multi-user deployments, consider adding a database backend and role-based access control.

---

## 📝 License & Attribution

This project uses:
- **spaCy** for NER (`en_core_web_sm`) — Apache 2.0
- **OpenAI API** for LLM chat — OpenAI's API terms
- **Groq API** for LLM chat — Groq's API terms
- **Sarvam Vision** for OCR — Sarvam AI's terms
- **scikit-learn** for TF-IDF retrieval — BSD 3-Clause

See individual licenses for details.

---

Made with ❤️ for the privacy-conscious developer community
