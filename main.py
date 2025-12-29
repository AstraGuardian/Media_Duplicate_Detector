#!/usr/bin/env python3
"""
Media Duplicate Detector

A cross-platform GUI application for detecting and managing duplicate
video files in media libraries.
"""

import tkinter as tk
from gui import DuplicateDetectorGUI


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = DuplicateDetectorGUI(root)
    app.run()


if __name__ == "__main__":
    main()
