# Contributing to Transmus

Thank you for considering contributing to Transmus! This document outlines the guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something useful.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/raj-mohan/transmus/issues)
2. If not, create a new issue using the bug report template
3. Include:
   - Python version and OS
   - Steps to reproduce
   - Expected vs actual behavior
   - Full error output (with sensitive info redacted)

### Suggesting Features

1. Open a feature request issue using the template
2. Describe the feature and why it would be useful
3. Include any relevant examples or use cases

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes following the coding standards
4. Add or update tests as needed
5. Run the test suite: `pytest`
6. Run the linter: `ruff check .`
7. Commit with clear messages
8. Push and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/transmus.git
cd transmus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install dev dependencies
pip install -r requirements.txt
```

## Coding Standards

- Python 3.10+ type hints required for all functions
- Follow PEP 8 (enforced by ruff)
- Docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use descriptive variable names

## Testing

- Write tests for all new functionality
- Use pytest fixtures for test data
- Mock external API calls in unit tests
- Run `pytest --cov` to check coverage

## Project Structure

```
transmus/
├── cli.py              # CLI commands
├── config.py           # Configuration management
├── models.py           # Data models
├── matcher.py          # Track matching engine
├── transfer.py         # Transfer orchestration
├── auth/
│   ├── youtube_auth.py
│   └── spotify_auth.py
└── services/
    ├── youtube_music.py
    └── spotify_service.py