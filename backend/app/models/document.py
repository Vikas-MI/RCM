from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class HealthcareDocument(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Uploaded / synthetic medical or billing document + OCR result."""

    __tablename__ = "healthcare_documents"

    patient_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # insurance_card | eob | medical_record | cms1500
    mime_type: Mapped[str] = mapped_column(String(128), default="application/pdf")
    source: Mapped[str] = mapped_column(String(64), default="MOCK")
    ocr_provider: Mapped[str] = mapped_column(
        String(64), default="MOCK_AZURE_DI"
    )  # MOCK_AZURE_DI | AZURE_DI
    ocr_status: Mapped[str] = mapped_column(
        String(32), default="pending"
    )  # pending | extracted | failed
    extracted_fields: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    raw_ocr: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    patient: Mapped[Optional["Patient"]] = relationship()
