# Contributing to a13x-depinj

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/a13x-depinj.git
cd a13x-depinj
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Code Style

We use:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

Format code before committing:
```bash
black src tests examples
isort src tests examples
```

Run type checking:
```bash
mypy src tests examples
```

## Testing

Run tests with pytest:
```bash
pytest

# With coverage
pytest --cov=a13x_depinj

# Generate coverage report
pytest --cov=a13x_depinj --cov-report=html
```

## Pull Request Process

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and follow these practices:
   - Write tests for new features
   - Update documentation
   - Add type hints
   - Follow PEP 8 style guide
   - Include docstrings for public APIs

3. Run test suite:
```bash
pytest
mypy src tests examples
black --check src tests examples
```

4. Update version if needed:
   - pyproject.toml
   - setup.cfg
   - __init__.py

5. Push changes and create PR:
```bash
git push origin feature/your-feature-name
```

## Commit Messages

Follow conventional commits:
```
feat: add new feature
fix: bug fix
docs: documentation updates
test: add or update tests
refactor: code refactoring
chore: maintenance tasks
```

## Documentation

- Update README.md for API changes
- Add docstrings for new functions/classes
- Update example code if needed
- Ensure docs build without warnings

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release PR
4. After merge, tag release:
```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Code Review Guidelines

- Changes should be focused and atomic
- Include tests and documentation
- Maintain backward compatibility
- Follow project style and conventions
- Add comments for complex logic

## Support

- Create issue for bugs/features
- Join discussions in Issues
- Tag maintainers for urgent matters
- Follow Code of Conduct