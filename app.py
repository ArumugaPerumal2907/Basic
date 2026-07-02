"""
app.py
------
Streamlit UI for the Sensitive Data Detection & Compliance Assistant.

Run with:
    streamlit run app.py
"""

import datetime
import streamlit as st

from document_parser import parse_document, SUPPORTED_EXTENSIONS
from detectors import detect_sensitive_data, summarize_findings
from risk_classifier import classify_risk, risk_color
from redaction import redact_text
from ai_service import AIService
from warehouse_export import (
    findings_to_dataframe,
    document_summary_dataframe,
    audit_log_to_dataframe,
    to_excel_bytes,
    to_parquet_bytes,
    to_csv_bytes,
)

st.set_page_config(
    page_title="Sensitive Data Detection & Compliance Assistant",
    page_icon="🛡️",
    layout="wide",
)

# --------------------------------------------------------------------------- #
# Session state init
# --------------------------------------------------------------------------- #
if "documents" not in st.session_state:
    st.session_state.documents = {}   # filename -> {text, findings, risk, summary, chat_history}
if "active_doc" not in st.session_state:
    st.session_state.active_doc = None
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []


def log_event(event: str):
    st.session_state.audit_log.append(
        {"timestamp": datetime.datetime.now().isoformat(timespec="seconds"), "event": event}
    )


def process_file(uploaded_file, sarvam_key: str, enable_ner: bool):
    """Parse + scan a single uploaded file and store the result in
    session state, keyed by filename."""
    name = uploaded_file.name
    try:
        text = parse_document(name, uploaded_file.getvalue(), sarvam_api_key=sarvam_key or None)
        findings = detect_sensitive_data(text, include_ner=enable_ner)
        risk = classify_risk(findings)
        st.session_state.documents[name] = {
            "text": text,
            "findings": findings,
            "risk": risk,
            "summary": None,
            "chat_history": [],
        }
        log_event(f"Uploaded & scanned '{name}': {len(findings)} finding(s), risk={risk['level']}")
        return True, None
    except Exception as e:
        log_event(f"Failed to process '{name}': {e}")
        return False, str(e)


# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.title("🛡️ Compliance Assistant")
    st.caption("Sensitive Data Detection & Compliance Assistant")

    st.subheader("🤖 AI Provider")
    provider = st.radio("Chat/summary provider", ["openai", "groq"], horizontal=True,
                         format_func=lambda p: {"openai": "OpenAI", "groq": "Groq"}[p])
    key_label = "OpenAI API Key" if provider == "openai" else "Groq API Key"
    api_key = st.text_input(
        key_label, type="password",
        help="Used only for the AI-generated summary and Q&A chat. "
             "Detection, risk scoring, and Q&A retrieval work without it "
             "(retrieval uses a local TF-IDF index, not an embeddings API).",
    )
    st.session_state["ai"] = AIService(provider=provider, api_key=api_key or None)

    st.divider()
    st.subheader("🖼️ OCR (optional)")
    sarvam_key = st.text_input(
        "Sarvam Vision API Key", type="password",
        help="Enables OCR for scanned PDFs and image uploads (PNG/JPG), "
             "with native support for 22 Indian languages + English. "
             "Without a key, plain PNG/JPG images still get local OCR via "
             "pytesseract (English only); scanned PDFs require this key.",
    )

    enable_ner = st.checkbox(
        "🧠 Also detect names & addresses (AI/NER)",
        value=False,
        help="Uses a local spaCy NER model to catch unstructured PII "
             "(person names, locations) that regex patterns can't express. "
             "Requires: pip install spacy && python -m spacy download en_core_web_sm",
    )
    if enable_ner:
        from ner_detector import ner_available, ner_status_message
        if not ner_available():
            st.warning(ner_status_message())

    st.divider()
    st.subheader("📄 Upload Documents")
    st.caption("Supports: " + ", ".join(sorted(SUPPORTED_EXTENSIONS)))
    uploaded_files = st.file_uploader(
        "Upload one or more files", type=SUPPORTED_EXTENSIONS, accept_multiple_files=True,
    )

    if uploaded_files:
        new_files = [f for f in uploaded_files if f.name not in st.session_state.documents]
        if new_files:
            progress = st.progress(0.0, text="Processing documents...")
            for i, f in enumerate(new_files):
                ok, err = process_file(f, sarvam_key, enable_ner)
                if not ok:
                    st.error(f"Failed to process {f.name}: {err}")
                progress.progress((i + 1) / len(new_files), text=f"Processed {f.name}")
            progress.empty()
            if not st.session_state.active_doc and st.session_state.documents:
                st.session_state.active_doc = list(st.session_state.documents.keys())[0]

    if st.session_state.documents:
        st.divider()
        st.session_state.active_doc = st.selectbox(
            "Active document (for the detail tabs)",
            options=list(st.session_state.documents.keys()),
            index=list(st.session_state.documents.keys()).index(st.session_state.active_doc)
            if st.session_state.active_doc in st.session_state.documents else 0,
        )
        if st.button("🔄 Rescan Active Document", use_container_width=True,
                      help="Re-run detection (e.g. after toggling NER)"):
            doc = st.session_state.documents[st.session_state.active_doc]
            findings = detect_sensitive_data(doc["text"], include_ner=enable_ner)
            doc["findings"] = findings
            doc["risk"] = classify_risk(findings)
            log_event(f"Rescanned '{st.session_state.active_doc}'")

        if st.button("🗑️ Clear All Documents", use_container_width=True):
            st.session_state.documents = {}
            st.session_state.active_doc = None
            log_event("Cleared all documents")
            st.rerun()

