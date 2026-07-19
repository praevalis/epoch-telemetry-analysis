from datetime import datetime

from engine.domain.common import DomainException


class TelemetryAnalysisTimestampError(DomainException, ValueError):
    def __init__(self, timestamp: datetime) -> None:
        self.timestamp = timestamp
        super().__init__(
            f'Invalid timestamp {timestamp}: Telemetry analysis records can not be created in future.'
        )
