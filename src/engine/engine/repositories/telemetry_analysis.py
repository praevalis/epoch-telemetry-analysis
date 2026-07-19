from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, insert, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from engine.database.relational.models import TelemetryAnalysis
from engine.domain.telemetry_analysis import (
    ITelemetryAnalysisRepository,
    TelemetryAnalysisCreate,
    TelemetryAnalysisFilterParams,
    TelemetryAnalysisResponse,
)


class TelemetryAnalysisRepository(ITelemetryAnalysisRepository):
    """Concrete implementation for telemetry analysis data operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes telemetry analysis repository.

        Args:
            session: Injected SQLAlchemy session.
        """
        self.session = session

    async def create(self, payload: TelemetryAnalysisCreate) -> TelemetryAnalysisResponse:
        """Create a telemetry analysis record.

        Args:
            payload: Data to create record.

        Returns:
            Created telemetry analysis record.
        """
        telemetry_analysis = TelemetryAnalysis(**payload.model_dump())
        self.session.add(telemetry_analysis)

        await self.session.flush()
        await self.session.refresh(telemetry_analysis)

        return TelemetryAnalysisResponse.model_validate(telemetry_analysis)

    async def create_many(self, payload: list[TelemetryAnalysisCreate]) -> int:
        """Batch create telemetry analysis records.

        Args:
            payload: Sequence of data to create records.

        Returns:
            Count of created records.
        """
        if not payload:
            return 0

        telemetry_analysis_records = [p.model_dump() for p in payload]

        stmt = insert(TelemetryAnalysis)
        raw_result = await self.session.execute(stmt, telemetry_analysis_records)
        result = cast(CursorResult[Any], raw_result)

        return result.rowcount

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
        stmt = select(TelemetryAnalysis).where(TelemetryAnalysis.machine_id == machine_id)

        if filter_params.is_anomaly is not None:
            stmt = stmt.where(TelemetryAnalysis.is_anomaly == filter_params.is_anomaly)

        if filter_params.model_version:
            stmt = stmt.where(TelemetryAnalysis.model_version == filter_params.model_version)

        if filter_params.start_time:
            stmt = stmt.where(TelemetryAnalysis.time >= filter_params.start_time)

        if filter_params.end_time:
            stmt = stmt.where(TelemetryAnalysis.time <= filter_params.end_time)

        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = (await self.session.execute(count_stmt)).scalar_one()

        sort_column = getattr(TelemetryAnalysis, filter_params.sort_by, TelemetryAnalysis.time)
        if filter_params.sort_dir == 'asc':
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(filter_params.limit).offset(filter_params.offset)
        result = await self.session.execute(stmt)
        telemetry_analysis_records = result.scalars().all()

        return [
            TelemetryAnalysisResponse.model_validate(tar) for tar in telemetry_analysis_records
        ], total
