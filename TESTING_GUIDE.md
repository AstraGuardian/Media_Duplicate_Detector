# Testing Guide: Tooltips and Quality Recommendations

## Overview

This guide helps you test the newly implemented features:
1. **Full path tooltips** - Hover over items to see complete paths
2. **Quality recommendations** - ⭐ star marks the best file/folder

## Test Library Setup

A test library has been created at: `test_library/`

### Structure:
```
test_library/
├── Movie1 (2023)/
│   ├── Movie1.2023.1080p.BluRay.x265.HEVC.mkv (500 MB) ← Should get ⭐
│   └── Movie1.2023.720p.WEB-DL.x264.mkv (200 MB)
│
├── Movie2 (2024)/
│   ├── Movie2.2024.2160p.4K.BluRay.HEVC.mkv (800 MB) ← Should get ⭐
│   ├── Movie2.2024.1080p.x264.mkv (400 MB)
│   └── Movie2.2024.720p.WEBRip.mkv (150 MB)
│
├── Matrix (1999) 1080p BluRay/
│   └── Matrix.1999.1080p.BluRay.x264.mkv (600 MB)
│
├── Matrix (1999) 720p/
│   └── Matrix.1999.720p.x264.mkv (300 MB)
│
└── Matrix 2160p 4K/ ← Should get ⭐ (best folder)
    └── Matrix.1999.2160p.4K.HEVC.mkv (1000 MB)
```

## Test 1: Video Files Tab - Quality Recommendations

### Steps:
1. **Launch the application**:
   ```bash
   python3 main.py
   ```

2. **Scan the test library**:
   - Type or paste the path: `/home/wes/cli-ai-projects/claude_projects/Plex_Duplicate_Detector/test_library`
   - Click **Scan**
   - Wait for scan to complete

3. **Verify quality recommendations**:
   - Go to **Video Files** tab
   - Expand "Movie1 (2023)" group
     - ✅ **Expected**: `⭐ Movie1.2023.1080p.BluRay.x265.HEVC.mkv` has star
     - ✅ **Expected**: `Movie1.2023.720p.WEB-DL.x264.mkv` has NO star

   - Expand "Movie2 (2024)" group
     - ✅ **Expected**: `⭐ Movie2.2024.2160p.4K.BluRay.HEVC.mkv` has star
     - ✅ **Expected**: Other two files have NO star

### Why these files get stars:
- **Movie1**: 1080p HEVC beats 720p x264 (higher resolution + better codec)
- **Movie2**: 2160p 4K HEVC beats others (highest resolution + best codec + largest size)

## Test 2: Video Files Tab - Tooltips

### Steps:
1. **Test tooltip appearance**:
   - Hover your mouse over "Movie1 (2023)" (parent item)
   - ✅ **Expected**: After ~500ms, tooltip appears showing full path
   - ✅ **Expected**: Tooltip shows: `/home/wes/.../test_library/Movie1 (2023)`

2. **Test tooltip on file items**:
   - Hover over "Movie1.2023.1080p.BluRay.x265.HEVC.mkv" (child item)
   - ✅ **Expected**: Tooltip shows: `/home/wes/.../test_library/Movie1 (2023)/Movie1.2023.1080p.BluRay.x265.HEVC.mkv`

3. **Test tooltip hiding**:
   - Move mouse to different item
   - ✅ **Expected**: Previous tooltip disappears
   - ✅ **Expected**: New tooltip appears after 500ms

4. **Test tooltip positioning**:
   - Move tooltip near screen edges
   - ✅ **Expected**: Tooltip stays on screen (doesn't go off-screen)

## Test 3: Duplicate Folders Tab - Quality Recommendations

### Steps:
1. **Add library paths**:
   - Go to **Duplicate Folders** tab
   - Click **Add Library Path**
   - Type: `/home/wes/cli-ai-projects/claude_projects/Plex_Duplicate_Detector/test_library`
   - Click **Add**

2. **Scan for duplicates**:
   - Select **Exact Match** mode
   - Click **Scan Libraries**
   - Wait for scan to complete

3. **Verify quality recommendations**:
   - Expand the "Matrix" duplicate group
   - ✅ **Expected**: Three folders appear:
     - `Matrix (1999) 1080p BluRay` - NO star
     - `Matrix (1999) 720p` - NO star
     - `⭐ Matrix 2160p 4K` - HAS star
   - ✅ **Expected**: The "Matrix 2160p 4K" folder should also show `[BEST]` tag

### Why "Matrix 2160p 4K" gets the star:
- Highest resolution (2160p/4K) detected in folder name
- Largest file size (1000 MB vs 600 MB vs 300 MB)
- HEVC codec detected in filename

## Test 4: Duplicate Folders Tab - Tooltips

### Steps:
1. **Test tooltip on folder items**:
   - Hover over "Matrix (1999) 1080p BluRay"
   - ✅ **Expected**: Tooltip shows: `/home/wes/.../test_library/Matrix (1999) 1080p BluRay`

2. **Test tooltip on best folder**:
   - Hover over "⭐ Matrix 2160p 4K"
   - ✅ **Expected**: Tooltip shows: `/home/wes/.../test_library/Matrix 2160p 4K`

## Quality Scoring System

The quality analyzer uses this weighted scoring:
- **File Size**: 30% (larger = better, capped at 100 points)
- **Codec**: 25% (h265/HEVC = 100, h264/x264 = 50)
- **Resolution**: 30% (4K = 400, 1080p = 300, 720p = 200, 480p = 100)
- **Source**: 15% (BluRay = 150, WEB-DL = 100, WEBRip = 80, DVD = 50)

### Filename Parsing Examples:
- `Movie.2023.2160p.4K.BluRay.HEVC.mkv`
  - Resolution: 2160p (400 points)
  - Codec: HEVC (100 points)
  - Source: BluRay (150 points)

- `Movie.2023.1080p.WEB-DL.x264.mkv`
  - Resolution: 1080p (300 points)
  - Codec: x264 (50 points)
  - Source: WEB-DL (100 points)

## Edge Cases to Test

### Single file (no comparison):
- Create a folder with only one video file
- ✅ **Expected**: No star appears (nothing to compare against)

### Tied scores:
- Create two files with identical quality indicators and same size
- ✅ **Expected**: Star appears on alphabetically first file

### No quality indicators:
- Create a file named "movie.mkv" (no resolution, codec, or source info)
- ✅ **Expected**: File size alone determines ranking

## Cleanup

After testing, you can remove the test library:
```bash
rm -rf test_library/
```

## Troubleshooting

### Tooltip not appearing:
- Make sure you're hovering for at least 500ms
- Check that the item has a valid path in its tags

### Wrong file/folder getting the star:
- Verify the filename contains quality indicators
- Check that file sizes are correct (use `ls -lh`)
- Review the scoring algorithm above

### Star emoji not visible:
- Check your terminal/font supports Unicode emoji
- The ⭐ emoji should appear before the filename

## Success Criteria

All features are working correctly if:
- ✅ Tooltips appear on hover for all items (Video Files and Duplicate Folders tabs)
- ✅ Tooltips show complete file/folder paths
- ✅ Best quality files get ⭐ star in Video Files tab
- ✅ Best quality folders get ⭐ star in Duplicate Folders tab
- ✅ Best folders also show [BEST] tag in Duplicate Folders tab
- ✅ Only one star per duplicate group
- ✅ No star when only one item in group
- ✅ Application remains responsive during scanning
