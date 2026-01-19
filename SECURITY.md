# Security Policy

## Security Best Practices

This application is designed with security and safety as top priorities:

### File Handling Security

- **No Automatic Deletion**: The application never automatically deletes files
- **Multiple Confirmations**: All destructive operations require explicit user confirmation
- **Recycle Bin Default**: Files are moved to Recycle Bin by default, not permanently deleted
- **Dry-Run Mode**: Preview deletions before executing
- **Comprehensive Logging**: All operations are logged with timestamps

### Data Privacy

- **Local Processing Only**: All scanning and processing happens locally on your machine
- **No Network Requests**: The application does not send any data over the network
- **No Telemetry**: No usage statistics or analytics are collected
- **No User Tracking**: Your files and data remain private

### Code Security

- **No Hardcoded Secrets**: No API keys, passwords, or sensitive data in code
- **Input Validation**: File paths and user inputs are validated
- **Error Handling**: Comprehensive error handling prevents crashes
- **Permission Checks**: Validates file permissions before operations

### Safe Dependencies

All dependencies are well-established, open-source libraries:
- PyQt6 - Official Qt bindings for Python
- Pillow - Python Imaging Library (PIL fork)
- imagehash - Pure Python perceptual hashing
- send2trash - Cross-platform send to trash

## Reporting Security Issues

If you discover a security vulnerability, please report it by:

1. **DO NOT** open a public GitHub issue
2. Email the maintainer directly (if applicable)
3. Provide detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Security Checklist for Users

Before using this application:

- ✅ **Backup Important Files**: Always maintain backups of critical data
- ✅ **Review Selections**: Carefully review files selected for deletion
- ✅ **Use Recycle Bin**: Prefer Recycle Bin over permanent deletion
- ✅ **Test on Sample Data**: Try with test files first
- ✅ **Check Logs**: Review `logs/` and `deletion_logs/` after operations

## Secure Configuration

The `config.json` file contains only non-sensitive settings:
- File extensions to scan
- UI preferences
- Performance tuning parameters

**No sensitive information should be added to config.json**

## File System Access

The application requires file system access to:
- Read files for scanning and hashing
- Generate thumbnails for preview
- Delete files (only when explicitly confirmed by user)
- Write logs to `logs/` and `deletion_logs/` directories

**The application only accesses directories you explicitly select.**

## Third-Party Code Audit

All dependencies can be reviewed:
```bash
pip show PyQt6 Pillow imagehash send2trash
```

## Updates and Patches

- Check for updates regularly
- Review changelogs for security fixes
- Keep dependencies up to date: `pip install --upgrade -r requirements.txt`

## Known Limitations

- ⚠️ Files on network drives may behave differently
- ⚠️ Very large files (>4GB) may not support Recycle Bin on all systems
- ⚠️ Read-only or locked files cannot be deleted

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Last Updated**: 2026-01-19
