from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from engine.domain.common import BaseDomainModel, BaseQueryModel

from .exceptions import RawTelemetryTimestampError


class RawTelemetryCreate(BaseDomainModel):
    time: datetime  # Accepts UNIX timestamp and converts it to native datetime
    machine_id: UUID

    cpu_r: float = Field(ge=0.0, le=100.0)
    mem_u: float = Field(ge=0.0, le=100.0)
    mem_u_e: float = Field(ge=0.0, le=100.0)
    disk_u: float = Field(ge=0.0, le=100.0)
    disk_wa: float = Field(ge=0.0, le=100.0)

    load_1: float = Field(ge=0.0)

    disk_r: float = Field(ge=0.0)
    disk_w: float = Field(ge=0.0)
    disk_rb: float = Field(ge=0.0)
    eth1_pi: float = Field(ge=0.0)

    tcp_use: int = Field(ge=0, le=4194304)
    tcp_tw: int = Field(ge=0, le=4194304)

    retransegs: float = Field(ge=0.0)
    tcp_timeouts: float = Field(ge=0.0)
    out_rsts: float = Field(ge=0.0)

    @field_validator('time', mode='after')
    @classmethod
    def validate_timestamp_window(cls, value: datetime) -> datetime:
        """Validates timestamp against current UTC timestamp."""

        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)

        now = datetime.now(UTC)

        if value < (now - timedelta(days=1)):
            raise RawTelemetryTimestampError(value, 'past')
        if value > (now + timedelta(minutes=5)):
            raise RawTelemetryTimestampError(value, 'future')

        return value


class RawTelemetryResponse(BaseDomainModel):
    id: UUID
    time: datetime
    machine_id: UUID

    cpu_r: float
    mem_u: float
    mem_u_e: float
    disk_u: float
    disk_wa: float

    load_1: float

    disk_r: float
    disk_w: float
    disk_rb: float
    eth1_pi: float

    tcp_use: int
    tcp_tw: int

    retransegs: float
    tcp_timeouts: float
    out_rsts: float


class RawTelemetryFilterParams(BaseQueryModel):
    start_time: datetime | None
    end_time: datetime | None
    sort_by: Literal['time'] = 'time'
