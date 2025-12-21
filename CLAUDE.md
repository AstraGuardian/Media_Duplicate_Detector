# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Plex Duplicate Detector is a cross-platform (Windows/Linux) GUI application that scans Plex media libraries to identify movies with multiple video files, helping users manage storage by detecting and removing duplicates.

## Project Requirements

- **Cross-platform**: Must run on both Windows and Linux with minimal setup
- **GUI Application**: User-friendly interface (not CLI)
- **Library Structure**: Assumes each movie is in its own folder containing video files, subtitles, etc.
- **Core Functionality**:
  - Prompt user for library folder location
  - Recursively scan all subfolders
  - Detect multiple video files within each movie folder (including nested subfolders)
  - Display results in a collapsible tree view:
    - Parent: Movie folder name + count of video files
    - Children: Individual video files with filename and full path
  - Show total count of duplicates across entire library
  - Allow multi-selection of files for deletion
  - Provide delete button to remove selected files

## Technology Stack Considerations

When implementing this project:

- **GUI Framework**: Choose a cross-platform GUI framework with minimal dependencies (e.g., tkinter for Python, Electron for JavaScript, or similar)
- **File Operations**: Must handle cross-platform path differences (Windows backslashes vs Linux forward slashes)
- **Video File Detection**: Need to identify video file extensions (mp4, mkv, avi, mov, etc.)
- **Safety**: Deletion operations should include confirmation dialogs and error handling

## Key Architecture Components

1. **Scanner Module**: Handles filesystem traversal and video file detection
2. **Data Model**: Represents the hierarchical structure of movies and their files
3. **GUI Module**: Manages the user interface, tree view, and user interactions
4. **File Operations Module**: Handles safe file deletion with proper error handling
5. **Configuration**: Store/retrieve last used library path and user preferences

## Important Behavioral Notes

- Video files should be detected by extension (case-insensitive)
- Each movie folder is scanned independently, including any nested subfolders within it
- Only folders containing 2+ video files should be considered "duplicates" for the count
- File deletion should be permanent (not move to trash) but require explicit user confirmation
- The application should handle permission errors gracefully when scanning or deleting files

## Network Share Support

- **Manual Path Entry**: Users can type paths directly into the path field (not just use Browse button)
- **SMB/CIFS Shares**: On Linux, SMB shares must be mounted to the filesystem first (e.g., via `mount -t cifs`)
- **Help Button**: The **?** button next to the path field provides instructions for mounting SMB shares
- **Path Validation**: The application validates that entered paths exist before scanning
- Works with any mounted filesystem path, including network mounts at `/mnt/`, `/media/`, etc.
