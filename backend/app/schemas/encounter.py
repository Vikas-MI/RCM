from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class EncounterOut(ORMModel):
    id: UUID
    patient_id: UUID
    external_ehr_encounter_id: str | None = None
    encounter_type: str | None = None
    encounter_status: str | None = None
    encounter_class: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    reason: str | None = None
    created_at: datetime | None = None


class EncounterListOut(BaseModel):
    items: list[EncounterOut]
    total: int = Field(ge=0)
