from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.encounter import Encounter
    from app.models.payer import Payer


class Claim(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "claims"

    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    encounter_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True
    )
    payer_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payers.id"), nullable=True
    )
    claim_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    claim_status: Mapped[str] = mapped_column(
        String(32), default="submitted"
    )  # draft | submitted | paid | denied | appealed
    service_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cpt_codes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    diagnosis_codes: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    billed_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    paid_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="MOCK")

    patient: Mapped["Patient"] = relationship()
    encounter: Mapped[Optional["Encounter"]] = relationship()
    payer: Mapped[Optional["Payer"]] = relationship()
    denials: Mapped[list["Denial"]] = relationship(back_populates="claim")
    appeals: Mapped[list["Appeal"]] = relationship(back_populates="claim")


class Denial(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "denials"

    claim_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("claims.id"), nullable=False
    )
    denial_code: Mapped[str] = mapped_column(String(32), nullable=False)  # CARC
    denial_reason: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(64), default="medical_necessity"
    )  # eligibility | coding | medical_necessity | auth | other
    denied_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    denial_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_appealable: Mapped[bool] = mapped_column(Boolean, default=True)

    claim: Mapped["Claim"] = relationship(back_populates="denials")
    appeals: Mapped[list["Appeal"]] = relationship(back_populates="denial")


class Appeal(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "appeals"

    claim_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("claims.id"), nullable=False
    )
    denial_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("denials.id"), nullable=False
    )
    appeal_status: Mapped[str] = mapped_column(
        String(32), default="draft"
    )  # draft | submitted | won | lost
    appeal_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    policy_citations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    claim: Mapped["Claim"] = relationship(back_populates="appeals")
    denial: Mapped["Denial"] = relationship(back_populates="appeals")
