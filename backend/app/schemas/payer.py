from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PayerCreate(BaseModel):
    payer_name: str
    payer_code: str
    description: str | None = None
    is_active: bool = True


class PayerUpdate(BaseModel):
    payer_name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class PayerOut(ORMModel):
    id: UUID
    payer_name: str
    payer_code: str
    description: str | None = None
    is_active: bool
    created_at: datetime | None = None


class PayerListOut(BaseModel):
    items: list[PayerOut]
    total: int = Field(ge=0)


class PayerMappingCreate(BaseModel):
    internal_payer_id: UUID
    external_payer_identifier: str
    mapping_source: str = "SYNTHETIC"
    is_active: bool = True


class PayerMappingOut(ORMModel):
    id: UUID
    internal_payer_id: UUID
    external_payer_identifier: str
    mapping_source: str
    is_active: bool
