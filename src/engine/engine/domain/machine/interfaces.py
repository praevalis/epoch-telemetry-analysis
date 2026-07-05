from typing import Protocol
from uuid import UUID

from .schemas import MachineCreate, MachineFilterParams, MachineResponse, MachineUpdate


class IMachineRepository(Protocol):
    """Abstract interface for Machine data operations."""

    async def create(self, payload: MachineCreate) -> MachineResponse:
        """Creates a machine with provided data.

        Args:
            payload: Data to create machine.

        Returns:
            Created machine.

        Raises:
            MachineAlreadyExistsError: When a machine with the same name exists.
        """
        ...

    async def get_by_id(self, machine_id: UUID) -> MachineResponse:
        """Retrieves the machine having provided ID.

        Args:
            machine_id: ID of the machine to retrieve.

        Returns:
            Retrieved machine.

        Raises:
            MachineNotFoundError: When a machine with the given ID does not exists.
        """
        ...

    async def get_many(self, filter_params: MachineFilterParams) -> list[MachineResponse]:
        """Retrieves machines based on defined filters.

        Args:
            filter_params: Conditions for filtering machines.

        Returns:
            Retrieved machines.
        """
        ...

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
        ...

    async def delete(self, machine_id: UUID) -> MachineResponse:
        """Deletes the machine having provided ID.

        Args:
            machine_id: ID of the machine to delete.

        Returns:
            Deleted machine.

        Raises:
            MachineNotFoundError: When a machine with the given ID does not exists.
        """
        ...
