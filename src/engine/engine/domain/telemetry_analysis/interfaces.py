from typing import Protocol
from uuid import UUID

from .schemas import (
    TelemetryAnalysisCreate,
    TelemetryAnalysisFilterParams,
    TelemetryAnalysisResponse,
)

# NOTE: Update and delete operations are omitted by design.
# Each record is tamper-proof evidence of a possible escalation.


class ITelemetryAnalysisRepository(Protocol):
    """Generic contract for telemetry analysis data operations."""

    async def create(self, payload: TelemetryAnalysisCreate) -> TelemetryAnalysisResponse:
        """Create a telemetry analysis record.

        Args:
            payload: Data to create record.

        Returns:
            Created telemetry analysis record.
        """
        ...

    async def create_many(self, payload: list[TelemetryAnalysisCreate]) -> int:
        """Batch create telemetry analysis records.

        Args:
            payload: Sequence of data to create records.

        Returns:
            Count of created records.
        """
        ...

    async def get_many_for_machine(
        self, machine_id: UUID, filter_params: TelemetryAnalysisFilterParams
    ) -> tuple[list[TelemetryAnalysisResponse], int]:
        """Retrieve telemetry analysis records for a machine.

        Args:
            machine_id: ID of the machine.
            filter_params: Filter criteria.

        Returns:
            Retrieved telemetry analysis records and their count.
        """
        ...
