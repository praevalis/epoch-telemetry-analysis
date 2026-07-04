from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, VARCHAR
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .machine import Machine


class ApiKeyStatusEnum(StrEnum):
    ACTIVE = 'ACTIVE'
    REVOKED = 'REVOKED'


class ApiKey(Base):
    """Represents access keys granted to a machine."""

    __tablename__ = 'api_keys'

    __table_args__ = (
        CheckConstraint(
            "(status = 'REVOKED' AND revoked_at IS NOT NULL) OR "
            "(status = 'ACTIVE' AND revoked_at IS NULL)",
            name='chk_revoked_at',
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    hash: Mapped[str] = mapped_column(VARCHAR(64), unique=True, nullable=False)
    status: Mapped[ApiKeyStatusEnum] = mapped_column(
        Enum(ApiKeyStatusEnum, name='apikey_status_enum'),
        nullable=False,
        default=ApiKeyStatusEnum.ACTIVE,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    machine_id: Mapped[UUID] = mapped_column(ForeignKey('machines.id', ondelete='CASCADE'))
    machine: Mapped['Machine'] = relationship(back_populates='api_keys')
