from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from engine.database.relational import TimescaleSessionManager


@pytest.fixture
def mock_session_factory() -> MagicMock:
    """Creates a fake session factory that returns a fake AsyncSession."""
    factory = MagicMock()
    factory.return_value = AsyncMock(spec=AsyncSession)
    return factory


@pytest.fixture
def session_manager(mock_session_factory: MagicMock) -> TimescaleSessionManager:
    """Injects fake session factory into the TimescaleSessionManager."""
    return TimescaleSessionManager(session_factory=mock_session_factory)


@pytest.mark.asyncio
class TestTimescaleSessionManager:
    """Tests the relational database session manager."""

    async def test_session_closes_on_success(
        self, session_manager: TimescaleSessionManager, mock_session_factory: MagicMock
    ) -> None:
        """Tests the happy path: No exceptions occur."""
        mock_session = mock_session_factory.return_value

        async with session_manager.session() as session:
            assert session is mock_session

        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

    async def test_session_rolls_back_on_exception(
        self, session_manager: TimescaleSessionManager, mock_session_factory: MagicMock
    ) -> None:
        """Tests the sad path: An exception is thrown during execution."""
        mock_session = mock_session_factory.return_value
        custom_error = ValueError('Something broke inside the context.')

        with pytest.raises(ValueError, match='Something broke'):
            async with session_manager.session():
                raise custom_error

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
