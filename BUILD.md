# Building Executables

This document explains how to build standalone executables for Media Duplicate Detector.

## Linux

### Prerequisites
- Python 3.7 or higher
- Virtual environment support

### Building

1. **Run the build script**:
   ```bash
   ./build_executable.sh
   ```

2. **Find the executable**:
   The executable will be created at: `dist/Media-Duplicate-Detector`

3. **Test it**:
   ```bash
   ./dist/Media-Duplicate-Detector
   ```

### First-Time Setup

If the build script fails, you may need to create the build environment first:

```bash
python3 -m venv build_env
source build_env/bin/activate
pip install pyinstaller
./build_executable.sh
```

## Windows

### Prerequisites
- Python 3.7 or higher installed on Windows

### Building

1. **Create virtual environment** (first time only):
   ```cmd
   python -m venv build_env
   build_env\Scripts\activate
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```cmd
   build_env\Scripts\activate
   pyinstaller --name="Media-Duplicate-Detector" ^
       --onefile ^
       --windowed ^
       --add-data="themes;themes" ^
       --hidden-import=tkinter ^
       --hidden-import=tkinter.ttk ^
       --hidden-import=tkinter.filedialog ^
       --hidden-import=tkinter.messagebox ^
       main.py
   ```

3. **Find the executable**:
   The executable will be created at: `dist\Media-Duplicate-Detector.exe`

## Distribution

The built executables are standalone and include:
- Python interpreter
- All required Python libraries
- Application themes
- All application code

Users do NOT need Python installed to run the executable.

### File Sizes (Approximate)
- **Linux**: ~12 MB
- **Windows**: ~15-20 MB

## Notes

- **Platform-specific**: Executables must be built on the target platform
  - Build on Linux for Linux users
  - Build on Windows for Windows users
- **Themes**: The `themes` folder is bundled into the executable
- **No dependencies**: Users don't need Python or any libraries installed

## Troubleshooting

### Linux: Missing tkinter
If the build fails with tkinter errors:
```bash
sudo apt-get install python3-tk
```

### Windows: PyInstaller not found
Make sure you activate the virtual environment:
```cmd
build_env\Scripts\activate
```

### Executable doesn't run
- **Linux**: Make sure it's executable: `chmod +x dist/Media-Duplicate-Detector`
- **Windows**: Check Windows Defender didn't quarantine it
