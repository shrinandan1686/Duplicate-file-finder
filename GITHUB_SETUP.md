# Quick Start: Pushing to GitHub

## Prerequisites

1. Install Git: https://git-scm.com/download/win
2. Create a GitHub account: https://github.com
3. Create a new repository on GitHub (don't initialize with README)

## Option 1: Automated Setup (Recommended)

### For Windows (PowerShell):
```powershell
.\setup_github.ps1
```

### For Linux/Mac:
```bash
chmod +x setup_github.sh
./setup_github.sh
```

The script will guide you through the process.

---

## Option 2: Manual Setup

### 1. Configure Git (First Time Only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Initialize Repository
```bash
cd "C:\Users\achar\Documents\Dublicate Finder"
git init
```

### 3. Add Files
```bash
git add .
```

### 4. Create Initial Commit
```bash
git commit -m "Initial commit: Duplicate File Finder v1.0.0"
```

### 5. Connect to GitHub
```bash
# Replace with your actual repository URL
git remote add origin https://github.com/yourusername/duplicate-file-finder.git
```

### 6. Push to GitHub
```bash
git branch -M main
git push -u origin main
```

---

## Important Files for GitHub

✅ **Included in this repository:**

- `.gitignore` - Excludes unnecessary files (logs, cache, user data)
- `README.md` - Comprehensive project documentation
- `LICENSE` - MIT License
- `SECURITY.md` - Security policy and best practices
- `CONTRIBUTING.md` - Contribution guidelines
- `.github/workflows/tests.yml` - Automated testing with GitHub Actions

---

## Security Notes

### Files Excluded by .gitignore:
- `logs/` - Application logs (user-specific)
- `deletion_logs/` - Deletion records (user-specific)
- `thumbnails/` - Cached thumbnails (user-specific)
- `__pycache__/` - Python cache
- Virtual environments

### Safe to Commit:
- Source code (`.py` files)
- Configuration template (`config.json`)
- Documentation (`.md` files)
- Tests (`test_core.py`)
- Requirements (`requirements.txt`)

**⚠️ Never commit:**
- User's personal files or images
- Logs containing file paths
- Any directories with sensitive data

---

## After Pushing to GitHub

1. **Add Description**: Go to repository settings → Add description
2. **Add Topics**: Add topics like `python`, `duplicate-finder`, `file-manager`, `pyqt6`
3. **Enable Actions**: Settings → Actions → Allow all actions
4. **Add Badge**: Copy badge from Actions tab to README
5. **Share**: Share your repository link!

---

## Repository Suggestions

### Recommended Repository Name:
`duplicate-file-finder`

### Suggested Description:
"A safe, user-friendly Windows application for detecting and managing duplicate image files with multi-stage deduplication and intelligent suggestions."

### Suggested Topics:
- `python`
- `pyqt6`
- `duplicate-finder`
- `file-manager`
- `image-processing`
- `windows`
- `desktop-application`
- `hash-algorithm`
- `perceptual-hash`

---

## Troubleshooting

### Git not recognized
Install Git from: https://git-scm.com/download/win

### Permission denied
Use SSH instead of HTTPS:
```bash
git remote set-url origin git@github.com:yourusername/duplicate-file-finder.git
```

### Large files warning
All project files are small. If you see this, check you didn't accidentally add `logs/` or `thumbnails/`

### Already initialized
If repository already exists locally:
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

---

## Next Steps

- ⭐ Star the repository
- 🐛 Open issues for bugs
- 💡 Suggest features
- 🤝 Contribute improvements
- 📢 Share with others

Enjoy sharing your project! 🚀
