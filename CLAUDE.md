# Claude Coding Guidelines

## Build & Testing Commands

- Run all tests: `python3 -m pytest tests/`
- Run specific test file: `python3 -m pytest tests/test_config.py`
- Run specific test: `python3 -m pytest tests/test_config.py::test_config_default_initialization`
- Run data validator: `python3 validate_data.py`
- Run main processor: `MPLBACKEND=Agg python3 seatek_processor.py`
- Code linting: `flake8 src/ tests/`
- Type checking: `mypy src/`
- CI mirrors these commands on pull requests and pushes to `main` (see `.github/workflows/python-tests.yml`)

Use `python3` (not `python`) — `python` is often missing from PATH in Cloud/CI environments.

## Code Style Guidelines

- **Formatting**: Follow PEP 8; line length of 88 characters (Black-compatible)
- **Imports**: Group as standard library, third-party, local imports; sort alphabetically
- **Types**: Use type hints for all function parameters and return values
- **Naming**: Classes use PascalCase; functions/variables use snake_case; constants use UPPER_SNAKE_CASE
- **Documentation**: Google-style docstrings with Args/Returns sections
- **Error Handling**: Use specific exception types; log errors with context; provide meaningful error messages
- **Architecture**: Follow dependency injection pattern; single responsibility principle
- **Testing**: Write unit tests for all components; mock external dependencies
