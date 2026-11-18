from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class EligibilityVerifyIn(BaseModel):
    patient_id: UUID
    insurance_policy_id: UUID
    encounter_id: UUID | None = None
    service_date: date
    scenario: str = "ACTIVE"


class EligibilityResponseOut(ORMModel):
    id: UUID
    eligibility_request_id: UUID
    eligibility_status: str
    payer_name: str | None = None
    member_id: str | None = None
    coverage_start_date: date | None = None
    coverage_end_date: date | None = None
    copay: Decimal | None = None
    deductible: Decimal | None = None
    deductible_remaining: Decimal | None = None
    coinsurance: str | None = None
    benefits: dict | None = None
    source: str
    response_message: str | None = None
    responded_at: datetime
    response_payload: dict | None = None


class EligibilityRequestOut(ORMModel):
    id: UUID
    patient_id: UUID
    encounter_id: UUID | None = None
    insurance_policy_id: UUID
    payer_id: UUID
    member_id: str
    service_date: date
    request_status: str
    scenario: str
    requested_at: datetime
    response: EligibilityResponseOut | None = None


class EligibilityHistoryOut(ORMModel):
    id: UUID
    patient_id: UUID
    insurance_policy_id: UUID
    eligibility_request_id: UUID
    previous_status: str | None = None
    current_status: str
    action: str
    details: dict | None = None
    created_at: datetime


class EligibilityListOut(BaseModel):
    items: list[EligibilityRequestOut]
    total: int = Field(ge=0)


class ScenarioListOut(BaseModel):
    scenarios: list[str]
    disclaimer: str
