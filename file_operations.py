"""
File operations module for handling file deletion and utilities.
"""

import os
from pathlib import Path
from typing import List, Dict


def format_file_size(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string (e.g., "1.2 GB", "800 MB", "50 KB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def delete_files(file_paths: List[str]) -> Dict[str, str]:
    """
    Delete multiple files and return status for each.

    Args:
        file_paths: List of file paths to delete

    Returns:
        Dictionary mapping file paths to status:
        - "success": File deleted successfully
        - Error message: If deletion failed
    """
    results = {}

    for file_path in file_paths:
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                os.remove(file_path)
                results[file_path] = "success"
            else:
                results[file_path] = "File not found"
        except PermissionError:
            results[file_path] = "Permission denied"
        except OSError as e:
            results[file_path] = f"Error: {str(e)}"
        except Exception as e:
            results[file_path] = f"Unexpected error: {str(e)}"

    return results


def calculate_total_size(file_paths: List[str]) -> int:
    """
    Calculate total size of multiple files.

    Args:
        file_paths: List of file paths

    Returns:
        Total size in bytes
    """
    total = 0
    for file_path in file_paths:
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                total += path.stat().st_size
        except (OSError, PermissionError):
            # Skip files we can't access
            continue

    return total
