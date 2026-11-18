from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class DocumentExtractIn(BaseModel):
    filename: str = Field(default="sample-insurance-card.pdf")
    doc_type: str = Field(
        description="insurance_card | eob | medical_record | cms1500"
    )
    patient_id: UUID | None = None
    use_azure: bool = False
    hint: dict | None = None


class DocumentOut(ORMModel):
    id: UUID
    patient_id: UUID | None = None
    filename: str
    doc_type: str
    mime_type: str
    source: str
    ocr_provider: str
    ocr_status: str
    extracted_fields: dict | None = None
    notes: str | None = None
    extracted_at: datetime | None = None
    created_at: datetime | None = None


class DocumentListOut(BaseModel):
    items: list[DocumentOut]
    total: int
