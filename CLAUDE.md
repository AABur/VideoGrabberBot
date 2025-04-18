# VideoGrabberBot Development Guidelines

## Commands
- Run bot: `uv run python run.py`
- Run all tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_file.py::test_function_name`
- Run tests with coverage: `uv run pytest --cov=bot --cov-report=term-missing`
- Type check: `uv run mypy .`
- Lint code: `uv run ruff check .`
- Format code: `uv run ruff format .`

## Code Style
- **Imports**: Standard lib → Third-party → Local (alphabetical within groups)
- **Types**: Use type annotations for all functions and variables
- **Naming**: snake_case for variables/functions, UPPER_CASE for constants
- **Error handling**: Use try/except with specific exceptions, log errors with loguru
- **Docstrings**: Google style docstrings for all modules, classes, and functions
- **Async**: Use async/await for I/O bound operations (DB, network)
- **Formatting**: 4 spaces indentation, max 79 char line length, one empty line at end of file
- **File Structure**: Each file should have one and only one blank line at the end
- **Logging**: Use loguru with appropriate levels (debug, info, error)
- **Testing**: pytest with pytest-asyncio for async tests, pytest-mock for mocking
- **Language**: Always use English for ALL code, comments, and docstrings (even if communication may be in Russian)

## Environment
- Python version management: Uses `uv` for Python version and dependency management
- Python version: >=3.13 (as specified in pyproject.toml)
- Dependencies are managed with `uv` and defined in pyproject.toml
- Use `uv pip install -e .` for development install
- Use `uv pip install -e ".[dev]"` to install development dependencies

## Documentation References
- aiogram: https://docs.aiogram.dev/
- yt-dlp: 
  - README: https://github.com/yt-dlp/yt-dlp/blob/master/README.md
  - Wiki: https://github.com/yt-dlp/yt-dlp/wiki
- aiosqlite: https://aiosqlite.omnilib.dev/en/latest/
- loguru: https://loguru.readthedocs.io/

Remember to run `uv run ruff check .` and `uv run ruff format .` after making changes to ensure code quality. Always run the tests with `uv run pytest` to verify code functionality.