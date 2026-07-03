"""Manages in-memory cache.

Features generic contracts, client managers, models and utility code for in-memory cache.
"""

from .interfaces import ICacheManager
from .manager import RedisCacheManager

__all__ = ['ICacheManager', 'RedisCacheManager']
