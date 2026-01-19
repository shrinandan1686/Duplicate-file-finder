# Fresh GitHub Repository Setup Guide

## Step 1: Delete the Old Repository on GitHub

1. **Go to your repository**: https://github.com/shrinandan1686/Duplicate-file-finder
2. **Click "Settings"** (tab at the top)
3. **Scroll all the way down** to the "Danger Zone" section
4. **Click "Delete this repository"**
5. **Type the repository name** to confirm: `shrinandan1686/Duplicate-file-finder`
6. **Click "I understand the consequences, delete this repository"**

✅ Repository deleted on GitHub

---

## Step 2: Clean Local Git History

Run these commands in PowerShell:

```powershell
cd "C:\Users\achar\Documents\Dublicate Finder"

# Remove Git remote connection
git remote remove origin

# Delete the entire .git folder (removes all history)
Remove-Item -Recurse -Force .git

# Verify Git is gone
Test-Path .git
# Should return: False
```

✅ Local Git history cleaned

---

## Step 3: Create New GitHub Repository

1. **Go to**: https://github.com/new
2. **Repository name**: `Duplicate-file-finder` (or your preferred name)
3. **Description**: "Safe duplicate file finder with multi-stage deduplication and intelligent suggestions"
4. **Public** (recommended for portfolio)
5. **DO NOT** check any boxes (no README, .gitignore, or license)
6. **Click "Create repository"**
7. **Copy the repository URL** (should be: `https://github.com/shrinandan1686/Duplicate-file-finder.git`)

✅ New repository created

---

## Step 4: Initialize and Push Fresh Code

Now all commits will show **shrinandan1686** as the author!

```powershell
cd "C:\Users\achar\Documents\Dublicate Finder"

# Initialize new Git repository
git init

# Verify Git config is correct
git config user.name
# Should show: shrinandan1686

git config user.email
# Should show: acharaya.srinandan@gmail.com

# If not correct, set them:
git config --global user.name "shrinandan1686"
git config --global user.email "acharaya.srinandan@gmail.com"

# Add all files
git add .

# Create initial commit with YOUR name
git commit -m "Initial commit: Duplicate File Finder v1.0.0

Features:
- Multi-stage deduplication (size → hash → perceptual)
- Safe deletion with Recycle Bin support
- Intelligent file suggestions with 5 strategies
- PyQt6 user interface with full file paths
- Clean, user-friendly UI design
- Comprehensive logging and error handling
- GitHub Actions CI/CD workflow"

# Add your new repository
git remote add origin https://github.com/shrinandan1686/Duplicate-file-finder.git

# Push to GitHub
git branch -M main
git push -u origin main
```

✅ Fresh repository with correct author name!

---

## Step 5: Verify on GitHub

Visit your repository: https://github.com/shrinandan1686/Duplicate-file-finder

All commits should now show **shrinandan1686** as the author! ✅

---

## Quick Commands (Copy-Paste)

```powershell
# Step 2: Clean local Git
cd "C:\Users\achar\Documents\Dublicate Finder"
git remote remove origin
Remove-Item -Recurse -Force .git

# Step 4: Fresh push (after creating new repo on GitHub)
git init
git add .
git commit -m "Initial commit: Duplicate File Finder v1.0.0"
git remote add origin https://github.com/shrinandan1686/Duplicate-file-finder.git
git branch -M main
git push -u origin main
```

---

**Ready?** Start with Step 1 above! Let me know when you've created the new repository and I'll help you push.
