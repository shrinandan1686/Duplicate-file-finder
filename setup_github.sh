#!/bin/bash
# GitHub Repository Setup Script
# Run this script to initialize and push your repository to GitHub

echo "==================================================================="
echo "   Duplicate File Finder - GitHub Setup"
echo "==================================================================="
echo ""

# Step 1: Configure Git (if not already configured)
echo "Step 1: Configuring Git..."
read -p "Enter your GitHub username: " github_username
read -p "Enter your email: " github_email

git config user.name "$github_username"
git config user.email "$github_email"

echo "✓ Git configured"
echo ""

# Step 2: Initialize repository (if not already done)
echo "Step 2: Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Repository already initialized"
fi
echo ""

# Step 3: Add files
echo "Step 3: Adding files to Git..."
git add .
echo "✓ Files added"
echo ""

# Step 4: Create initial commit
echo "Step 4: Creating initial commit..."
git commit -m "Initial commit: Duplicate File Finder v1.0.0

Features:
- Multi-stage deduplication (size → hash → perceptual)
- Safe deletion with Recycle Bin support
- Intelligent file suggestions
- PyQt6 user interface with thumbnails
- Comprehensive logging and error handling"

echo "✓ Initial commit created"
echo ""

# Step 5: Set up GitHub remote
echo "Step 5: Setting up GitHub remote..."
read -p "Enter your GitHub repository URL (e.g., https://github.com/username/duplicate-file-finder.git): " repo_url

git remote add origin "$repo_url"
echo "✓ Remote added"
echo ""

# Step 6: Create and push to main branch
echo "Step 6: Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "==================================================================="
echo "   ✓ Successfully pushed to GitHub!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "1. Visit your repository on GitHub"
echo "2. Add repository description and topics"
echo "3. Enable GitHub Actions in Settings > Actions"
echo "4. (Optional) Add a repository banner/logo"
echo ""
