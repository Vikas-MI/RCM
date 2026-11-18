from datetime import date
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.payer import Payer
    from app.models.eligibility import EligibilityRequest, EligibilityHistory


class InsurancePolicy(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "insurance_policies"
    __table_args__ = (
        Index("ix_insurance_patient_id", "patient_id"),
        Index("ix_insurance_member_id", "member_id"),
        Index("ix_insurance_payer_id", "payer_id"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )
    payer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payers.id"), nullable=False
    )
    member_id: Mapped[str] = mapped_column(String(128), nullable=False)
    group_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    policy_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    policy_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    relationship_to_subscriber: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    coverage_status: Mapped[str] = mapped_column(
        String(64), default="active", nullable=False
    )
    coverage_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    coverage_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    external_coverage_id: Mapped[Optional[str]] = mapped_column(
        String(128), unique=True, nullable=True
    )
    raw_fhir_resource: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    patient: Mapped["Patient"] = relationship(back_populates="insurance_policies")
    payer: Mapped["Payer"] = relationship(back_populates="insurance_policies")
    eligibility_requests: Mapped[list["EligibilityRequest"]] = relationship(
        back_populates="insurance_policy"
    )
    eligibility_history: Mapped[list["EligibilityHistory"]] = relationship(
        back_populates="insurance_policy"
    )
