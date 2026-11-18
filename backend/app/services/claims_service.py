from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.integrations.rag.policy_assistant import draft_appeal_letter
from app.models.claim import Appeal, Claim, Denial
from app.models.patient import Patient


def list_claims(db: Session) -> list[Claim]:
    return list(
        db.scalars(
            select(Claim)
            .options(joinedload(Claim.denials), joinedload(Claim.appeals))
            .order_by(Claim.created_at.desc())
        )
        .unique()
        .all()
    )


def list_denials(db: Session) -> list[Denial]:
    return list(
        db.scalars(
            select(Denial)
            .options(joinedload(Denial.claim))
            .order_by(Denial.created_at.desc())
        )
        .unique()
        .all()
    )


def create_appeal_from_denial(db: Session, denial_id: UUID) -> Appeal:
    denial = db.scalar(
        select(Denial)
        .options(joinedload(Denial.claim).joinedload(Claim.patient))
        .where(Denial.id == denial_id)
    )
    if not denial:
        raise HTTPException(404, "Denial not found")
    claim = denial.claim
    patient: Patient | None = claim.patient if claim else None
    name = (
        f"{patient.first_name} {patient.last_name}" if patient else "Unknown Patient"
    )
    clinical = (
        f"Service date {claim.service_date}. CPT {claim.cpt_codes}. "
        f"Diagnoses {claim.diagnosis_codes}. Notes: {claim.notes or 'n/a'}"
    )
    draft = draft_appeal_letter(
        patient_name=name,
        claim_number=claim.claim_number,
        denial_code=denial.denial_code,
        denial_reason=denial.denial_reason,
        clinical_summary=clinical,
    )
    appeal = Appeal(
        claim_id=claim.id,
        denial_id=denial.id,
        appeal_status="draft",
        appeal_letter=draft["appeal_letter"],
        policy_citations=draft["policy_citations"],
        ai_generated=True,
    )
    claim.claim_status = "appealed"
    db.add(appeal)
    db.commit()
    db.refresh(appeal)
    return appeal


def seed_claims_bundle(db: Session) -> dict:
    """Create demo claims/denials tied to existing patients."""
    patients = list(db.scalars(select(Patient).order_by(Patient.last_name)).all())
    if len(patients) < 1:
        return {"created_claims": 0, "note": "No patients — run FHIR sync first"}

    existing = db.scalar(select(Claim).limit(1))
    if existing:
        return {"created_claims": 0, "note": "Claims already seeded"}

    ava = next((p for p in patients if p.first_name == "Ava"), patients[0])
    liam = next((p for p in patients if p.first_name == "Liam"), patients[-1])

    c1 = Claim(
        patient_id=ava.id,
        claim_number="CLM-2026-1001",
        claim_status="denied",
        service_date=date(2026, 3, 12),
        cpt_codes=["72148"],
        diagnosis_codes=["M54.5"],
        billed_amount=Decimal("450.00"),
        paid_amount=Decimal("0.00"),
        notes="Lumbar MRI denied for medical necessity",
        source="MOCK",
    )
    c2 = Claim(
        patient_id=liam.id,
        claim_number="CLM-2026-1002",
        claim_status="paid",
        service_date=date(2026, 2, 20),
        cpt_codes=["99213"],
        diagnosis_codes=["M54.5"],
        billed_amount=Decimal("185.00"),
        paid_amount=Decimal("142.00"),
        notes="Office visit paid",
        source="MOCK",
    )
    c3 = Claim(
        patient_id=ava.id,
        claim_number="CLM-2026-1003",
        claim_status="submitted",
        service_date=date(2026, 4, 1),
        cpt_codes=["97110"],
        diagnosis_codes=["M54.5"],
        billed_amount=Decimal("120.00"),
        paid_amount=None,
        notes="PT session — pending payer",
        source="MOCK",
    )
    db.add_all([c1, c2, c3])
    db.flush()
    d1 = Denial(
        claim_id=c1.id,
        denial_code="CO-50",
        denial_reason="Not deemed a medical necessity",
        category="medical_necessity",
        denied_amount=Decimal("450.00"),
        denial_date=date(2026, 3, 20),
        details={"source": "MOCK_EOB"},
        is_appealable=True,
    )
    db.add(d1)
    db.commit()
    return {"created_claims": 3, "created_denials": 1}
