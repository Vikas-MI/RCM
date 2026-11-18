from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import ORMModel


class DenialOut(ORMModel):
    id: UUID
    claim_id: UUID
    denial_code: str
    denial_reason: str
    category: str
    denied_amount: Decimal | None = None
    denial_date: date | None = None
    is_appealable: bool
    created_at: datetime | None = None


class AppealOut(ORMModel):
    id: UUID
    claim_id: UUID
    denial_id: UUID
    appeal_status: str
    appeal_letter: str | None = None
    policy_citations: list | None = None
    ai_generated: bool
    created_at: datetime | None = None


class ClaimOut(ORMModel):
    id: UUID
    patient_id: UUID
    encounter_id: UUID | None = None
    payer_id: UUID | None = None
    claim_number: str
    claim_status: str
    service_date: date | None = None
    cpt_codes: list | None = None
    diagnosis_codes: list | None = None
    billed_amount: Decimal | None = None
    paid_amount: Decimal | None = None
    notes: str | None = None
    source: str
    denials: list[DenialOut] = []
    appeals: list[AppealOut] = []
    created_at: datetime | None = None


class ClaimListOut(BaseModel):
    items: list[ClaimOut]
    total: int


class AssistantAskIn(BaseModel):
    question: str
    patient_id: UUID | None = None


class AssistantAskOut(BaseModel):
    answer: str
    modules_used: list[str]
    citations: list
    patient_id: str | None = None
    disclaimer: str
