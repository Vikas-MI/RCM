from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    external_ehr_patient_id: str | None = None
    source: str = "MANUAL"


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None


class PatientOut(ORMModel):
    id: UUID
    external_ehr_patient_id: str | None = None
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    source: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PatientListOut(BaseModel):
    items: list[PatientOut]
    total: int = Field(ge=0)
