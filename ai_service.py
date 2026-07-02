"""
ai_service.py
-------------
Provider-agnostic LLM service. Supports OpenAI and Groq, since both
expose an OpenAI-compatible /chat/completions API -- switching provider
is just a base_url + model swap.

Two jobs:

1. generate_compliance_summary() - turns detected findings + a text
   excerpt into a human-readable compliance/security summary.

2. Retrieval-Augmented Q&A:
   - build_index()     -> chunks the document and fits a local TF-IDF
     retriever over the chunks
   - answer_question() -> retrieves the most relevant chunks (cosine
     similarity over TF-IDF vectors) and asks the chat model to answer
     using only that context.

Why TF-IDF instead of an embeddings API for retrieval? Groq's API does
not expose an embeddings endpoint at all, so an OpenAI-only embeddings
call would silently break the moment someone switches provider. TF-IDF
retrieval runs locally in milliseconds for document-scale text, needs no
API call (zero extra cost/latency), and keeps the RAG layer identical
regardless of which chat provider is selected -- a deliberate simplicity
trade-off explained further in the README.

If no API key is configured, every public method raises a clear
RuntimeError that the UI layer catches and surfaces to the user, rather
than silently failing.
"""

import os
from typing import List, Dict, Optional

from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Provider registry: base_url=None means "use the provider SDK's default
# endpoint" (OpenAI's own API). Groq is accessed through its
# OpenAI-compatible endpoint.
PROVIDER_CONFIG = {
    "openai": {
        "base_url": None,
        "default_model": "gpt-4o-mini",
        "env_var": "OPENAI_API_KEY",
        "display_name": "OpenAI",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "env_var": "GROQ_API_KEY",
        "display_name": "Groq",
    },
}

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


class AIService:
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        provider = provider if provider in PROVIDER_CONFIG else "openai"
        self.provider = provider
        cfg = PROVIDER_CONFIG[provider]
        self.display_name = cfg["display_name"]
        self.chat_model = model or cfg["default_model"]

        self.api_key = api_key or os.environ.get(cfg["env_var"])

        self.client = None
        if self.api_key:
            client_kwargs = {"api_key": self.api_key}
            if cfg["base_url"]:
                client_kwargs["base_url"] = cfg["base_url"]
            self.client = OpenAI(**client_kwargs)

        self._chunks: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._doc_matrix = None

    # ------------------------------------------------------------------ #
    def _require_client(self):
        if not self.client:
            raise RuntimeError(
                f"No {self.display_name} API key configured. Add it in the "
                f"sidebar, or set the {PROVIDER_CONFIG[self.provider]['env_var']} "
                "environment variable."
            )

    # ------------------------------------------------------------------ #
    # Compliance summary
    # ------------------------------------------------------------------ #
    def generate_compliance_summary(
        self, findings_summary: Dict[str, int], risk: Dict, text_excerpt: str
    ) -> str:
        self._require_client()

        findings_lines = "\n".join(
            f"- {k}: {v} occurrence(s)" for k, v in findings_summary.items()
        ) or "- No sensitive data types detected."

        prompt = f"""You are a data privacy & compliance assistant. Based on the
scan results below, write a concise compliance/security report with three
sections: "Compliance Observations", "Security Risks", and "Suggested
Remediation Steps". Use short bullet points. Be specific about the types
of sensitive data found, but do NOT repeat the raw sensitive values back.

Overall Risk Level: {risk['level']} (score: {risk['score']})
High-severity finding count: {risk['high_count']}
Medium-severity finding count: {risk['medium_count']}

Detected data types:
{findings_lines}

Document excerpt (for context only, may be truncated):
\"\"\"{text_excerpt[:3000]}\"\"\"
"""
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            temperature=0.3,
        )
        return response.choices[0].message.content

    # ------------------------------------------------------------------ #
    # RAG-lite Q&A (local TF-IDF retrieval + LLM generation)
    # ------------------------------------------------------------------ #
    def _chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + CHUNK_SIZE
            chunks.append(text[start:end])
            start = end - CHUNK_OVERLAP
        return [c for c in chunks if c.strip()]

    def build_index(self, text: str):
        """Chunk the document and fit a TF-IDF vectorizer over the
        chunks. Cheap enough to call before every question -- no need to
        persist across Streamlit reruns."""
        self._chunks = self._chunk_text(text)
        if not self._chunks:
            self._vectorizer = None
            self._doc_matrix = None
            return
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._doc_matrix = self._vectorizer.fit_transform(self._chunks)

    def _top_chunks(self, question: str, k: int = 4) -> List[str]:
        if self._vectorizer is None or self._doc_matrix is None:
            return []
        q_vec = self._vectorizer.transform([question])
        sims = cosine_similarity(q_vec, self._doc_matrix)[0]
        top_idx = sims.argsort()[::-1][:k]
        return [self._chunks[i] for i in top_idx]

    def answer_question(
        self, question: str, findings_summary: Dict[str, int], risk: Dict
    ) -> str:
        self._require_client()
        if not self._chunks:
            raise RuntimeError(
                "Document index not built yet. Call build_index() first."
            )

        context_chunks = self._top_chunks(question)
        context = "\n---\n".join(context_chunks)
        findings_lines = "\n".join(
            f"- {k}: {v}" for k, v in findings_summary.items()
        ) or "- None detected."

        prompt = f"""You are a compliance assistant answering questions about a
scanned document. Use the retrieved excerpts and the sensitive-data scan
summary below to answer the user's question accurately and concisely.
If the answer isn't in the provided context, say so honestly rather than
guessing. Do not reproduce full sensitive values (e.g. full card/Aadhaar
numbers) in your answer -- refer to them by type and count instead.

Sensitive data scan summary:
{findings_lines}

Overall risk level: {risk['level']}

Retrieved document excerpts (most relevant first):
{context}

Question: {question}
"""
        response = self.client.chat.completions.create(
            model=self.chat_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.2,
        )
        return response.choices[0].message.content
