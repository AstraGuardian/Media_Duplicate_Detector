"""
Scanner module for detecting duplicate video files in Plex library folders.
"""

from pathlib import Path
from typing import Dict, List, Tuple

# Supported video file extensions
VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.m4v')


def is_video_file(filepath: Path) -> bool:
    """
    Check if a file is a video file based on its extension.

    Args:
        filepath: Path object representing the file

    Returns:
        True if file has a video extension, False otherwise
    """
    return filepath.suffix.lower() in VIDEO_EXTENSIONS


def find_videos_in_folder(folder_path: Path) -> List[Dict[str, any]]:
    """
    Find all video files within a folder and its subfolders.

    Args:
        folder_path: Path to the folder to scan

    Returns:
        List of dictionaries containing video file information:
        - filename: Name of the file
        - full_path: Full path to the file
        - size: File size in bytes
    """
    video_files = []

    try:
        # Recursively walk through the folder and all subfolders
        for item in folder_path.rglob('*'):
            if item.is_file() and is_video_file(item):
                try:
                    file_size = item.stat().st_size
                    video_files.append({
                        'filename': item.name,
                        'full_path': str(item),
                        'size': file_size
                    })
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
    except (OSError, PermissionError):
        # Skip folders we can't access
        pass

    return video_files


def scan_library(root_path: str) -> Dict[str, List[Dict[str, any]]]:
    """
    Scan the entire library for movie folders with multiple video files.

    This function assumes each movie is in its own folder. It scans each
    top-level folder in the library and identifies folders containing 2+
    video files (potential duplicates).

    Args:
        root_path: Path to the root library folder

    Returns:
        Dictionary mapping movie folder paths to lists of video file info.
        Only includes folders with 2 or more video files.

    Example:
        {
            '/library/The Matrix': [
                {'filename': 'movie1.mp4', 'full_path': '/library/The Matrix/movie1.mp4', 'size': 1234567},
                {'filename': 'movie2.mkv', 'full_path': '/library/The Matrix/movie2.mkv', 'size': 2345678}
            ]
        }
    """
    root = Path(root_path)
    duplicates = {}

    if not root.exists() or not root.is_dir():
        return duplicates

    try:
        # Iterate through all subdirectories in the library
        for movie_folder in root.iterdir():
            if not movie_folder.is_dir():
                continue

            # Find all video files in this movie folder (including subfolders)
            video_files = find_videos_in_folder(movie_folder)

            # Only include folders with 2 or more video files
            if len(video_files) >= 2:
                duplicates[str(movie_folder)] = video_files

    except (OSError, PermissionError):
        # Handle permission errors for the root folder
        pass

    return duplicates


def get_folder_name(folder_path: str) -> str:
    """
    Extract the folder name from a full path.

    Args:
        folder_path: Full path to a folder

    Returns:
        Name of the folder (last component of the path)
    """
    return Path(folder_path).name
