from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient


class Encounter(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "encounters"
    __table_args__ = (
        Index("ix_encounters_patient_id", "patient_id"),
        Index("ix_encounters_external_id", "external_ehr_encounter_id"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    external_ehr_encounter_id: Mapped[Optional[str]] = mapped_column(
        String(128), unique=True, nullable=True
    )
    encounter_type: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    encounter_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    encounter_class: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_fhir_resource: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="encounters")
