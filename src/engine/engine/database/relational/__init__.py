"""Manages relational databases.

Features generic contracts, session managers, database models and
ORM config for the relational databases used in the application.
"""

from .interfaces import ISessionManager
from .session import TimescaleSessionManager

__all__ = ['ISessionManager', 'TimescaleSessionManager']
