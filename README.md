# Plex Duplicate Detector

A cross-platform GUI application for detecting and managing duplicate video files in Plex media libraries.

## Features

- **Cross-Platform**: Works on Windows and Linux with minimal setup
- **Modern UI**: Sleek, professional interface with dark/light theme support
- **Theme Toggle**: Switch between dark and light modes with a single click
- **User-Friendly GUI**: Intuitive interface with visual feedback and animations
- **Smart Scanning**: Recursively scans library folders to find movies with multiple video files
- **Quality Indicators**: Green stars highlight recommended files to keep
- **Visual Feedback**: Colored checkboxes, hover effects, and animated scanning status
- **Organized Display**: Collapsible tree view with row striping for easy scanning
- **Safe Deletion**: Select specific files to delete with confirmation dialog
- **File Information**: Displays file sizes and full paths with modern tooltips
- **Persistent Settings**: Remembers your theme preference across sessions

## User Interface

The application features a modern, polished interface with:

- **Dark Mode (Default)**: Easy on the eyes with a professional dark color scheme
- **Light Mode**: Clean, bright alternative theme
- **One-Click Theme Toggle**: Switch themes instantly with the 🌙/☀️ button
- **Visual Hierarchy**:
  - Blue buttons for primary actions (Scan)
  - Red buttons for destructive actions (Delete)
  - Gray buttons for utility functions
- **Quality Recommendations**: Green stars (★) mark the best quality files to keep
- **Interactive Feedback**:
  - Animated scanning indicator with rotating dots
  - Hover effects on tree rows for easier tracking
  - Blue highlighting for selected items
  - Row striping for improved readability
- **Modern Typography**: Cross-platform fonts optimized for readability
- **Responsive Design**: Smooth animations and instant theme switching

## Requirements

- Python 3.7 or higher
- tkinter (included with most Python installations)

## Installation

### Quick Start

1. Clone or download this repository:
   ```bash
   git clone <repository-url>
   cd Plex_Duplicate_Detector
   ```

2. Run the application:
   ```bash
   python main.py
   ```

That's it! No additional dependencies required.

### Verifying tkinter Installation

Tkinter is usually included with Python, but if you get an import error:

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install python3-tk
```

**Linux (Fedora):**
```bash
sudo dnf install python3-tkinter
```

**Windows:**
Tkinter is included with the official Python installer from python.org. Make sure you didn't uncheck it during installation.

## Usage

1. **Launch the application**:
   ```bash
   python main.py
   ```

2. **Select your library**:
   - Click the "Browse" button
   - Navigate to your Plex library root folder
   - Click "Select Folder"

3. **Scan for duplicates**:
   - Click the blue "Scan" button
   - Watch the animated scanning indicator (rotating dots show progress)
   - Results appear automatically when complete

4. **Review results**:
   - Movies with multiple video files are displayed in a tree view with row striping
   - Files marked with green stars (★) are recommended to keep (best quality)
   - Hover over rows to highlight them
   - Click on a movie folder to expand and see individual files
   - Each file shows its name and size
   - Tooltips show full paths when hovering over files (appears after 0.5 seconds)

5. **Delete duplicates**:
   - Click checkboxes next to files you want to delete (selected rows turn blue)
   - Use "Select All" or "Deselect All" for bulk operations
   - Click the red "Delete Selected" button
   - Confirm the deletion when prompted

## Working with SMB/Network Shares

If your Plex library is stored on a NAS or network share, you'll need to mount it to your Linux filesystem first.

### Quick SMB Mount (Temporary)

1. **Install cifs-utils** (if not already installed):
   ```bash
   sudo apt-get install cifs-utils
   ```

2. **Create a mount point**:
   ```bash
   sudo mkdir -p /mnt/nas
   ```

3. **Mount the SMB share**:
   ```bash
   sudo mount -t cifs //SERVER_IP/SHARE_NAME /mnt/nas -o username=YOUR_USERNAME,password=YOUR_PASSWORD
   ```

4. **In the application**:
   - Type the mount path directly: `/mnt/nas/Movies`
   - Or click Browse and navigate to `/mnt/nas/Movies`
   - Click the **?** button next to the path field for more help

### Permanent SMB Mount (Recommended)

For automatic mounting on boot:

1. **Create credentials file** (more secure than storing password in fstab):
   ```bash
   nano ~/.smbcreds
   ```

   Add these lines:
   ```
   username=YOUR_USERNAME
   password=YOUR_PASSWORD
   domain=WORKGROUP
   ```

   Secure the file:
   ```bash
   chmod 600 ~/.smbcreds
   ```

2. **Edit /etc/fstab**:
   ```bash
   sudo nano /etc/fstab
   ```

   Add this line (replace with your details):
   ```
   //SERVER_IP/SHARE_NAME /mnt/nas cifs credentials=/home/YOUR_USER/.smbcreds,uid=1000,gid=1000,iocharset=utf8 0 0
   ```

3. **Mount all entries in fstab**:
   ```bash
   sudo mount -a
   ```

4. **Verify the mount**:
   ```bash
   ls /mnt/nas
   ```

Now you can use `/mnt/nas` as your library path in the application.

### Troubleshooting Network Shares

- **Permission denied**: Check your username/password and SMB share permissions
- **Host not found**: Verify the server IP/hostname is correct and accessible
- **Mount fails**: Ensure `cifs-utils` is installed
- **Files not accessible**: Check the `uid` and `gid` in mount options match your user ID (run `id` to check)

## Library Structure Assumption

The application assumes your Plex library follows this structure:

```
Library/
├── Movie 1/
│   ├── movie1.mp4
│   ├── movie1-720p.mkv
│   └── subtitles.srt
├── Movie 2/
│   ├── movie2.mkv
│   └── movie2-1080p.mp4
└── Movie 3/
    └── movie3.mp4
