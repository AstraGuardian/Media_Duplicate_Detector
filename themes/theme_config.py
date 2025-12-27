"""
Theme configuration for Plex Duplicate Detector.

Defines color palettes, fonts, and spacing constants for dark and light themes.
"""

import sys
from tkinter import font as tkfont


# Color Palettes
DARK_PALETTE = {
    # Backgrounds
    'bg_primary': '#1e1e1e',
    'bg_secondary': '#252526',
    'bg_tertiary': '#2d2d30',
    'bg_elevated': '#3e3e42',
    'bg_hover': '#2a2d2e',

    # Text
    'text_primary': '#cccccc',
    'text_secondary': '#999999',
    'text_disabled': '#656565',
    'text_bright': '#ffffff',

    # Accents
    'accent_primary': '#007acc',
    'accent_success': '#4ec9b0',
    'accent_danger': '#f48771',

    # Borders
    'border_default': '#3e3e42',
    'border_focus': '#007acc',

    # Tooltips
    'tooltip_bg': '#2b2b2b',
    'tooltip_border': '#454545',

    # Selection
    'selection_bg': '#094771',
}

LIGHT_PALETTE = {
    # Backgrounds
    'bg_primary': '#ffffff',
    'bg_secondary': '#f3f3f3',
    'bg_tertiary': '#fafafa',
    'bg_elevated': '#ffffff',
    'bg_hover': '#e8e8e8',

    # Text
    'text_primary': '#333333',
    'text_secondary': '#666666',
    'text_disabled': '#999999',
    'text_bright': '#000000',

    # Accents (same as dark for brand consistency)
    'accent_primary': '#007acc',
    'accent_success': '#4ec9b0',
    'accent_danger': '#f48771',

    # Borders
    'border_default': '#d4d4d4',
    'border_focus': '#007acc',

    # Tooltips
    'tooltip_bg': '#f5f5f5',
    'tooltip_border': '#cccccc',

    # Selection
    'selection_bg': '#cce4f7',
}

# Spacing scale (8px base unit)
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 24,
}


def get_system_font():
    """
    Detect and return the best font for the current platform.

    Returns:
        tuple: (font_family, body_size, header_size)
    """
    platform = sys.platform

    if platform == 'win32':
        # Windows
        font_family = 'Segoe UI'
        body_size = 10
        header_size = 13
    else:
        # Linux/Unix - try Ubuntu first, fallback to DejaVu Sans
        try:
            # Check if Ubuntu font is available
            test_font = tkfont.Font(family='Ubuntu', size=10)
            font_family = 'Ubuntu'
        except:
            # Fallback to DejaVu Sans
            font_family = 'DejaVu Sans'

        body_size = 10
        header_size = 12

    return (font_family, body_size, header_size)


def get_monospace_font():
    """
    Get monospace font for the current platform.

    Returns:
        str: Font family name
    """
    platform = sys.platform

    if platform == 'win32':
        return 'Consolas'
    else:
        # Try Ubuntu Mono, fallback to Courier
        try:
            test_font = tkfont.Font(family='Ubuntu Mono', size=10)
            return 'Ubuntu Mono'
        except:
            return 'Courier'