# --------------------------------------------------------------------------- #
# Main area
# --------------------------------------------------------------------------- #
st.title("Sensitive Data Detection & Compliance Assistant")

if not st.session_state.documents:
    st.info("👈 Upload one or more documents from the sidebar to get started.")
    st.markdown(
        """
**What this tool does**
1. Scans uploaded documents (PDF, TXT, MD, CSV, DOCX, XLSX, JSON, and
   images via OCR) for sensitive/confidential data.
2. Classifies each document's risk level (Low / Medium / High).
3. Generates an AI-written compliance & security summary via OpenAI or
   Groq, with remediation suggestions.
4. Lets you ask natural-language questions about a document, grounded in
   its actual content.
5. Aggregates results across all uploaded documents in a Dashboard tab.
6. Produces a redacted copy of any document with sensitive values masked.
7. Tracks every action in an Audit Log, exportable to Excel/Parquet/CSV
   for downstream BI or data-warehouse ingestion.
        """
    )
    st.stop()

active_name = st.session_state.active_doc
active_doc = st.session_state.documents[active_name]
findings = active_doc["findings"]
risk = active_doc["risk"]
findings_summary = summarize_findings(findings)

tab_overview, tab_findings, tab_summary, tab_qa, tab_redacted, tab_dashboard, tab_audit = st.tabs(
    ["📊 Overview", "🔎 Findings", "📝 AI Summary", "💬 Ask Questions",
     "🕶️ Redacted View", "📈 Dashboard", "🧾 Audit Log"]
)

