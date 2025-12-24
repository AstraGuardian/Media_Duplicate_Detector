"""
Tooltip system for displaying full paths on treeview hover.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class TreeviewTooltip:
    """
    Display tooltips showing full paths when hovering over treeview items.

    Features:
    - 500ms delay before tooltip appears
    - Auto-hides when mouse moves away
    - Positioned at mouse cursor
    - Light yellow background with black border
    """

    def __init__(self, treeview: ttk.Treeview, get_tooltip_text_func: Callable[[str], Optional[str]]):
        """
        Initialize tooltip for a treeview.

        Args:
            treeview: The treeview widget to add tooltips to
            get_tooltip_text_func: Function that takes item_id and returns tooltip text
        """
        self.treeview = treeview
        self.get_tooltip_text = get_tooltip_text_func
        self.tooltip_window: Optional[tk.Toplevel] = None
        self.current_item: Optional[str] = None
        self.after_id: Optional[str] = None

        # Bind mouse events
        self.treeview.bind('<Motion>', self._on_mouse_motion)
        self.treeview.bind('<Leave>', self._on_mouse_leave)

    def _on_mouse_motion(self, event):
        """
        Handle mouse motion over treeview.

        Args:
            event: Mouse motion event
        """
        # Identify the item under mouse cursor
        item = self.treeview.identify_row(event.y)

        if item != self.current_item:
            # Mouse moved to different item, hide current tooltip
            self._hide_tooltip()
            self.current_item = item

            if item:
                # Schedule tooltip to appear after 500ms
                self.after_id = self.treeview.after(500, lambda: self._show_tooltip(item, event.x_root, event.y_root))

    def _on_mouse_leave(self, event):
        """
        Handle mouse leaving treeview.

        Args:
            event: Mouse leave event
        """
        self._hide_tooltip()
        self.current_item = None

    def _show_tooltip(self, item_id: str, x: int, y: int):
        """
        Display tooltip at specified position.

        Args:
            item_id: Treeview item ID
            x: Screen X coordinate
            y: Screen Y coordinate
        """
        # Get tooltip text from callback
        tooltip_text = self.get_tooltip_text(item_id)

        if not tooltip_text:
            return

        # Hide any existing tooltip
        self._hide_tooltip()

        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.treeview)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations

        # Create label with tooltip text
        label = tk.Label(
            self.tooltip_window,
            text=tooltip_text,
            background="#FFFACD",  # Light yellow
            foreground="black",
            relief=tk.SOLID,
            borderwidth=1,
            font=("sans-serif", 9),
            justify=tk.LEFT,
            padx=5,
            pady=3
        )
        label.pack()

        # Position tooltip
        # Offset slightly from cursor to avoid interference
        tooltip_x = x + 10
        tooltip_y = y + 10

        # Adjust position to keep tooltip on screen
        self.tooltip_window.update_idletasks()
        tooltip_width = self.tooltip_window.winfo_width()
        tooltip_height = self.tooltip_window.winfo_height()
        screen_width = self.tooltip_window.winfo_screenwidth()
        screen_height = self.tooltip_window.winfo_screenheight()

        # Keep tooltip within screen bounds
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = screen_width - tooltip_width - 10
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = screen_height - tooltip_height - 10

        self.tooltip_window.wm_geometry(f"+{tooltip_x}+{tooltip_y}")

    def _hide_tooltip(self):
        """Hide the current tooltip if visible."""
        # Cancel any pending tooltip
        if self.after_id:
            self.treeview.after_cancel(self.after_id)
            self.after_id = None

        # Destroy tooltip window
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def get_path_from_tags(treeview: ttk.Treeview, item_id: str) -> Optional[str]:
    """
    Extract full path from treeview item tags.

    This is a helper function for common use case where paths are stored
    as the second element in item tags (first is the tag type).

    Args:
        treeview: The treeview widget
        item_id: The item ID to get path from

    Returns:
        Full path string or None if not available
    """
    tags = treeview.item(item_id, "tags")
    if tags and len(tags) >= 2:
        # Tags format: (type, path) e.g., ("file", "/full/path/to/file.mkv")
        return tags[1]
    return None
