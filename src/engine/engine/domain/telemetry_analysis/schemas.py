from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator

from engine.domain.common import BaseDomainModel, BaseQueryModel

from .exceptions import TelemetryAnalysisTimestampError


class TelemetryAnalysisCreate(BaseDomainModel):
    time: datetime
    machine_id: UUID

    anomaly_score: float = Field(ge=0.0, le=1.0)
    is_anomaly: bool

    model_version: str
    window_size_s: int

    @field_validator('time', mode='after')
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        """Validates timestamp against current UTC timestamp."""

        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)

        now = datetime.now(tz=UTC)

        if value > (now + timedelta(minutes=5)):
            # Analysis records cannot be created in future.
            # The 5 minutes timedelta accounts for potential clock drift.
            raise TelemetryAnalysisTimestampError(value)

        return value


class TelemetryAnalysisResponse(BaseDomainModel):
    time: datetime
    machine_id: UUID

    anomaly_score: float
    is_anomaly: bool

    model_version: str
    window_size_s: int
    processed_at: datetime


class TelemetryAnalysisFilterParams(BaseQueryModel):
    is_anomaly: bool | None = None
    model_version: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    sort_by: Literal['time'] = 'time'