# ------------------------------- Overview ---------------------------------- #
with tab_overview:
    st.caption(f"Viewing: **{active_name}**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Findings", risk["total_findings"])
    c2.metric("High Severity", risk["high_count"])
    c3.metric("Medium Severity", risk["medium_count"])
    c4.metric("Risk Score", risk["score"])

    st.markdown(
        f"""
        <div style="padding:16px;border-radius:10px;background-color:{risk_color(risk['level'])}22;
        border:2px solid {risk_color(risk['level'])};">
        <h3 style="color:{risk_color(risk['level'])};margin:0;">Overall Risk: {risk['level']}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Breakdown by Data Type")
    if findings_summary:
        st.bar_chart(findings_summary)
    else:
        st.write("No sensitive data types detected.")

# ------------------------------- Findings ----------------------------------- #
with tab_findings:
    st.caption(f"Viewing: **{active_name}**")
    st.subheader(f"All Findings ({len(findings)})")
    if not findings:
        st.write("✅ No sensitive data detected in this document.")
    for f in findings:
        with st.expander(f"{f.type} — `{f.value}`"):
            st.write(f"**Context:** {f.context}")
            st.write(f"**Position:** char {f.position}")
            st.write(f"**Severity weight:** {f.risk_weight}")

# ------------------------------- AI Summary --------------------------------- #
with tab_summary:
    st.caption(f"Viewing: **{active_name}**")
    st.subheader("AI-Generated Compliance & Security Summary")
    if st.button("Generate Summary"):
        try:
            with st.spinner("Generating summary..."):
                summary = st.session_state.ai.generate_compliance_summary(
                    findings_summary, risk, active_doc["text"]
                )
                active_doc["summary"] = summary
                log_event(f"Generated AI compliance summary for '{active_name}'")
        except RuntimeError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Summary generation failed: {e}")

    if active_doc["summary"]:
        st.markdown(active_doc["summary"])
        st.download_button(
            "⬇️ Download Summary", active_doc["summary"],
            f"{active_name}_compliance_summary.md", "text/markdown",
        )

# ------------------------------- Q&A ----------------------------------------- #
with tab_qa:
    st.caption(f"Viewing: **{active_name}**")
    st.subheader("Ask Questions About This Document")
    st.caption(
        'Try: "What sensitive data exists in the document?", '
        '"How many email addresses are present?", "Summarize this document."'
    )

    for msg in active_doc["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about the document...")
    if question:
        active_doc["chat_history"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    st.session_state.ai.build_index(active_doc["text"])
                    answer = st.session_state.ai.answer_question(
                        question, findings_summary, risk
                    )
                st.markdown(answer)
                active_doc["chat_history"].append({"role": "assistant", "content": answer})
                log_event(f"Q&A on '{active_name}': {question}")
            except RuntimeError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Could not answer question: {e}")

# ------------------------------- Redacted view ------------------------------- #
with tab_redacted:
    st.caption(f"Viewing: **{active_name}**")
    st.subheader("Redacted Document Preview")
    st.caption("Sensitive values are masked with [REDACTED:<type>] placeholders.")
    redacted_text = redact_text(active_doc["text"], findings)
    st.text_area("Redacted content", redacted_text, height=400)
    st.download_button(
        "⬇️ Download Redacted Document", redacted_text,
        f"{active_name}_redacted.txt", "text/plain",
    )

# ------------------------------- Dashboard ----------------------------------- #
with tab_dashboard:
    st.subheader("Cross-Document Dashboard")

    findings_by_doc = {name: d["findings"] for name, d in st.session_state.documents.items()}
    risk_by_doc = {name: d["risk"] for name, d in st.session_state.documents.items()}

    df_summary = document_summary_dataframe(risk_by_doc)
    df_findings = findings_to_dataframe(findings_by_doc)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Documents Scanned", len(st.session_state.documents))
    c2.metric("Total Findings", int(df_summary["total_findings"].sum()) if not df_summary.empty else 0)
    c3.metric("High Risk Docs", int((df_summary["risk_level"] == "High Risk").sum()) if not df_summary.empty else 0)
    c4.metric("Avg Risk Score", round(df_summary["risk_score"].mean(), 1) if not df_summary.empty else 0)

    st.subheader("Risk Level by Document")
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    st.subheader("Sensitive Data Types Across All Documents")
    if not df_findings.empty:
        type_counts = df_findings["finding_type"].value_counts()
        st.bar_chart(type_counts)
    else:
        st.write("No findings yet.")

    st.divider()
    st.subheader("📦 Export to Data Warehouse / BI Tools")
    st.caption(
        "Parquet is read natively by Apache Spark, Hive, Presto/Trino, DuckDB, "
        "and most cloud warehouses (Snowflake, BigQuery, Redshift Spectrum) — "
        "drop it into a landing bucket and point an external table at it. "
        "Excel/CSV cover ad-hoc analysis and non-technical stakeholders. "
        "Sensitive values are masked in every export."
    )
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        st.download_button(
            "⬇️ Excel (.xlsx)",
            to_excel_bytes({"Findings": df_findings, "Document Summary": df_summary}),
            "compliance_export.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with ec2:
        st.download_button(
            "⬇️ Parquet (.parquet)",
            to_parquet_bytes(df_findings),
            "compliance_findings.parquet",
            "application/octet-stream",
            use_container_width=True,
        )
    with ec3:
        st.download_button(
            "⬇️ CSV (.csv)",
            to_csv_bytes(df_findings),
            "compliance_findings.csv",
            "text/csv",
            use_container_width=True,
        )

# ------------------------------- Audit Log ------------------------------------ #
with tab_audit:
    st.subheader("Audit Log")
    st.caption("Every upload, scan, summary generation, and question is timestamped here.")

    if not st.session_state.audit_log:
        st.write("No activity yet.")
    else:
        df_audit = audit_log_to_dataframe(st.session_state.audit_log)
        search = st.text_input("Filter events", placeholder="e.g. 'scanned', a filename, 'failed'...")
        if search:
            df_audit = df_audit[df_audit["event"].str.contains(search, case=False, na=False)]
        st.dataframe(df_audit.sort_values("timestamp", ascending=False),
                     use_container_width=True, hide_index=True)

        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            st.download_button("⬇️ CSV", to_csv_bytes(df_audit), "audit_log.csv",
                                "text/csv", use_container_width=True)
        with ac2:
            st.download_button("⬇️ Excel", to_excel_bytes({"Audit Log": df_audit}),
                                "audit_log.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True)
        with ac3:
            st.download_button("⬇️ Parquet", to_parquet_bytes(df_audit), "audit_log.parquet",
                                "application/octet-stream", use_container_width=True)
