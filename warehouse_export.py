"""
warehouse_export.py
--------------------
Exports scan results (findings across all uploaded documents) and the
audit log into formats that plug directly into common BI / data
warehouse tooling, without needing a live database connector:

- **Parquet** (.parquet) -- columnar format read natively by Apache Spark,
  Hive, Presto/Trino, DuckDB, and most cloud warehouses (Snowflake,
  BigQuery, Redshift Spectrum) with zero conversion. Drop the file into
  an S3/ADLS/GCS landing path and point an external table at it.
- **Excel** (.xlsx) -- for ad-hoc analysis or sharing with non-technical
  stakeholders (compliance/legal teams).
- **CSV** (.csv) -- universal fallback, importable everywhere.

This is intentionally file-based rather than a live DB connector, so the
assistant stays credential-free for the warehouse side and deployable
anywhere; the exported files are designed to land in a normal ingestion
path (S3 bucket + Spark/Hive external table, Power BI "Get Data > From
File", etc.).

Sensitive values are masked in every export by default (only type,
position, and severity are included) -- a compliance tool should not be
the thing that leaks raw PII into a downstream warehouse table.
"""

import io
from typing import Dict, List

import pandas as pd

from detectors import Finding


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"


def findings_to_dataframe(findings_by_doc: Dict[str, List[Finding]]) -> pd.DataFrame:
    """Flatten findings across all documents into one tabular DataFrame,
    ready for a warehouse fact table (one row per finding)."""
    rows = []
    for doc_name, findings in findings_by_doc.items():
        for f in findings:
            rows.append(
                {
                    "document": doc_name,
                    "finding_type": f.type,
                    "masked_value": _mask(f.value),
                    "char_position": f.position,
                    "risk_weight": f.risk_weight,
                }
            )
    return pd.DataFrame(
        rows,
        columns=["document", "finding_type", "masked_value", "char_position", "risk_weight"],
    )


def document_summary_dataframe(risk_by_doc: Dict[str, Dict]) -> pd.DataFrame:
    """One row per document with its overall risk classification -- the
    natural grain for a warehouse dimension/summary table."""
    rows = []
    for doc_name, risk in risk_by_doc.items():
        rows.append(
            {
                "document": doc_name,
                "risk_level": risk["level"],
                "risk_score": risk["score"],
                "high_severity_findings": risk["high_count"],
                "medium_severity_findings": risk["medium_count"],
                "low_severity_findings": risk["low_count"],
                "total_findings": risk["total_findings"],
            }
        )
    return pd.DataFrame(rows)


def audit_log_to_dataframe(audit_log: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(audit_log, columns=["timestamp", "event"])


def to_excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    """sheets: {sheet_name: dataframe} -- supports multi-sheet workbooks
    (e.g. one sheet for findings, one for the document-level summary)."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=name[:31])  # Excel sheet-name limit
    return buf.getvalue()


def to_parquet_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    return buf.getvalue()


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
