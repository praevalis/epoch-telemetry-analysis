from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import BOOLEAN, DOUBLE_PRECISION, INTEGER, TEXT, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .machine import Machine


class RawTelemetry(Base):
    """Immutable ledger of raw ingested machine logs."""

    __tablename__ = 'raw_telemetry'

    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    machine_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey('machines.id', ondelete='RESTRICT'), primary_key=True
    )

    machine: Mapped['Machine'] = relationship(back_populates='raw_telemetry_logs')

    cpu_r: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    mem_u: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    mem_u_e: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    disk_u: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    disk_wa: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)

    load_1: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)

    disk_r: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    disk_w: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    disk_rb: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    eth1_pi: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)

    tcp_use: Mapped[int] = mapped_column(INTEGER, nullable=False)
    tcp_tw: Mapped[int] = mapped_column(INTEGER, nullable=False)

    retransegs: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    tcp_timeouts: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    out_rsts: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)


class TelemetryAnalysis(Base):
    """Stores the derived analysis results post-processing."""

    __tablename__ = 'telemetry_analysis'

    time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), primary_key=True)
    machine_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey('machines.id', ondelete='RESTRICT'), primary_key=True
    )

    machine: Mapped['Machine'] = relationship(back_populates='telemetry_analysis_logs')

    anomaly_score: Mapped[float] = mapped_column(DOUBLE_PRECISION, nullable=False)
    is_anomaly: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    model_version: Mapped[str] = mapped_column(TEXT, nullable=False)
    window_size_s: Mapped[int] = mapped_column(INTEGER, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
