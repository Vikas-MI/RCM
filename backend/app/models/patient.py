from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.encounter import Encounter
    from app.models.insurance import InsurancePolicy
    from app.models.eligibility import EligibilityRequest, EligibilityHistory


class Patient(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_external_ehr_patient_id", "external_ehr_patient_id"),
        Index("ix_patients_last_name", "last_name"),
    )

    external_ehr_patient_id: Mapped[Optional[str]] = mapped_column(
        String(128), unique=True, nullable=True
    )
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    raw_fhir_resource: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    source: Mapped[str] = mapped_column(String(64), default="MOCK", nullable=False)

    encounters: Mapped[list["Encounter"]] = relationship(back_populates="patient")
    insurance_policies: Mapped[list["InsurancePolicy"]] = relationship(
        back_populates="patient"
    )
    eligibility_requests: Mapped[list["EligibilityRequest"]] = relationship(
        back_populates="patient"
    )
    eligibility_history: Mapped[list["EligibilityHistory"]] = relationship(
        back_populates="patient"
    )
