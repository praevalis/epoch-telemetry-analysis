"""Manages pub/sub based event broker.

Features generic contracts, concrete managers and utility code for event management.
"""

from .interfaces import IEventManager
from .manager import RedisStreamManager

__all__ = ['IEventManager', 'RedisStreamManager']
