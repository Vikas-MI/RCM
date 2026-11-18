from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.insurance import InsurancePolicy


class Payer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payers"
    __table_args__ = (Index("ix_payers_payer_code", "payer_code", unique=True),)

    payer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payer_code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    mappings: Mapped[list["PayerMapping"]] = relationship(back_populates="payer")
    insurance_policies: Mapped[list["InsurancePolicy"]] = relationship(
        back_populates="payer"
    )


class PayerMapping(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payer_mappings"
    __table_args__ = (Index("ix_payer_mappings_external", "external_payer_identifier"),)

    internal_payer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("payers.id"), nullable=False
    )
    external_payer_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    mapping_source: Mapped[str] = mapped_column(
        String(64), default="SYNTHETIC", nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    payer: Mapped["Payer"] = relationship(back_populates="mappings")
