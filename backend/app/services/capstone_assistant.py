"""End-to-end Smart RCM Assistant — stitches FHIR + docs + RAG + claims."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.integrations.rag.policy_assistant import ask_policy
from app.models.claim import Appeal, Claim, Denial
from app.models.document import HealthcareDocument
from app.models.eligibility import EligibilityRequest
from app.models.patient import Patient


_DISCLAIMER = (
    "CAPSTONE MOCK ASSISTANT – Combines local data + synthetic policy RAG. "
    "Not real clinical, billing, or legal advice."
)


def ask_capstone(
    db: Session, *, question: str, patient_id: UUID | None = None
) -> dict[str, Any]:
    q = question.strip()
    context_bits: list[str] = []
    modules_used: list[str] = []

    # Module: patients / FHIR store
    patient_count = db.scalar(select(func.count()).select_from(Patient)) or 0
    context_bits.append(f"Patients in DB: {patient_count}")
    modules_used.append("fhir_sync_store")

    patient = None
    if patient_id:
        patient = db.get(Patient, patient_id)
    else:
        # Heuristic: name mention
        for p in db.scalars(select(Patient)).all():
            full = f"{p.first_name} {p.last_name}".lower()
            if p.first_name.lower() in q.lower() or full in q.lower():
                patient = p
                break

    if patient:
        context_bits.append(
            f"Focus patient: {patient.first_name} {patient.last_name} "
            f"(EHR {patient.external_ehr_patient_id})"
        )
        modules_used.append("patient_chart")

        elig = db.scalars(
            select(EligibilityRequest)
            .where(EligibilityRequest.patient_id == patient.id)
            .order_by(EligibilityRequest.requested_at.desc())
            .limit(3)
        ).all()
        if elig:
            context_bits.append(
                "Recent eligibility: "
                + ", ".join(f"{e.scenario}/{e.request_status}" for e in elig)
            )
            modules_used.append("eligibility")

        docs = db.scalars(
            select(HealthcareDocument)
            .where(HealthcareDocument.patient_id == patient.id)
            .limit(3)
        ).all()
        if docs:
            context_bits.append(
                "Documents: "
                + ", ".join(f"{d.doc_type}:{d.ocr_status}" for d in docs)
            )
            modules_used.append("document_ocr")

        claims = db.scalars(
            select(Claim)
            .options(joinedload(Claim.denials))
            .where(Claim.patient_id == patient.id)
        ).unique().all()
        if claims:
            context_bits.append(
                "Claims: "
                + ", ".join(f"{c.claim_number}={c.claim_status}" for c in claims)
            )
            modules_used.append("claims")
            for c in claims:
                for d in c.denials:
                    context_bits.append(
                        f"Denial {d.denial_code} on {c.claim_number}: {d.denial_reason}"
                    )
                    modules_used.append("denials")

    # Module: policy RAG
    rag = ask_policy(q, top_k=3)
    modules_used.append("policy_rag")

    # Module: appeals inventory
    appeal_count = db.scalar(select(func.count()).select_from(Appeal)) or 0
    denial_count = db.scalar(select(func.count()).select_from(Denial)) or 0
    context_bits.append(f"Open denials: {denial_count}, appeals drafted: {appeal_count}")
    modules_used.append("appeals")

    answer = (
        "Smart RCM Capstone Assistant (MOCK)\n\n"
        f"Question: {q}\n\n"
        "What I see in your local learning DB:\n"
        + "\n".join(f"• {b}" for b in context_bits)
        + "\n\nPolicy assistant says:\n"
        + rag["answer"]
        + f"\n\n{_DISCLAIMER}"
    )

    return {
        "answer": answer,
        "modules_used": sorted(set(modules_used)),
        "citations": rag.get("citations", []),
        "patient_id": str(patient.id) if patient else None,
        "disclaimer": _DISCLAIMER,
    }
