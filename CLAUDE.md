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

## Claude Interaction Guidelines

This section contains rules and guidelines for working with Claude on this project. These rules should be followed during all interactions related to VideoGrabberBot development.

### Communication Rules

1. **Language**: 
   - Claude should communicate with developers in Russian in the chat
   - All project artifacts (code, comments, documentation, commit messages) must be in English

2. **Message Tags**:
   - Use special tags in messages for Claude to recognize specific instructions:
     - `#правило: [содержание правила]` — for adding a new rule
     - `#напоминание: [содержание]` — for important reminders

### Project-Specific Rules

1. **Version Control**: 
   - All changes to project files must be saved to git after developer confirmation
   - Do not commit changes automatically without explicit approval

2. **Testing**:
   - After changing code, always run corresponding tests

3. **Code Quality**:
   - Before committing to git, always run formatting and linter

4. **Rule Management**:
   - All rules must be added to CLAUDE.md
   - Before adding a new rule, check for duplicates or contradictions

### Code Generation Rules

1. **[Add future code generation rules here]**

### Documentation Rules

1. **[Add future documentation rules here]**