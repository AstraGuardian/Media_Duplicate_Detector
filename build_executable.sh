#!/bin/bash
# Build script for Media Duplicate Detector executable

echo "Building Media Duplicate Detector executable..."

# Activate virtual environment
source build_env/bin/activate

# Build the executable
pyinstaller --name="Media-Duplicate-Detector" \
    --onefile \
    --windowed \
    --add-data="themes:themes" \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=tkinter.filedialog \
    --hidden-import=tkinter.messagebox \
    main.py

echo ""
echo "Build complete!"
echo "Executable location: dist/Media-Duplicate-Detector"
echo ""
echo "To run the executable:"
echo "  ./dist/Media-Duplicate-Detector"
