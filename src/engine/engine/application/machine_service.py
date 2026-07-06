from uuid import UUID

from engine.domain.api_key import IApiKeyRepository
from engine.domain.common import ITransactionManager
from engine.domain.machine import (
    IMachineRepository,
    MachineCreate,
    MachineFilterParams,
    MachineResponse,
    MachineUpdate,
)


class MachineService:
    """Handles business logic for machine domain."""

    def __init__(
        self,
        machine_repo: IMachineRepository,
        api_key_repo: IApiKeyRepository,
        tx_manager: ITransactionManager,
    ) -> None:
        """Initializes the service.

        Args:
            machine_repo: Repository that handles machine-related data operations.
            api_key_repo: Repository that handles api key-related data operations.
            tx_manager: Cross-domain transaction manager.
        """
        self.machine_repo = machine_repo
        self.api_key_repo = api_key_repo
        self.tx_manager = tx_manager

    async def create_machine(self, payload: MachineCreate) -> MachineResponse:
        """Handles machine creation.

        Args:
            payload: Data to create machine.

        Returns:
            Created machine.
        """
        created_machine = await self.machine_repo.create(payload)
        await self.tx_manager.commit()

        return created_machine

    async def get_machine_by_id(self, machine_id: UUID) -> MachineResponse:
        """Retrieves a machine using the provided ID.

        Args:
            machine_id: ID of the machine.

        Returns:
            Retrieved machine.
        """
        return await self.machine_repo.get_by_id(machine_id)

    async def get_many_machines(
        self, filter_params: MachineFilterParams
    ) -> tuple[list[MachineResponse], int]:
        """Retrieves all machines based on provided filter.

        Args:
            filter_params: Filter criteria.

        Returns:
            Retrieved machines and total number of machines.
        """
        return await self.machine_repo.get_many(filter_params)

    async def update_machine(self, machine_id: UUID, payload: MachineUpdate) -> MachineResponse:
        """Updates the specified machine with provided data.

        Args:
            machine_id: ID of the machine to update.
            payload: Data to update.

        Returns:
            Updated machine.
        """
        updated_machine = await self.machine_repo.update(machine_id, payload)
        await self.tx_manager.commit()

        return updated_machine

    async def delete_machine(self, machine_id: UUID) -> None:
        """Deletes a machine and revokes all active API keys.

        Args:
            machine_id: ID of the machine to delete.

        Returns:
            No response is returned.
        """
        deleted_machine = await self.machine_repo.delete(machine_id)
        await self.api_key_repo.revoke_for_machine(deleted_machine.id)
        await self.tx_manager.commit()
