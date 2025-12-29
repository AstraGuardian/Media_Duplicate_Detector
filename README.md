# Media Duplicate Detector

A cross-platform GUI application that helps you find and manage duplicate video files in your media libraries, making it easy to free up storage space.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

## About This Project

**Full Disclosure**: I'm not a programmer. This entire application was built with the help of [Claude Code](https://claude.ai/code), Anthropic's AI coding assistant. I had a problem (too many duplicate movie files eating up my storage), described what I needed, and Claude Code helped me build a solution.

The app works great for my needs, which is why I'm sharing it publicly. However, because I don't have traditional coding expertise:
- **Code reviews are especially welcome** - I trust Claude Code, but I can't personally verify everything
- **Bug fixes might take time** - I'll need Claude Code's help to understand and fix issues
- **Community contributions are highly valued** - Your expertise can make this better for everyone

If you're an experienced developer and you see improvements to be made, please contribute! This project is a perfect example of what AI-assisted development can achieve, and I'm excited to see how the community can enhance it.

## What It Does

Media Duplicate Detector scans your movie library folders and identifies movies that have multiple video files. This commonly happens when you:
- Have different quality versions of the same movie (1080p and 4K)
- Downloaded replacements but forgot to delete the old files
- Have backup copies taking up extra space

The app shows you all duplicates in an easy-to-browse tree view, lets you compare file details (size, resolution, bitrate), and allows you to safely delete unwanted files—all from a user-friendly interface.

## Features

- **Smart Scanning**: Recursively scans your library to find folders with multiple video files
- **Visual Quality Comparison**: Shows resolution, file size, bitrate, codec, and quality scores
- **Quality Recommendations**: Highlights the highest-quality version to help you decide what to keep
- **Flexible Selection**: Multi-select files for batch deletion
- **Safe Deletion**: Confirmation dialogs prevent accidental data loss
- **Modern UI**: Clean, theme-able interface with helpful tooltips
- **Network Share Support**: Works with mounted network drives and SMB/CIFS shares
- **No Dependencies**: Uses only Python standard library (tkinter)

## Screenshots

*(Coming soon - contributions welcome!)*

## Installation

### Requirements

- Python 3.7 or higher
- tkinter (usually comes pre-installed with Python)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AstraGuardian/Media_Duplicate_Detector.git
   cd Media_Duplicate_Detector
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

   Or on Linux/Mac:
   ```bash
   chmod +x main.py
   ./main.py
   ```

That's it! No installation or dependencies needed.

### Verify tkinter Installation

If you get an error about tkinter, you may need to install it:

**Ubuntu/Debian**:
```bash
sudo apt-get install python3-tk
```

**Fedora/RHEL**:
```bash
sudo dnf install python3-tkinter
```

**Windows/Mac**: tkinter comes pre-installed with Python

## Usage

1. **Launch the app**: Run `python main.py`
2. **Select your library**: Click "Browse" or type the path to your movie library folder
3. **Scan**: Click "Scan for Duplicates"
4. **Review**: Browse the results—movies with duplicates are shown in a tree view
5. **Compare**: Click on files to see quality details and recommendations
6. **Select**: Check the boxes next to files you want to delete
7. **Delete**: Click "Delete Selected Files" and confirm

### Network Shares

The app supports network shares:
- **Windows**: Use UNC paths like `\\server\share\Movies`
- **Linux**: Mount SMB shares first (click the **?** button in the app for instructions)

## How It Works

The application assumes your library is structured like this:

```
Movies/
├── The Matrix (1999)/
│   ├── The Matrix (1999) - 1080p.mkv
│   ├── The Matrix (1999) - 4K.mkv
│   └── subtitles.srt
├── Inception (2010)/
│   └── Inception (2010).mp4
└── ...
```

It scans each movie folder (including nested subfolders) and flags any folder containing 2+ video files as having duplicates.

## Contributing

**Contributions are especially welcome!** Since I built this with AI assistance and I'm not an experienced developer, I genuinely value input from the community. Whether it's:
- Bug fixes or security improvements
- Code quality enhancements
- New features
- Documentation improvements
- Even just reviewing code and suggesting changes

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Project Maintenance

**How This Project Works**:
- I maintain this project casually in my spare time
- I use Claude Code to help me understand issues and implement fixes
- Pull requests may take time to review as I work through them with AI assistance
- The app currently solves my needs, so active development is limited
- Community contributions keep this project growing

**If you need something urgently**: Feel free to fork the project and make it your own. That's what open source is all about!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This means you're free to use, modify, and distribute this software, even commercially. No warranties provided.

## Support

- **Issues**: Found a bug? [Open an issue](https://github.com/AstraGuardian/Media_Duplicate_Detector/issues)
- **Questions**: Check existing issues or open a new one
- **Feature Requests**: Open an issue with your idea

## Acknowledgments

- Built with **Python** and **tkinter** to keep things simple and dependency-free
- Created with assistance from **Claude Code** by Anthropic
- Inspired by the need to manage my ever-growing media library

---

**Safety Note**: This tool permanently deletes files. Always ensure you have backups before using any file deletion features. Only use this on media you have the rights to manage.
