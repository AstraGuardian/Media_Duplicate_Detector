"""
Folder tagging system for managing tagged folders in the duplicate detector.
"""

import json
import threading
from pathlib import Path
from typing import Set, Dict
from datetime import datetime


class FolderTagManager:
    """Manages persistent storage of tagged folders."""

    def __init__(self):
        """Initialize the tag manager and create config directory if needed."""
        self.config_dir = Path.home() / ".plex_duplicate_detector"
        self.tags_file = self.config_dir / "folder_tags.json"
        self._lock = threading.Lock()

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_tags(self) -> Set[str]:
        """
        Load tagged folders from JSON file.

        Returns:
            Set of tagged folder paths
        """
        if not self.tags_file.exists():
            return set()

        try:
            with open(self.tags_file, 'r') as f:
                data = json.load(f)
                return set(data.get('tagged_folders', []))
        except (json.JSONDecodeError, OSError):
            # If file is corrupted or unreadable, return empty set
            return set()

    def save_tags(self, tagged_folders: Set[str]):
        """
        Save tagged folders to JSON file.

        Args:
            tagged_folders: Set of folder paths to save

        Raises:
            IOError: If the tags file cannot be written
        """
        with self._lock:
            # Build metadata for each tagged folder
            tag_metadata = {}
            for folder_path in tagged_folders:
                tag_metadata[folder_path] = {
                    'tagged_date': datetime.now().isoformat()
                }

            data = {
                'tagged_folders': sorted(list(tagged_folders)),
                'tag_metadata': tag_metadata
            }

            try:
                with open(self.tags_file, 'w') as f:
                    json.dump(data, f, indent=2)
            except OSError as e:
                raise IOError(f"Could not save tags to {self.tags_file}: {e}")

    def add_tag(self, folder_path: str, current_tags: Set[str]) -> Set[str]:
        """
        Add a tag to a folder.

        Args:
            folder_path: Path to the folder to tag
            current_tags: Current set of tagged folders

        Returns:
            Updated set of tagged folders
        """
        updated_tags = current_tags.copy()
        updated_tags.add(folder_path)
        self.save_tags(updated_tags)
        return updated_tags

    def remove_tag(self, folder_path: str, current_tags: Set[str]) -> Set[str]:
        """
        Remove a tag from a folder.

        Args:
            folder_path: Path to the folder to untag
            current_tags: Current set of tagged folders

        Returns:
            Updated set of tagged folders
        """
        updated_tags = current_tags.copy()
        updated_tags.discard(folder_path)
        self.save_tags(updated_tags)
        return updated_tags

    def clear_all_tags(self):
        """Clear all tags and delete the tags file."""
        with self._lock:
            if self.tags_file.exists():
                try:
                    self.tags_file.unlink()
                except OSError:
                    pass
            return set()
