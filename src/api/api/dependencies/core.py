from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request

from engine.database.cache import ICacheManager
from engine.database.relational import (
    DbSession,
    ISessionManager,
    SqlAlchemyTransactionManager,
)
from engine.domain.common import ITransactionManager
from engine.infrastructure import ConnectionManager


def get_connection_manager(request: Request) -> ConnectionManager:
    """Dependency that returns connection manager from app state."""
    return request.app.state.connections


def get_db_manager(
    conn_manager: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> ISessionManager:
    """Dependency that returns database manager."""
    return conn_manager.get_db_manager()


def get_cache_manager(
    conn_manager: Annotated[ConnectionManager, Depends(get_connection_manager)],
) -> ICacheManager:
    """Dependency that returns cache manager."""
    return conn_manager.get_cache_manager()


async def get_db_session(
    db_manager: Annotated[ISessionManager, Depends(get_db_manager)],
) -> AsyncGenerator[DbSession]:
    """Dependency that yields database session."""
    async with db_manager.session() as session:
        yield session


def get_tx_manager(session: Annotated[DbSession, Depends(get_db_session)]) -> ITransactionManager:
    """Dependency that returns transaction manager."""
    return SqlAlchemyTransactionManager(session)
