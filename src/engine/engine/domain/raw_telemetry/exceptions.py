from datetime import datetime
from typing import Literal
from uuid import UUID

from engine.domain.common import DomainException


# Inherits from ValueError because it can be used inside Pydantic validators.
class RawTelemetryTimestampError(DomainException, ValueError):
    def __init__(self, timestamp: datetime, direction: Literal['past', 'future']) -> None:
        self.timestamp = timestamp
        self.direction = direction

        message = f'Invalid telemetry timestamp [{self.timestamp}]: '
        message += (
            'Timestamp is older than 24-hour retention window.'
            if self.direction == 'past'
            else 'Timestamp exceeds the 5-minute future clock drift allowance.'
        )
        super().__init__(message)


class RawTelemetryNotFoundError(DomainException):
    def __init__(self, entry_id: UUID) -> None:
        super().__init__(f'Raw telemetry with ID {entry_id} not found.')
        self.entry_id = entry_id
