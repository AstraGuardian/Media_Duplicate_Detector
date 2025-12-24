"""
Quality analysis system for video files and folders.

Analyzes video files and folders based on:
- File size (larger = better)
- Codec from filename (h265/HEVC > h264/AVC)
- Resolution from filename (4K > 1080p > 720p > 480p)
- Source quality from filename (BluRay > WEB-DL > WEBRip)
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional


@dataclass
class QualityScore:
    """
    Quality score breakdown for a video file or folder.

    Attributes:
        total_score: Combined weighted score (0-1000+)
        size_score: Score based on file/folder size (0-100)
        codec_score: Score based on codec (0-100)
        resolution_score: Score based on resolution (0-400)
        source_score: Score based on source quality (0-150)
        has_metadata: Whether video metadata was used
        details: Additional details about detected attributes
    """
    total_score: float
    size_score: float
    codec_score: float
    resolution_score: float
    source_score: float
    has_metadata: bool
    details: Dict[str, Any]


class QualityAnalyzer:
    """
    Analyze video files and folders to determine quality scores.

    Uses filename parsing to extract quality indicators like codec,
    resolution, and source. Optionally can use video metadata if available.
    """

    # Codec patterns and scores
    CODEC_PATTERNS = {
        r'\b(h\.?265|hevc|x265)\b': ('h265', 100),
        r'\b(h\.?264|avc|x264)\b': ('h264', 50),
    }

    # Resolution patterns and scores
    RESOLUTION_PATTERNS = {
        r'\b(4k|2160p|uhd)\b': ('2160p', 400),
        r'\b(1080p|fhd)\b': ('1080p', 300),
        r'\b(720p|hd)\b': ('720p', 200),
        r'\b(480p|sd)\b': ('480p', 100),
    }

    # Source quality patterns and scores
    SOURCE_PATTERNS = {
        r'\b(bluray|blu-ray|bdrip|bd)\b': ('BluRay', 150),
        r'\b(web-?dl)\b': ('WEB-DL', 100),
        r'\b(webrip)\b': ('WEBRip', 80),
        r'\b(dvdrip|dvd)\b': ('DVD', 50),
    }

    # Score weights for final calculation
    SIZE_WEIGHT = 0.3
    CODEC_WEIGHT = 0.25
    RESOLUTION_WEIGHT = 0.30
    SOURCE_WEIGHT = 0.15

    def __init__(self, use_metadata: bool = False):
        """
        Initialize quality analyzer.

        Args:
            use_metadata: Whether to use video metadata (requires ffprobe)
                          Currently not implemented, reserved for future use
        """
        self.use_metadata = use_metadata

    def analyze_video_file(self, file_path: str, size: int) -> QualityScore:
        """
        Analyze a video file and return quality score.

        Args:
            file_path: Full path to video file
            size: File size in bytes

        Returns:
            QualityScore with breakdown of quality metrics
        """
        filename = Path(file_path).name
        return self._analyze_item(filename, size, is_folder=False)

    def analyze_folder(self, folder_path: str, stats: Dict[str, Any]) -> QualityScore:
        """
        Analyze a folder and return quality score.

        Args:
            folder_path: Full path to folder
            stats: Folder statistics dict containing:
                   - total_size: Total size in bytes
                   - video_files: Number of video files

        Returns:
            QualityScore with breakdown of quality metrics
        """
        folder_name = Path(folder_path).name
        size = stats.get('total_size', 0)
        return self._analyze_item(folder_name, size, is_folder=True)

    def _analyze_item(self, name: str, size: int, is_folder: bool) -> QualityScore:
        """
        Core analysis logic for both files and folders.

        Args:
            name: Filename or folder name
            size: Size in bytes
            is_folder: Whether analyzing a folder

        Returns:
            QualityScore with all metrics
        """
        # Parse name for quality indicators
        codec_name, codec_score = self._parse_codec(name)
        resolution_name, resolution_score = self._parse_resolution(name)
        source_name, source_score = self._parse_source(name)

        # Calculate size score (normalize to 0-100, 1GB = ~10 points)
        # Larger files get higher scores, capped at 100
        gb_size = size / (1024 ** 3)  # Convert bytes to GB
        size_score = min(100, gb_size * 10)

        # Calculate weighted total score
        total_score = (
            (size_score * self.SIZE_WEIGHT) +
            (codec_score * self.CODEC_WEIGHT) +
            (resolution_score * self.RESOLUTION_WEIGHT) +
            (source_score * self.SOURCE_WEIGHT)
        )

        # Build details dictionary
        details = {
            'name': name,
            'size_gb': round(gb_size, 2),
            'codec': codec_name or 'unknown',
            'resolution': resolution_name or 'unknown',
            'source': source_name or 'unknown',
            'is_folder': is_folder
        }

        return QualityScore(
            total_score=round(total_score, 2),
            size_score=round(size_score, 2),
            codec_score=codec_score,
            resolution_score=resolution_score,
            source_score=source_score,
            has_metadata=False,
            details=details
        )

    def _parse_codec(self, name: str) -> tuple[Optional[str], int]:
        """
        Parse codec from filename.

        Args:
            name: Filename or folder name

        Returns:
            Tuple of (codec_name, score)
        """
        name_lower = name.lower()
        for pattern, (codec_name, score) in self.CODEC_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                return codec_name, score
        return None, 0

    def _parse_resolution(self, name: str) -> tuple[Optional[str], int]:
        """
        Parse resolution from filename.

        Args:
            name: Filename or folder name

        Returns:
            Tuple of (resolution_name, score)
        """
        name_lower = name.lower()
        for pattern, (resolution_name, score) in self.RESOLUTION_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                return resolution_name, score
        return None, 0

    def _parse_source(self, name: str) -> tuple[Optional[str], int]:
        """
        Parse source quality from filename.

        Args:
            name: Filename or folder name

        Returns:
            Tuple of (source_name, score)
        """
        name_lower = name.lower()
        for pattern, (source_name, score) in self.SOURCE_PATTERNS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                return source_name, score
        return None, 0


def find_best_item(items: list, analyzer: QualityAnalyzer,
                   get_path_func, get_size_func, is_folder: bool = False) -> Optional[str]:
    """
    Find the best item from a list based on quality analysis.

    Args:
        items: List of items to analyze
        analyzer: QualityAnalyzer instance
        get_path_func: Function to extract path from item
        get_size_func: Function to extract size from item
        is_folder: Whether analyzing folders

    Returns:
        Path of best item, or None if list is empty or has only one item
    """
    if len(items) < 2:
        # No comparison needed for 0 or 1 item
        return None

    best_path = None
    best_score = -1
    best_name = None

    for item in items:
        path = get_path_func(item)
        size = get_size_func(item)

        if is_folder:
            score_obj = analyzer.analyze_folder(path, {'total_size': size})
        else:
            score_obj = analyzer.analyze_video_file(path, size)

        # Track best score, use alphabetical order for ties
        if score_obj.total_score > best_score:
            best_score = score_obj.total_score
            best_path = path
            best_name = Path(path).name
        elif score_obj.total_score == best_score and best_name:
            # Tie: pick alphabetically first
            current_name = Path(path).name
            if current_name < best_name:
                best_path = path
                best_name = current_name

    return best_path
