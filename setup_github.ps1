# GitHub Repository Setup Script for Windows
# Run this script in PowerShell to initialize and push your repository to GitHub

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "   Duplicate File Finder - GitHub Setup" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Configure Git (if not already configured)
Write-Host "Step 1: Configuring Git..." -ForegroundColor Yellow
$github_username = Read-Host "Enter your GitHub username"
$github_email = Read-Host "Enter your email"

git config user.name "$github_username"
git config user.email "$github_email"

Write-Host "✓ Git configured" -ForegroundColor Green
Write-Host ""

# Step 2: Initialize repository (if not already done)
Write-Host "Step 2: Initializing Git repository..." -ForegroundColor Yellow
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Repository already initialized" -ForegroundColor Green
}
Write-Host ""

# Step 3: Add files
Write-Host "Step 3: Adding files to Git..." -ForegroundColor Yellow
git add .
Write-Host "✓ Files added" -ForegroundColor Green
Write-Host ""

# Step 4: Create initial commit
Write-Host "Step 4: Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Duplicate File Finder v1.0.0

Features:
- Multi-stage deduplication (size -> hash -> perceptual)
- Safe deletion with Recycle Bin support
- Intelligent file suggestions
- PyQt6 user interface with thumbnails
- Comprehensive logging and error handling"

Write-Host "✓ Initial commit created" -ForegroundColor Green
Write-Host ""

# Step 5: Set up GitHub remote
Write-Host "Step 5: Setting up GitHub remote..." -ForegroundColor Yellow
$repo_url = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/duplicate-file-finder.git)"

git remote add origin $repo_url
Write-Host "✓ Remote added" -ForegroundColor Green
Write-Host ""

# Step 6: Create and push to main branch
Write-Host "Step 6: Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "   ✓ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your repository on GitHub"
Write-Host "2. Add repository description and topics"
Write-Host "3. Enable GitHub Actions in Settings > Actions"
Write-Host "4. (Optional) Add a repository banner/logo"
Write-Host ""
