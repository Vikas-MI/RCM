from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.insurance import InsurancePolicy
    from app.models.payer import Payer


class EligibilityRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "eligibility_requests"
    __table_args__ = (
        Index("ix_elig_req_patient_id", "patient_id"),
        Index("ix_elig_req_policy_id", "insurance_policy_id"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    encounter_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True
    )
    insurance_policy_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("insurance_policies.id"), nullable=False
    )
    payer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payers.id"), nullable=False
    )
    member_id: Mapped[str] = mapped_column(String(128), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    request_status: Mapped[str] = mapped_column(String(64), nullable=False)
    scenario: Mapped[str] = mapped_column(String(64), nullable=False)
    request_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    patient: Mapped["Patient"] = relationship(back_populates="eligibility_requests")
    insurance_policy: Mapped["InsurancePolicy"] = relationship(
        back_populates="eligibility_requests"
    )
    response: Mapped[Optional["EligibilityResponse"]] = relationship(
        back_populates="request", uselist=False
    )


class EligibilityResponse(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "eligibility_responses"

    eligibility_request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("eligibility_requests.id"),
        unique=True,
        nullable=False,
    )
    eligibility_status: Mapped[str] = mapped_column(String(64), nullable=False)
    payer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    member_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    coverage_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    coverage_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    copay: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    deductible: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    deductible_remaining: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    coinsurance: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    benefits: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="MOCK", nullable=False)
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    request: Mapped["EligibilityRequest"] = relationship(back_populates="response")


class EligibilityHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "eligibility_history"
    __table_args__ = (Index("ix_elig_hist_patient_id", "patient_id"),)

    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    insurance_policy_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("insurance_policies.id"), nullable=False
    )
    eligibility_request_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("eligibility_requests.id"), nullable=False
    )
    previous_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    current_status: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="eligibility_history")
    insurance_policy: Mapped["InsurancePolicy"] = relationship(
        back_populates="eligibility_history"
    )
