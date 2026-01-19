# Contributing to Duplicate File Finder

Thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Windows version, Python version)
- Relevant logs from `logs/` directory

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first
- Describe the use case
- Explain how it would benefit users

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation
4. **Test your changes**
   ```bash
   python test_core.py
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add: feature description"
   ```
6. **Push and create a Pull Request**

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/duplicate-file-finder.git
cd duplicate-file-finder

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_core.py

# Run the application
python main.py
```

## Code Style Guidelines

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Keep functions focused and modular
- Add error handling with appropriate logging

### Example

```python
def compute_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
    """
    Compute cryptographic hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal hash string or None if failed
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Hash computation failed: {e}")
        return None
```

## Testing

- All core modules should have tests in `test_core.py`
- Test edge cases and error conditions
- Ensure tests pass before submitting PR

## Documentation

- Update README.md if adding new features
- Update SECURITY.md if changing security-related code
- Add inline comments for complex algorithms

## Pull Request Process

1. Ensure tests pass
2. Update documentation
3. Describe your changes in the PR
4. Link related issues
5. Wait for review

## Project Structure

```
├── main.py                    # Entry point
├── config.json                # Configuration
├── requirements.txt           # Dependencies
│
├── Core Modules:
│   ├── file_scanner.py
│   ├── deduplication_engine.py
│   ├── deletion_manager.py
│   └── suggestion_engine.py
│
├── UI Components:
│   ├── ui_main_window.py
│   ├── ui_results_view.py
│   └── ui_dialogs.py
│
└── Utilities:
    ├── utils.py
    └── logger.py
```

## Areas for Contribution

- 🎯 **Video/Audio Support**: Extend to other file types
- 🚀 **Performance**: Optimize hashing and scanning
- 🎨 **UI/UX**: Improve interface design
- 📝 **Documentation**: Tutorials and guides
- 🧪 **Testing**: Expand test coverage
- 🌍 **Internationalization**: Multi-language support

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping improve Duplicate File Finder! 🙏
