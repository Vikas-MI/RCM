"""Seed synthetic demo data for learning.

Usage:
  cd backend && source .venv/bin/activate
  python -m app.seed.run --reset
"""

from __future__ import annotations

import argparse

from sqlalchemy import delete, select, text

from app.core.database import Base, SessionLocal, engine
from app.models import (
    Appeal,
    Claim,
    Denial,
    EligibilityHistory,
    EligibilityRequest,
    EligibilityResponse,
    Encounter,
    HealthcareDocument,
    InsurancePolicy,
    Patient,
    Payer,
    PayerMapping,
)
from app.services import claims_service, document_service, sync_service


def reset_tables(db) -> None:
    for table in [
        Appeal,
        Denial,
        Claim,
        HealthcareDocument,
        EligibilityHistory,
        EligibilityResponse,
        EligibilityRequest,
        InsurancePolicy,
        Encounter,
        PayerMapping,
        Payer,
        Patient,
    ]:
        db.execute(delete(table))
    db.commit()


def seed_payers(db) -> None:
    payers = [
        ("Acme Health Insurance", "PAYER001", "Synthetic commercial payer"),
        ("Blue Ridge Mutual", "PAYER002", "Synthetic mutual plan"),
        ("Summit Care Plan", "PAYER003", "Synthetic regional plan"),
    ]
    for name, code, desc in payers:
        existing = db.scalar(select(Payer).where(Payer.payer_code == code))
        if existing:
            continue
        payer = Payer(payer_name=name, payer_code=code, description=desc, is_active=True)
        db.add(payer)
        db.flush()
        db.add(
            PayerMapping(
                internal_payer_id=payer.id,
                external_payer_identifier=code,
                mapping_source="SYNTHETIC",
            )
        )
    db.commit()


def seed_documents(db) -> None:
    patients = list(db.scalars(select(Patient)).all())
    by_first = {p.first_name: p for p in patients}
    samples = [
        ("ava-insurance-card.pdf", "insurance_card", "Ava"),
        ("ava-eob-mri.pdf", "eob", "Ava"),
        ("liam-progress-note.pdf", "medical_record", "Liam"),
        ("sofia-cms1500.pdf", "cms1500", "Sofia"),
    ]
    for filename, doc_type, first in samples:
        pid = by_first[first].id if first in by_first else None
        document_service.extract_document(
            db, filename=filename, doc_type=doc_type, patient_id=pid
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Clear demo tables first")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        if args.reset:
            reset_tables(db)
        seed_payers(db)
        # Default POC path: Mock Epic → Postgres (patient/encounter/coverage + EHR ids)
        ehr = sync_service.sync_all(db, use_mock_only=True, ehr_source="epic")
        availity = sync_service.ensure_availity_payer_mappings(db)
        seed_documents(db)
        claims = claims_service.seed_claims_bundle(db)
        print(
            "Seed complete:",
            {
                "ehr": ehr,
                "availity_mappings": availity,
                "claims": claims,
                "documents": "seeded",
            },
        )
        print(
            "Demo: http://localhost:3001/walkthrough "
            "(Mock Epic → Postgres → Mock Availity eligibility). NOT live."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