```

Each movie should be in its own folder. The scanner will detect all video files within each movie folder (including subfolders).

## Supported Video Formats

The following video file extensions are detected:
- .mp4
- .mkv
- .avi
- .mov
- .wmv
- .flv
- .m4v

## Creating a Standalone Executable

To create a standalone executable that doesn't require Python to be installed:

### Install PyInstaller

```bash
pip install pyinstaller
```

### Build the Executable

**For Windows:**
```bash
pyinstaller --onefile --windowed --name "Plex Duplicate Detector" main.py
```

**For Linux:**
```bash
pyinstaller --onefile --windowed --name "plex-duplicate-detector" main.py
```

The executable will be created in the `dist/` folder.

### Notes on Executables

- The `--onefile` flag creates a single executable file
- The `--windowed` flag prevents a console window from appearing (GUI only)
- First launch may be slow as PyInstaller extracts temporary files
- Executables are platform-specific (Windows .exe won't run on Linux and vice versa)

## Safety Features

- **Confirmation Dialog**: Always asks for confirmation before deleting files
- **Error Handling**: Gracefully handles permission errors and missing files
- **No Trash**: Files are permanently deleted (not moved to recycle bin)
- **Detailed Results**: Shows which files were successfully deleted and which failed

## Troubleshooting

### "No module named 'tkinter'" error

This means tkinter is not installed. See the "Verifying tkinter Installation" section above.

### Permission Errors

If you get permission errors when scanning or deleting:
- Make sure you have read/write permissions for the library folder
- On Linux, you may need to adjust folder permissions with `chmod`
- Try running the application with appropriate permissions

### Files Not Showing Up

- Make sure your video files have one of the supported extensions
- Check that each movie is in its own folder
- Verify the folder path is correct

### Scanning is Slow

- Large libraries may take time to scan
- The application remains responsive during scanning
- Progress is shown in the status bar

## Theme Customization

The application includes a sophisticated theme system with persistent preferences.

### Switching Themes

Click the theme toggle button (🌙 for dark mode, ☀️ for light mode) in the top-right corner of the window. Your preference is automatically saved and will be remembered the next time you launch the application.

### Theme Preferences

Theme preferences are stored in: `~/.plex_duplicate_detector/config.json`

This file also stores other settings like your last-used library path and window size.

### Color Schemes

**Dark Theme (Default)**:
- Easy on the eyes in low-light conditions
- Professional appearance with subtle contrast
- Colors: Dark grays, blue accents, green stars, blue checkboxes

**Light Theme**:
- Clean, bright interface for well-lit environments
- Same accent colors for consistency
- Colors: Light grays, white backgrounds, blue accents

## Development

### Project Structure

```
Plex_Duplicate_Detector/
├── main.py              # Application entry point
├── gui.py               # GUI components and logic
├── scanner.py           # File scanning functionality
├── file_operations.py   # File deletion and utilities
├── folder_tags.py       # Folder tagging system
├── quality_analyzer.py  # Video quality scoring
├── tooltip.py           # Modern tooltip system
├── themes/              # Theme system
│   ├── __init__.py
│   ├── theme_config.py  # Color palettes and spacing
│   ├── theme_manager.py # Theme application and persistence
│   └── widget_styles.py # Widget-specific styling
├── requirements.txt     # Python dependencies (still empty!)
├── CLAUDE.md           # Project guidance for Claude Code
└── README.md           # This file
```

### Running Tests

To test the application, create a test library structure with sample files:

```bash
mkdir -p test_library/Movie1
mkdir -p test_library/Movie2
touch test_library/Movie1/file1.mp4
touch test_library/Movie1/file2.mkv
touch test_library/Movie2/single.mp4
```

Then run the application and scan the `test_library` folder.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Acknowledgments

Built with Python and tkinter for cross-platform compatibility and minimal dependencies.
