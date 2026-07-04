from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Index, func, text
from sqlalchemy.dialects.postgresql import BOOLEAN, TEXT, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .api_key import ApiKey
    from .telemetry import RawTelemetry, TelemetryAnalysis


class Machine(Base):
    """Represents a client's identity."""

    __tablename__ = 'machines'

    __table_args__ = (
        CheckConstraint(
            '(is_active = true AND deleted_at IS NULL) OR '
            '(is_active = false AND deleted_at IS NOT NULL)',
            name='chk_deleted_at',
        ),
        Index(
            'ix_machines_name_unique_active',
            'name',
            unique=True,
            postgresql_where=text('deleted_at IS NULL'),
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    api_keys: Mapped[list['ApiKey']] = relationship(
        back_populates='machine', cascade='all, delete-orphan', passive_deletes=True
    )
    raw_telemetry_logs: Mapped[list['RawTelemetry']] = relationship(
        back_populates='machine', passive_deletes=True
    )
    telemetry_analysis_logs: Mapped[list['TelemetryAnalysis']] = relationship(
        back_populates='machine', passive_deletes=True
    )
