# Claude Coding Guidelines

## Build & Testing Commands
- Run all tests: `python -m pytest tests/`
- Run specific test file: `python -m pytest tests/test_config.py`
- Run specific test: `python -m pytest tests/test_config.py::test_config_default_initialization`
- Run data validator: `python validate_data.py`
- Run main processor: `python seatek_processor_new.py`
- Code linting: `flake8 src/ tests/`
- Type checking: `mypy src/`

## Code Style Guidelines
- **Formatting**: Follow PEP 8; line length of 88 characters (Black-compatible)
- **Imports**: Group as standard library, third-party, local imports; sort alphabetically
- **Types**: Use type hints for all function parameters and return values
- **Naming**: Classes use PascalCase; functions/variables use snake_case; constants use UPPER_SNAKE_CASE
- **Documentation**: Google-style docstrings with Args/Returns sections
- **Error Handling**: Use specific exception types; log errors with context; provide meaningful error messages
- **Architecture**: Follow dependency injection pattern; single responsibility principle
- **Testing**: Write unit tests for all components; mock external dependencies