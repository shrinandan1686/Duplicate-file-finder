# Duplicate File Finder

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

**A safe, user-friendly Windows desktop application for detecting and managing duplicate image files with intelligent suggestions and multiple safety mechanisms.**

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage-guide) • [Safety](#-safety-features) • [Troubleshooting](#-troubleshooting)

</div>

---

## Features

- **Multi-Stage Deduplication**
  - Fast pre-filtering by file size and extension
  - SHA-256 hash-based exact duplicate detection
  - Optional perceptual hashing for visually similar images (resized, recompressed)

- **Safe Deletion**
  - Move to Recycle Bin (default, reversible)
  - Permanent deletion with multiple confirmation layers
  - Comprehensive JSON logs of all deletion operations
  - Dry-run preview mode

- **Intelligent Suggestions**
  - Keep highest resolution
  - Keep oldest/newest file
  - Keep shortest path
  - Configurable strategies

- **User-Friendly Interface**
  - Dark-themed modern UI
  - Progress tracking with real-time updates
  - Thumbnail previews for all images
  - Export results to JSON
  - Load previous scan results

---

## Quick Start

### Prerequisites

- **Windows 10 or 11**
- **Python 3.10 or higher** — download from [python.org](https://www.python.org/downloads/)
  - During installation, check **"Add Python to PATH"**

### 1. Clone the repository

```powershell
git clone https://github.com/shrinandan1686/Duplicate-file-finder.git
cd "Duplicate-file-finder"
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs:
| Package | Purpose |
|---------|---------|
| `PyQt6 >= 6.6.0` | Desktop GUI framework |
| `Pillow >= 10.0.0` | Image processing and thumbnails |
| `imagehash >= 4.3.1` | Perceptual hashing for similar images |
| `send2trash >= 1.8.2` | Safe Recycle Bin deletion |

### 4. Run the application

```powershell
python main.py
```

---

## Project Structure

```
Duplicate-file-finder/
│
├── main.py                    # Application entry point
├── config.json                # Runtime configuration
├── requirements.txt           # Python dependencies
│
├── Core Modules
│   ├── file_scanner.py        # Recursive directory scanning
│   ├── deduplication_engine.py# Duplicate detection (hash + perceptual)
│   ├── deletion_manager.py    # Safe file deletion with logging
│   └── suggestion_engine.py   # Smart keeper suggestions
│
├── Utilities
│   ├── utils.py               # File helpers, hashing, thumbnails
│   └── logger.py              # Rotating file + console logging
│
├── UI Components
│   ├── ui_main_window.py      # Main application window
│   ├── ui_results_view.py     # Duplicate results display
│   ├── ui_dialogs.py          # Confirmation dialogs
│   └── ui_styles.py           # Dark theme stylesheet
│
├── Tests
│   └── test_core.py           # Core backend tests (no UI required)
│
└── Generated at runtime (gitignored)
    ├── logs/                  # App logs (app_YYYYMMDD.log)
    ├── deletion_logs/         # Deletion records (deletion_*.json)
    └── thumbnails/            # Cached image thumbnails
```

---

## Usage Guide

### 1. Select Folders

Click **Add Folder** to choose directories to scan. The app recursively scans all subdirectories.

### 2. Configure Options

| Option | Default | Description |
|--------|---------|-------------|
| Include hidden/system folders | Off | System folders excluded for safety |
| Enable perceptual hashing | Off | Finds visually similar images (slower) |
| Similarity threshold | 5 | 1–10, lower = stricter matching |

### 3. Start Scan

Click **Start Scan**. Real-time progress shows:
- Files scanned counter
- Current operation status
- Progress bar

### 4. Review Results

Each duplicate group shows:
- **Thumbnails** — visual preview of each file
- **Metadata** — path, size, resolution, creation date
- **Suggested file** — automatically recommended keeper

### 5. Select Files to Delete

- **Select All Except Suggested** — quick-select all duplicates
- **Manual selection** — check/uncheck individual files
- **Change strategy** — switch between suggestion strategies

### 6. Delete Files

Click **Delete Selected Files** and choose:
- **Move to Recycle Bin** *(Recommended)* — reversible
- **Permanent Delete** — requires typing `DELETE` to confirm, then a final prompt

A deletion log is saved to `deletion_logs/` with full details.

### 7. Load Previous Results

Use **Load Previous Results** to reload a saved `duplicate_results.json` scan without rescanning.

---

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "supported_extensions": [".jpg", ".jpeg", ".png", ".heic", ".webp", ".gif", ".bmp"],
  "scan_options": {
    "include_hidden_folders": false,
    "include_system_folders": false,
    "min_file_size_bytes": 1024
  },
  "suggestion_strategy": "keep_highest_resolution",
  "ui_preferences": {
    "thumbnail_size": 150,
    "theme": "light"
  },
  "performance": {
    "max_worker_threads": 4,
    "hash_chunk_size_kb": 64
  },
  "perceptual_hash": {
    "enabled": false,
    "similarity_threshold": 5
  }
}
```

---

## How It Works

### Stage 1 — Fast Pre-filter
Groups files by `(size, extension)`. Files with different sizes cannot be duplicates — eliminates most files instantly.

### Stage 2 — SHA-256 Hash Detection
Computes SHA-256 hash for each file in same-size groups using chunked reading. Identical hashes = exact duplicates.

### Stage 3 — Perceptual Hashing *(optional)*
Uses `imagehash` (aHash algorithm) to detect visually similar images even if:
- Resized to different dimensions
- Recompressed at different quality
- Minor edits applied

---

## Running Tests

Tests cover core backend logic without requiring a display:

```powershell
python test_core.py
```

This validates:
- File Scanner — directory traversal and metadata extraction
- Deduplication Engine — hash-based grouping
- Suggestion Engine — keeper selection strategies
- Deletion Manager — dry-run and preview modes

---

## Safety Features

### Multiple Confirmation Layers
1. Explicit file selection required — no auto-deletion
2. Deletion method selection dialog
3. Type `DELETE` to confirm permanent deletion
4. Final "Are you sure?" prompt

### Comprehensive Logging

| Log Type | Location | Format |
|----------|----------|--------|
| Application log | `logs/app_YYYYMMDD.log` | Rotating (10 MB max, 5 backups) |
| Deletion records | `deletion_logs/deletion_YYYYMMDD_HHMMSS.json` | JSON with full details |

### Error Handling
- Permission errors — logged, file skipped
- Locked files — detected before deletion attempt
- Corrupt images — caught, reported, skipped

---

## Performance

| Workload | Time |
|----------|------|
| 10,000 files (hash only) | ~30–60 seconds |
| 10,000 files (with perceptual) | ~2–5 minutes |
| Memory usage | ~200–500 MB |

**Tips for faster scans:**
- Disable perceptual hashing unless needed
- Lower `max_worker_threads` if CPU usage is too high
- Raise `min_file_size_bytes` to skip small files

---

## Troubleshooting

**Application won't start**
```powershell
python --version          # Must be 3.10+
pip install -r requirements.txt --force-reinstall
```

**Virtual environment not activating**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\activate
```

**"send2trash library not available"**
```powershell
pip install send2trash
```

**Thumbnails not showing**
```powershell
pip install Pillow
# Also verify thumbnails/ directory has write permissions
```

**Scan is very slow**
- Disable perceptual hashing in `config.json`
- Reduce the number of folders scanned
- Check that antivirus isn't intercepting file reads

---

## Important Notes

- Only image files with supported extensions are scanned
- System and hidden folders are excluded by default
- Files are never auto-deleted — explicit selection is always required
- Very large files (>4 GB) may not go to Recycle Bin on some configurations
- Network drives may not support Recycle Bin

---

**Always back up important files before using any duplicate finder.**
