"""CMS Policy RAG assistant (mock LLM answer from retrieved chunks)."""

from __future__ import annotations

from typing import Any

from app.integrations.rag.cms_policies import CMS_POLICY_CHUNKS
from app.integrations.rag.vector_store import LocalVectorStore

_DISCLAIMER = (
    "MOCK RAG – Synthetic CMS policies only. Not legal/medical advice. "
    "Not connected to real CMS.gov."
)

_STORE: LocalVectorStore | None = None


def _store() -> LocalVectorStore:
    global _STORE
    if _STORE is None:
        _STORE = LocalVectorStore(CMS_POLICY_CHUNKS)
    return _STORE


def ask_policy(question: str, top_k: int = 3) -> dict[str, Any]:
    hits = _store().search(question, top_k=top_k)
    if not hits or hits[0]["score"] <= 0:
        return {
            "answer": (
                "I could not find a matching synthetic policy chunk. Try asking about "
                "MRI back pain, physical therapy, medical necessity (CO-50), prior auth, "
                "or appeals. " + _DISCLAIMER
            ),
            "citations": [],
            "disclaimer": _DISCLAIMER,
            "mode": "rag_mock",
        }

    bullets = []
    citations = []
    for h in hits:
        citations.append(
            {
                "id": h["id"],
                "title": h["title"],
                "policy_id": h["policy_id"],
                "category": h["category"],
                "score": h["score"],
                "snippet": h["text"][:280] + ("…" if len(h["text"]) > 280 else ""),
            }
        )
        bullets.append(f"- ({h['policy_id']}) {h['text'][:220]}…")

    answer = (
        f"Based on synthetic policy lookup for: “{question.strip()}”\n\n"
        + "\n".join(bullets)
        + f"\n\n{_DISCLAIMER}"
    )
    return {
        "answer": answer,
        "citations": citations,
        "disclaimer": _DISCLAIMER,
        "mode": "rag_mock",
    }


def draft_appeal_letter(
    *,
    patient_name: str,
    claim_number: str,
    denial_code: str,
    denial_reason: str,
    clinical_summary: str,
) -> dict[str, Any]:
    rag = ask_policy(
        f"appeal medical necessity {denial_code} {denial_reason} {clinical_summary}",
        top_k=3,
    )
    cites = [c["policy_id"] for c in rag["citations"]]
    letter = f"""RE: Appeal of claim {claim_number} — Denial {denial_code}

Dear Appeals Reviewer,

We respectfully request reconsideration of the denial for patient {patient_name}.

Denial: {denial_code} — {denial_reason}

Clinical summary:
{clinical_summary}

Coverage support (synthetic citations for learning):
{chr(10).join(f"- {c}" for c in cites) or "- (no citations retrieved)"}

Based on the attached documentation and the coverage criteria above, we ask that
this claim be reprocessed for payment.

Sincerely,
Smart RCM Appeals Desk (MOCK AI DRAFT)

{_DISCLAIMER}
"""
    return {
        "appeal_letter": letter.strip(),
        "policy_citations": rag["citations"],
        "disclaimer": _DISCLAIMER,
    }
