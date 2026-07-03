"""Manages heavy TCP pool connection and other required infrastructure
for the application."""

from .connection_manager import ConnectionManager

__all__ = ['ConnectionManager']
