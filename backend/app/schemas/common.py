from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    message: str


class IdOut(BaseModel):
    id: UUID


class TimestampOut(ORMModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None
