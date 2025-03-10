# A13X-DEPINJ Project Guide

## Build & Test Commands
- Install dev: `pip install -e ".[dev]"`
- Format: `black src tests examples`
- Sort imports: `isort src tests examples`
- Type check: `mypy src tests examples`
- Check formatting: `black --check src tests examples`
- Run all tests: `pytest`
- Run specific test: `pytest tests/test_file.py::test_function`
- Coverage: `pytest --cov=a13x_depinj`
- HTML coverage: `pytest --cov=a13x_depinj --cov-report=html`

## Code Style Guidelines
- Imports: standard lib first, then project imports
- Naming: snake_case for variables/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- Types: Always use type hints; leverage TypeVar, Optional, Union, etc.
- Error handling: Custom exceptions inherit from DepinjError, preserve context with "from e"
- Docstrings: Include Args, Returns, Raises sections
- Formatting: 4-space indentation, ~88-120 char line length
- Project structure: Clear separation of concerns between modules