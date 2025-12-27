"""
Theme manager for the Plex Duplicate Detector application.

Handles theme application, persistence, and widget styling.
"""

import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from .theme_config import DARK_PALETTE, LIGHT_PALETTE, get_system_font, get_monospace_font
from .widget_styles import (
    apply_button_styles,
    apply_frame_styles,
    apply_label_styles,
    apply_treeview_styles,
    apply_notebook_styles,
    apply_entry_styles,
    apply_scale_styles,
    apply_scrollbar_styles,
    apply_radiobutton_styles,
    apply_separator_styles
)


class ThemeManager:
    """
    Singleton manager for application theming.

    Manages theme application, switching, and persistence.
    """

    _instance = None

    def __new__(cls, root: tk.Tk = None):
        """Ensure only one ThemeManager instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, root: tk.Tk):
        """
        Initialize the theme manager.

        Args:
            root: Main tkinter window
        """
        # Only initialize once
        if hasattr(self, '_initialized'):
            return

        self.root = root
        self.style = ttk.Style()

        # Use 'clam' as base theme (most customizable)
        self.style.theme_use('clam')

        # Load user preference or default to dark
        self.current_theme = self.load_preference()

        # Get system fonts
        font_family, body_size, header_size = get_system_font()
        self.fonts = {
            'body': (font_family, body_size),
            'header': (font_family, header_size),
            'small': (font_family, body_size - 1),
            'mono': (get_monospace_font(), body_size)
        }

        # List of custom non-ttk widgets for manual updates
        self.custom_widgets = []

        self._initialized = True

    def apply_theme(self, theme: str):
        """
        Apply a complete theme to all widgets.

        Args:
            theme: Theme name ('dark' or 'light')
        """
        # Get the appropriate palette
        palette = self.get_palette(theme)

        # Apply styles to all widget types with fonts
        apply_button_styles(self.style, palette, self.fonts)
        apply_frame_styles(self.style, palette)
        apply_label_styles(self.style, palette, self.fonts)
        apply_treeview_styles(self.style, palette, self.fonts)
        apply_notebook_styles(self.style, palette, self.fonts)
        apply_entry_styles(self.style, palette, self.fonts)
        apply_scale_styles(self.style, palette, self.fonts)
        apply_scrollbar_styles(self.style, palette)
        apply_radiobutton_styles(self.style, palette, self.fonts)
        apply_separator_styles(self.style, palette)

        # Update root window background
        self.root.configure(bg=palette['bg_primary'])

        # Update custom non-ttk widgets
        self._update_custom_widgets(palette)

        # Store current theme
        self.current_theme = theme

    def get_palette(self, theme: str) -> dict:
        """
        Get color palette for the specified theme.

        Args:
            theme: Theme name ('dark' or 'light')

        Returns:
            dict: Color palette dictionary
        """
        if theme == 'dark':
            return DARK_PALETTE
        else:
            return LIGHT_PALETTE

    def load_preference(self) -> str:
        """
        Load theme preference from config file.

        Returns:
            str: Theme name ('dark' or 'light'), defaults to 'dark'
        """
        config_path = self._get_config_path()

        if not config_path.exists():
            return 'dark'  # Default theme

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('theme', 'dark')
        except (json.JSONDecodeError, IOError):
            return 'dark'

    def save_preference(self, theme: str):
        """
        Save theme preference to config file.

        Args:
            theme: Theme name to save
        """
        config_path = self._get_config_path()

        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new one
        config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Update theme
        config['theme'] = theme

        # Save config
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            # Silently fail if we can't save preference
            print(f"Warning: Could not save theme preference: {e}")

    def register_custom_widget(self, widget):
        """
        Register a non-ttk widget for theme updates.

        Args:
            widget: Widget instance (Listbox, Text, etc.)
        """
        if widget not in self.custom_widgets:
            self.custom_widgets.append(widget)

    def _update_custom_widgets(self, palette: dict):
        """
        Update colors for non-ttk widgets.

        Args:
            palette: Color palette dictionary
        """
        for widget in self.custom_widgets:
            try:
                # Update widget colors
                widget.configure(
                    bg=palette['bg_secondary'],
                    fg=palette['text_primary'],
                    selectbackground=palette['selection_bg'],
                    selectforeground=palette['text_bright']
                )

                # If it's a Text widget, also update insert color
                if isinstance(widget, tk.Text):
                    widget.configure(insertbackground=palette['text_primary'])
            except tk.TclError:
                # Widget might not support these options
                pass

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(new_theme)
        self.save_preference(new_theme)

    def _get_config_path(self) -> Path:
        """
        Get path to config file.

        Returns:
            Path: Path to config.json file
        """
        home = Path.home()
        config_dir = home / '.plex_duplicate_detector'
        return config_dir / 'config.json'
