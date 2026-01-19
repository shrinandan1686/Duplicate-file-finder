# Duplicate File Finder

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

**A safe, user-friendly Windows desktop application for detecting and managing duplicate image files with intelligent suggestions and multiple safety mechanisms.**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage-guide) • [Security](#-safety-features) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- **Multi-Stage Deduplication**
  - Fast pre-filtering by file size and extension
  - SHA-256 hash-based exact duplicate detection
  - Optional perceptual hashing for finding similar images (resized, recompressed)

- **Safe Deletion**
  - Move to Recycle Bin (default, reversible)
  - Permanent deletion with multiple confirmation layers
  - Comprehensive logging of all deletion operations
  - Dry-run preview mode

- **Intelligent Suggestions**
  - Keep highest resolution
  - Keep oldest/newest file
  - Keep shortest path
  - Configurable strategies

- **User-Friendly Interface**
  - Progress tracking with real-time updates
  - Thumbnail previews for all images
  - Easy selection and batch operations
  - Export results to JSON

## 📋 Requirements

- Windows 10 or 11
- Python 3.10 or higher
- ~100MB disk space for application and thumbnails

## 🚀 Installation

### Step 1: Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/)

Make sure to check "Add Python to PATH" during installation.

### Step 2: Install Dependencies

Open PowerShell or Command Prompt in the application directory and run:

```powershell
pip install -r requirements.txt
```

This will install:
- `PyQt6` - UI framework
- `Pillow` - Image processing
- `imagehash` - Perceptual hashing (optional)
- `send2trash` - Recycle bin support

### Step 3: Run the Application

```powershell
python main.py
```

## 📖 Usage Guide

### 1. Select Folders

Click **Add Folder** to select one or more directories to scan. The application will recursively scan all subdirectories.

### 2. Configure Options

- **Include hidden/system folders**: By default, system folders are excluded for safety
- **Enable perceptual hashing**: Find visually similar images (slower but more thorough)
- **Similarity threshold**: Adjust how strict the similarity matching is (1-10, lower = stricter)

### 3. Start Scan

Click **Start Scan** to begin. Progress will be shown in real-time:
- Files scanned counter
- Current operation status
- Progress bar

### 4. Review Results

After scanning, you'll see:
- **Duplicate Groups**: Each group shows files with identical or similar content
- **Thumbnails**: Visual preview of each file
- **Metadata**: Path, size, resolution, creation date
- **⭐ Suggested file**: Automatically recommended file to keep

### 5. Select Files to Delete

For each group:
- **Select All Except Suggested**: Quick select all duplicates except the recommended keeper
- **Manual selection**: Check/uncheck individual files
- **Change strategy**: Try different suggestion strategies (highest resolution, oldest, etc.)

### 6. Delete Files

Click **Delete Selected Files** and choose:
- **Move to Recycle Bin** (Recommended): Files can be restored
- **Permanent Delete**: Requires typing "DELETE" for confirmation

A deletion log will be saved to `deletion_logs/` with complete details.

## 🛡️ Safety Features

### Multiple Confirmation Layers
1. Explicit file selection (no auto-deletion)
2. Deletion confirmation dialog
3. Type "DELETE" for permanent deletion
4. Final "Are you sure?" prompt

### Comprehensive Logging
All operations are logged to:
- `logs/app_YYYYMMDD.log` - Application log
- `deletion_logs/deletion_YYYYMMDD_HHMMSS.json` - Deletion records

### Error Handling
- Permission errors
- Locked files
- Corrupt images
All errors are logged and displayed with helpful messages.

## 📂 File Structure

```
Dublicate Finder/
├── main.py                    # Application entry point
├── config.json                # Configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── Core Modules:
│   ├── file_scanner.py        # Directory scanning
│   ├── deduplication_engine.py # Duplicate detection
│   ├── deletion_manager.py    # Safe file deletion
│   └── suggestion_engine.py   # File keeper suggestions
│
├── Utilities:
│   ├── utils.py               # Helper functions
│   └── logger.py              # Logging configuration
│
├── UI Components:
│   ├── ui_main_window.py      # Main window
│   ├── ui_results_view.py     # Results display
│   └── ui_dialogs.py          # Confirmation dialogs
│
└── Generated Directories:
    ├── logs/                  # Application logs
    ├── deletion_logs/         # Deletion records
    └── thumbnails/            # Cached thumbnails
```

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "supported_extensions": [".jpg", ".jpeg", ".png", ".heic", ".webp"],
  "scan_options": {
    "include_hidden_folders": false,
    "min_file_size_bytes": 1024
  },
  "suggestion_strategy": "keep_highest_resolution",
  "perceptual_hash": {
    "enabled": false,
    "similarity_threshold": 5
  }
}
```

## 🔍 How It Works

### Stage 1: Fast Pre-filter
Groups files by (size, extension). Files with different sizes can't be duplicates.

### Stage 2: Hash-based Detection
Computes SHA-256 hash for files in same size groups. Identical hashes = exact duplicates.

### Stage 3: Perceptual Hashing (Optional)
Uses image hashing algorithms (aHash) to detect visually similar images even if:
- Resized to different dimensions
- Recompressed with different quality
- Minor edits applied

## 📊 Performance

- **10,000 files**: ~30-60 seconds (hash-based only)
- **10,000 files**: ~2-5 minutes (with perceptual hashing)
- **Memory usage**: ~200-500 MB depending on image sizes

Tips for faster scanning:
- Disable perceptual hashing if not needed
- Reduce `max_worker_threads` if CPU usage is too high
- Increase `min_file_size_bytes` to skip tiny files

## ⚠️ Important Notes

### What Gets Scanned
- Only image files with supported extensions
- Recursively scans subdirectories
- Skips system/hidden folders by default

### What Doesn't Get Deleted
- Files not explicitly selected
- Files that are locked by other programs
- Files with permission errors

### Recycle Bin Limitations
- Very large files (>4GB) may not go to Recycle Bin on some systems
- Network drives may not support Recycle Bin

## 🐛 Troubleshooting

### Application won't start
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### "send2trash library not available"
- Install manually: `pip install send2trash`

### Thumbnails not showing
- Ensure Pillow is installed: `pip install Pillow`
- Check `thumbnails/` directory has write permissions

### Scan is very slow
- Disable perceptual hashing
- Reduce number of folders being scanned
- Check antivirus isn't scanning files

## 🚀 Future Enhancements

- [ ] Video file support
- [ ] Cloud storage scanning (Google Photos, OneDrive)
- [ ] Scheduled automatic scanning
- [ ] Auto-rules based on past decisions
- [ ] GPU-accelerated perceptual hashing
- [ ] Integration with file managers

## 📝 License

This software is provided as-is for personal use.

## 🤝 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review deletion logs in `deletion_logs/` directory
3. Ensure all dependencies are properly installed

---

**⚠️ Always backup important files before using any duplicate file finder!**
