from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from engine.database.relational.models import Machine
from engine.domain.machine import (
    IMachineRepository,
    MachineAlreadyExistsError,
    MachineCreate,
    MachineFilterParams,
    MachineNotFoundError,
    MachineResponse,
    MachineUpdate,
)


class MachineRepository(IMachineRepository):
    """Concrete implementation for machine data operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes machine repository.

        Args:
            session: Injected SQLAlchemy session.
        """
        self.session = session

    async def create(self, payload: MachineCreate) -> MachineResponse:
        """Creates a machine with provided data.

        Args:
            payload: Data to create machine.

        Returns:
            Created machine.

        Raises:
            MachineAlreadyExistsError: When a machine with the same name exists.
        """
        machine = Machine(**payload.model_dump())
        self.session.add(machine)

        try:
            await self.session.flush()

        except IntegrityError as e:
            if getattr(e.orig, 'sqlstate', None) == '23505':
                raise MachineAlreadyExistsError(machine.name) from e

            raise

        await self.session.refresh(machine)
        return MachineResponse.model_validate(machine)

    async def get_by_id(self, machine_id: UUID) -> MachineResponse:
        """Retrieves the machine having provided ID.

        Args:
            machine_id: ID of the machine to retrieve.

        Returns:
            Retrieved machine.

        Raises:
            MachineNotFoundError: When a machine with the given ID does not exists.
        """
        stmt = select(Machine).where(Machine.id == machine_id, Machine.deleted_at.is_(None))

        try:
            result = await self.session.execute(stmt)
            machine = result.scalar_one()

        except NoResultFound as e:
            raise MachineNotFoundError(machine_id) from e

        return MachineResponse.model_validate(machine)

    async def get_many(
        self, filter_params: MachineFilterParams
    ) -> tuple[list[MachineResponse], int]:
        """Retrieves machines based on defined filters.

        Args:
            filter_params: Conditions for filtering machines.

        Returns:
            Retrieved machines and total number of machines.
        """
        stmt = select(Machine)

        if filter_params.is_active is not None:
            stmt = stmt.where(Machine.is_active == filter_params.is_active)
        else:
            stmt = stmt.where(Machine.deleted_at.is_(None))

        if filter_params.search:
            search_term = f'%{filter_params.search}%'
            stmt = stmt.where(
                or_(Machine.name.ilike(search_term), Machine.description.ilike(search_term))
            )

        count_stmt = stmt.with_only_columns(func.count(Machine.id)).order_by(None)
        total = (await self.session.execute(count_stmt)).scalar_one()

        sort_column = getattr(Machine, filter_params.sort_by)
        if filter_params.sort_dir == 'asc':
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(filter_params.limit).offset(filter_params.offset)

        result = await self.session.execute(stmt)
        machines = result.scalars().all()

        return [MachineResponse.model_validate(m) for m in machines], total

    async def update(self, machine_id: UUID, payload: MachineUpdate) -> MachineResponse:
        """Updates the machine with the provided data.

        Args:
            machine_id: ID of the machine to update.
            payload: Data to update machine.

        Returns:
            Updated machine.

        Raises:
            MachineNotFoundError: When a machine with the given ID does not exists.
            MachineAlreadyExistsError: When a machine with the same name exists.
        """
        stmt = select(Machine).where(Machine.id == machine_id, Machine.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        machine = result.scalar_one_or_none()

        if not machine:
            raise MachineNotFoundError(machine_id)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(machine, key, value)

        try:
            await self.session.flush()

        except IntegrityError as e:
            if getattr(e.orig, 'sqlstate', None) == '23505':
                conflicting_name = update_data.get('name', machine.name)
                raise MachineAlreadyExistsError(conflicting_name) from e

            raise

        await self.session.refresh(machine)
        return MachineResponse.model_validate(machine)

    async def delete(self, machine_id: UUID) -> MachineResponse:
        """Deletes the machine having provided ID.

        Args:
            machine_id: ID of the machine to delete.

        Returns:
            Deleted machine.

        Raises:
            MachineNotFoundError: When a machine with the given ID does not exists.
        """
        stmt = select(Machine).where(Machine.id == machine_id, Machine.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        machine = result.scalar_one_or_none()

        if not machine:
            raise MachineNotFoundError(machine_id)

        machine.is_active = False
        machine.deleted_at = (
            func.now()
        )  # Using func.now() instead of datetime.now() to prevent Clock Skew problem

        await self.session.flush()
        await self.session.refresh(machine)
        return MachineResponse.model_validate(machine)
