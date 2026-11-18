from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.documents.mock_azure_di import (
    AzureDocumentIntelligenceStub,
    MockAzureDocumentIntelligence,
)
from app.models.document import HealthcareDocument


def list_documents(db: Session, patient_id: UUID | None = None) -> list[HealthcareDocument]:
    stmt = select(HealthcareDocument).order_by(HealthcareDocument.created_at.desc())
    if patient_id:
        stmt = stmt.where(HealthcareDocument.patient_id == patient_id)
    return list(db.scalars(stmt).all())


def extract_document(
    db: Session,
    *,
    filename: str,
    doc_type: str,
    patient_id: UUID | None = None,
    use_azure: bool = False,
    hint: dict | None = None,
) -> HealthcareDocument:
    provider = (
        AzureDocumentIntelligenceStub() if use_azure else MockAzureDocumentIntelligence()
    )
    result = provider.extract(doc_type=doc_type, filename=filename, hint=hint)
    doc = HealthcareDocument(
        patient_id=patient_id,
        filename=filename,
        doc_type=doc_type,
        source="MOCK",
        ocr_provider=result.get("provider", "MOCK_AZURE_DI"),
        ocr_status="extracted" if result.get("fields") else "failed",
        extracted_fields=result.get("fields"),
        raw_ocr=result,
        notes=result.get("message"),
        extracted_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
