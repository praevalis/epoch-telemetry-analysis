from uuid import UUID

from engine.domain.common import DomainException


class ApiKeyNotFoundError(DomainException):
    def __init__(self, key_id: UUID | None = None, key_hash: str | None = None) -> None:
        if key_id:
            super().__init__(f'API key with ID {key_id} was not found.')
        elif key_hash:
            super().__init__('API key with the specified hash was not found.')
        else:
            super().__init__('API key was not found.')

        self.key_id = key_id
        self.key_hash = key_hash


class ApiKeyRevokedError(DomainException):
    def __init__(self, key_id: UUID) -> None:
        super().__init__(f'API key with {key_id} has been revoked.')
        self.key_id = key_id
