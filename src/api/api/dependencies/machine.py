from typing import Annotated

from fastapi import Depends

from engine.application.machine_service import MachineService
from engine.database.relational import DbSession
from engine.domain.api_key import IApiKeyRepository
from engine.domain.common import ITransactionManager
from engine.domain.machine import IMachineRepository
from engine.repositories.machine import MachineRepository

from .api_key import get_cached_api_key_repo
from .core import get_db_session, get_tx_manager


def get_machine_repo(session: Annotated[DbSession, Depends(get_db_session)]) -> IMachineRepository:
    """Dependency that returns machine repository."""
    return MachineRepository(session)


def get_machine_service(
    machine_repo: Annotated[IMachineRepository, Depends(get_machine_repo)],
    api_key_repo: Annotated[IApiKeyRepository, Depends(get_cached_api_key_repo)],
    tx_manager: Annotated[ITransactionManager, Depends(get_tx_manager)],
) -> MachineService:
    """Dependency that returns machine service."""
    return MachineService(machine_repo, api_key_repo, tx_manager)
