from typing import Protocol
from uuid import UUID

from .schemas import RawTelemetryCreate, RawTelemetryFilterParams, RawTelemetryResponse

# NOTE: Update and delete operations are not allowed for RawTelemetry entries.
# Therefore, only create and read operations (with their batch alternatives) are allowed.


class IRawTelemetryRepository(Protocol):
    """Generic contract for RawTelemetry database operations."""

    async def create(self, payload: RawTelemetryCreate) -> RawTelemetryResponse:
        """Creates a raw telemetry entry.

        Args:
            payload: Data to use for creation.

        Returns:
            Created raw telemetry entry.
        """
        ...

    async def create_many(self, payload: list[RawTelemetryCreate]) -> int:
        """Batch creates raw telemetry entries.

        Args:
            payload: Sequence of payloads.

        Returns:
            Count of created entries.
        """
        ...

    async def get_many_for_machine(
        self, machine_id: UUID, filter_params: RawTelemetryFilterParams
    ) -> tuple[list[RawTelemetryResponse], int]:
        """Retrives raw telemetry entries for a machine.

        Args:
            machine_id: ID for the machine.
            filter_params: Filter criteria.

        Returns:
            Retrieved raw telemetry entries and their count.
        """
        ...
