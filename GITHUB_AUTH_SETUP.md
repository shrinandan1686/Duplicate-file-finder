# GitHub Personal Access Token Setup Guide

## ⚠️ Authentication Issue

Your push failed because GitHub no longer accepts password authentication. You need a **Personal Access Token (PAT)**.

---

## 🔑 Create Personal Access Token (2 Minutes)

### Step 1: Go to GitHub Token Settings
Visit: https://github.com/settings/tokens

OR Navigate manually:
1. Click your profile picture (top right)
2. Settings → Developer settings → Personal access tokens → Tokens (classic)

### Step 2: Generate New Token
1. Click **"Generate new token"** → **"Generate new token (classic)"**
2. **Note**: "Duplicate Finder Push Token"
3. **Expiration**: Choose 90 days (or longer)
4. **Scopes**: Check these boxes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Actions workflows)

### Step 3: Generate and Copy Token
1. Click **"Generate token"** at bottom
2. **IMPORTANT**: Copy the token immediately (starts with `ghp_`)
3. **Save it somewhere safe** - you won't see it again!

---

## 🚀 Push to GitHub Using Token

### Option 1: Quick Push (Recommended)
Run these commands in PowerShell:

```powershell
cd "C:\Users\achar\Documents\Dublicate Finder"

# Stage all files
git add .

# Commit
git commit -m "Initial commit: Duplicate File Finder v1.0.0"

# Add remote (if not already added)
git remote add origin https://github.com/shrinandan1686/Duplicate-file-finder.git

# Rename branch to main
git branch -M main

# Push (you'll be prompted for credentials)
git push -u origin main
```

**When prompted:**
- **Username**: `shrinandan1686`
- **Password**: Paste your Personal Access Token (ghp_...)

---

## Option 2: Save Token in Git (One-Time Setup)

This saves your credentials so you don't need to enter them every time:

```powershell
# Enable credential storage
git config --global credential.helper wincred

# Now push (enter token once, it will be saved)
git push -u origin main
```

---

## Option 3: Use Token in URL (Direct Method)

```powershell
# Replace YOUR_TOKEN with your actual token
git remote set-url origin https://YOUR_TOKEN@github.com/shrinandan1686/Duplicate-file-finder.git

# Push without prompts
git push -u origin main
```

**Example:**
```powershell
git remote set-url origin https://ghp_ABCD1234XYZ@github.com/shrinandan1686/Duplicate-file-finder.git
```

---

## ✅ Verify Push Success

After successful push, you should see:
```
Enumerating objects: XX, done.
Counting objects: 100% (XX/XX), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), XX.XX KiB | XX.XX MiB/s, done.
Total XX (delta X), reused 0 (delta 0), pack-reused 0
To https://github.com/shrinandan1686/Duplicate-file-finder.git
 * [new branch]      main -> main
```

Then visit: https://github.com/shrinandan1686/Duplicate-file-finder

---

## 🔒 Security Best Practices

✅ **DO:**
- Store tokens in Windows Credential Manager (using `credential.helper wincred`)
- Set token expiration dates
- Use tokens with minimal required scopes

❌ **DON'T:**
- Share your token with anyone
- Commit tokens to repositories
- Use the same token forever (expire and renew)

---

## ❓ Troubleshooting

### Error: "repository not found"
- Check repository URL is correct
- Verify you have access to the repository

### Error: "failed to push some refs"
- Pull first: `git pull origin main --rebase`
- Then push: `git push -u origin main`

### Token doesn't work
- Verify token has `repo` scope enabled
- Check token hasn't expired
- Regenerate a new token if needed

---

## 🎯 Next Steps After Successful Push

1. ✅ Visit your repository: https://github.com/shrinandan1686/Duplicate-file-finder
2. ✅ Add description and topics in repository settings
3. ✅ Enable GitHub Actions (Settings → Actions)
4. ✅ Star your own repository ⭐
5. ✅ Share with others!

---

**Ready? Follow Option 1 above to push your code!**
