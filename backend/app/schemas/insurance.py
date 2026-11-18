from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class InsuranceCreate(BaseModel):
    patient_id: UUID
    payer_id: UUID
    member_id: str
    group_number: str | None = None
    policy_number: str | None = None
    policy_type: str | None = "commercial"
    relationship_to_subscriber: str | None = "self"
    coverage_status: str = "active"
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    is_primary: bool = True
    is_active: bool = True


class InsuranceUpdate(BaseModel):
    member_id: str | None = None
    group_number: str | None = None
    policy_number: str | None = None
    policy_type: str | None = None
    coverage_status: str | None = None
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class InsuranceOut(ORMModel):
    id: UUID
    patient_id: UUID
    payer_id: UUID
    member_id: str
    group_number: str | None = None
    policy_number: str | None = None
    policy_type: str | None = None
    relationship_to_subscriber: str | None = None
    coverage_status: str
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    is_primary: bool
    is_active: bool
    external_coverage_id: str | None = None
    created_at: datetime | None = None
    payer_name: str | None = None


class InsuranceListOut(BaseModel):
    items: list[InsuranceOut]
    total: int = Field(ge=0)
