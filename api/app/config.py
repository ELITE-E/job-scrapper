"""
DEPRECATED: Compatibility layer for backward compatibility.

This module re-exports the new Settings from app.core.config to maintain
backward compatibility with existing code that imports from app.config.

All new code should import directly from app.core.config.
"""

from app.core.config import Settings, settings

__all__ = ["Settings", "settings"]