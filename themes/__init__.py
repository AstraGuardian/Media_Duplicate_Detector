"""
Theme package for Plex Duplicate Detector.

Provides modern, sleek theming with dark and light mode support.
"""

from .theme_manager import ThemeManager
from .theme_config import DARK_PALETTE, LIGHT_PALETTE, SPACING

__all__ = ['ThemeManager', 'DARK_PALETTE', 'LIGHT_PALETTE', 'SPACING']
