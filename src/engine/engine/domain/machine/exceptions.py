from uuid import UUID

from engine.domain.common import DomainException


class MachineNotFoundError(DomainException):
    def __init__(self, machine_id: UUID) -> None:
        super().__init__(f'Machine with ID {machine_id} not found.')
        self.machine_id = machine_id


class MachineAlreadyExistsError(DomainException):
    def __init__(self, name: str) -> None:
        super().__init__(f'Machine with name {name} already exists.')
        self.name = name
