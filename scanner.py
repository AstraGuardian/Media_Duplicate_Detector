"""
Scanner module for detecting duplicate video files in Plex library folders.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
from difflib import SequenceMatcher

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


def find_videos_in_folder(folder_path: Path) -> List[Dict[str, Any]]:
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


# ===== Duplicate Folder Detection Functions =====


def normalize_folder_name(folder_name: str) -> str:
    """
    Normalize folder name for comparison by removing common variations.

    Removes:
    - Years in parentheses or brackets: (2020), [2020]
    - Quality indicators: 1080p, 720p, 4K, BluRay, etc.
    - Extra whitespace

    Args:
        folder_name: Original folder name

    Returns:
        Normalized folder name (lowercase, stripped)
    """
    normalized = folder_name.lower()

    # Remove years in parentheses/brackets
    normalized = re.sub(r'\s*[\(\[]?\d{4}[\)\]]?\s*', ' ', normalized)

    # Remove quality indicators
    quality_patterns = [
        r'\b(1080p|720p|480p|4k|2160p|uhd)\b',
        r'\b(bluray|blu-ray|brrip|bdrip|web-?dl|webrip|hdtv|dvdrip)\b',
        r'\b(x264|x265|h264|h265|hevc|avc)\b',
        r'\b(aac|dts|ac3|mp3|flac)\b',
        r'\[\w+\]',  # Remove bracketed tags
    ]

    for pattern in quality_patterns:
        normalized = re.sub(pattern, ' ', normalized, flags=re.IGNORECASE)

    # Clean up extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized.strip()


def calculate_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity ratio between two strings using SequenceMatcher.

    Args:
        name1: First string to compare
        name2: Second string to compare

    Returns:
        Similarity ratio from 0.0 (completely different) to 1.0 (identical)
    """
    return SequenceMatcher(None, name1, name2).ratio()


def find_duplicate_folders_exact(library_paths: List[str]) -> Dict[str, List[str]]:
    """
    Find folders with exact matching normalized names.

    Args:
        library_paths: List of library root paths to scan

    Returns:
        Dictionary mapping normalized names to lists of full folder paths.
        Only includes groups with 2 or more folders.

    Example:
        {
            'the matrix': [
                '/library1/The Matrix (1999)',
                '/library2/The Matrix [2020]'
            ]
        }
    """
    folder_groups = {}

    for library_path in library_paths:
        root = Path(library_path)
        if not root.exists() or not root.is_dir():
            continue

        try:
            for folder in root.iterdir():
                if not folder.is_dir():
                    continue

                folder_name = folder.name
                normalized = normalize_folder_name(folder_name)

                if normalized:  # Skip empty normalized names
                    if normalized not in folder_groups:
                        folder_groups[normalized] = []
                    folder_groups[normalized].append(str(folder))

        except (OSError, PermissionError):
            # Skip folders we can't access
            continue

    # Filter out groups with only 1 folder
    return {k: v for k, v in folder_groups.items() if len(v) >= 2}


def find_duplicate_folders_fuzzy(library_paths: List[str], threshold: float = 0.8) -> Dict[str, List[str]]:
    """
    Find folders with similar names using fuzzy matching.

    Args:
        library_paths: List of library root paths to scan
        threshold: Similarity threshold (0.0-1.0), default 0.8 (80%)

    Returns:
        Dictionary mapping group IDs to lists of full folder paths.
        Only includes groups with 2 or more folders.

    Example:
        {
            'group_0': [
                '/library/The Matrix',
                '/library/Matrix',
                '/library/The Matrix Reloaded'
            ]
        }
    """
    # First, collect all folders with their normalized names
    all_folders = []

    for library_path in library_paths:
        root = Path(library_path)
        if not root.exists() or not root.is_dir():
            continue

        try:
            for folder in root.iterdir():
                if not folder.is_dir():
                    continue

                folder_name = folder.name
                normalized = normalize_folder_name(folder_name)

                if normalized:  # Skip empty normalized names
                    all_folders.append({
                        'path': str(folder),
                        'name': folder_name,
                        'normalized': normalized
                    })

        except (OSError, PermissionError):
            # Skip folders we can't access
            continue

    # Group folders by similarity
    groups = []
    processed = set()

    for i, folder1 in enumerate(all_folders):
        if i in processed:
            continue

        current_group = [folder1['path']]
        processed.add(i)

        for j, folder2 in enumerate(all_folders):
            if j <= i or j in processed:
                continue

            similarity = calculate_similarity(folder1['normalized'], folder2['normalized'])
            if similarity >= threshold:
                current_group.append(folder2['path'])
                processed.add(j)

        # Only include groups with 2+ folders
        if len(current_group) >= 2:
            groups.append(current_group)

    # Convert to dictionary with group IDs
    return {f'group_{i}': paths for i, paths in enumerate(groups)}


def get_folder_stats(folder_path: str) -> Dict[str, Any]:
    """
    Get statistics for a folder.

    Args:
        folder_path: Path to the folder

    Returns:
        Dictionary containing:
        - total_files: Total number of files
        - video_files: Number of video files
        - total_size: Total size in bytes
        - video_size: Total size of video files in bytes
    """
    folder = Path(folder_path)
    stats = {
        'total_files': 0,
        'video_files': 0,
        'total_size': 0,
        'video_size': 0
    }

    if not folder.exists() or not folder.is_dir():
        return stats

    try:
        for item in folder.rglob('*'):
            if item.is_file():
                try:
                    file_size = item.stat().st_size
                    stats['total_files'] += 1
                    stats['total_size'] += file_size

                    if is_video_file(item):
                        stats['video_files'] += 1
                        stats['video_size'] += file_size

                except (OSError, PermissionError):
                    continue

    except (OSError, PermissionError):
        pass

    return stats
