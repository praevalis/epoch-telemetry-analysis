from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, insert, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from engine.database.relational.models import RawTelemetry
from engine.domain.raw_telemetry import (
    IRawTelemetryRepository,
    RawTelemetryCreate,
    RawTelemetryFilterParams,
    RawTelemetryResponse,
)


class RawTelemetryRepository(IRawTelemetryRepository):
    """Concrete implementation for raw telemetry data operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes raw telemetry repository.

        Args:
            session: Injected SQLAlchemy session.
        """
        self.session = session

    async def create(self, payload: RawTelemetryCreate) -> RawTelemetryResponse:
        """Creates a raw telemetry entry.

        Args:
            payload: Data to use for creation.

        Returns:
            Created raw telemetry entry.
        """
        raw_telemetry = RawTelemetry(**payload.model_dump())
        self.session.add(raw_telemetry)

        await self.session.flush()
        await self.session.refresh(raw_telemetry)

        return RawTelemetryResponse.model_validate(raw_telemetry)

    async def create_many(self, payload: list[RawTelemetryCreate]) -> int:
        """Batch creates raw telemetry entries.

        Args:
            payload: Sequence of payloads.

        Returns:
            Count of created entries.
        """
        if not payload:
            return 0

        raw_telemetry_entries = [p.model_dump() for p in payload]

        stmt = insert(RawTelemetry)
        raw_result = await self.session.execute(stmt, raw_telemetry_entries)
        result = cast(CursorResult[Any], raw_result)

        return result.rowcount

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
        stmt = select(RawTelemetry).where(RawTelemetry.machine_id == machine_id)

        if filter_params.start_time:
            stmt = stmt.where(RawTelemetry.time >= filter_params.start_time)

        if filter_params.end_time:
            stmt = stmt.where(RawTelemetry.time <= filter_params.end_time)

        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = (await self.session.execute(count_stmt)).scalar_one()

        sort_column = getattr(RawTelemetry, filter_params.sort_by, RawTelemetry.time)
        if filter_params.sort_dir == 'asc':
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(filter_params.limit).offset(filter_params.offset)

        result = await self.session.execute(stmt)
        raw_telemetry_entries = result.scalars().all()

        return [RawTelemetryResponse.model_validate(rte) for rte in raw_telemetry_entries], total
