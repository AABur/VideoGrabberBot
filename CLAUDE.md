# VideoGrabberBot Development Guidelines

## Commands
- Run bot: `uv run python run.py`
- Run all tests: `uv run pytest`
- Run single test: `uv run pytest tests/test_file.py::test_function_name`
- Run tests with coverage: `uv run pytest --cov=bot --cov-report=term-missing`
- Type check: `uv run mypy .`
- Lint code with Ruff: `uv run ruff check .`
- Lint code with wemake-python-styleguide: `uv run flake8 . --select=WPS`
- Format code: `uv run ruff format .`
- Complete linting: `uv run ruff check && uv run ruff format && uv run flake8 . --select=WPS`
- Using Makefile: `make lint-all` (runs all linting commands in sequence)

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

## Linting
The project uses two linting tools that complement each other:

1. **Ruff**: Fast Python linter for basic checks and formatting
   - Configuration: In pyproject.toml under [tool.ruff]
   - Command: `uv run ruff check .`
   - Format: `uv run ruff format .`

2. **wemake-python-styleguide**: Strict linter for enforcing best practices
   - Configuration: In .flake8 file
   - Command: `uv run flake8 . --select=WPS` (WPS only checks)
   - No automatic fixes - requires manual corrections

**Recommended workflow**:
1. Run `make lint-all` or `uv run ruff check && uv run ruff format && uv run flake8 . --select=WPS`
2. Fix any issues reported by both linters
3. Run tests to verify functionality

The linters work together - Ruff handles most formatting and basic linting, while wemake-python-styleguide adds additional stricter checks.

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
- wemake-python-styleguide: https://wemake-python-styleguide.readthedocs.io/
- ruff: https://docs.astral.sh/ruff/

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
   - NEVER change code and tests simultaneously
   - When adding tests for existing code, do not modify the code itself
   - When writing new code, run existing tests and create new tests afterward
   - When refactoring code, always run existing tests to verify functionality
   - Maintain minimum test coverage of 85%

3. **Code Quality**:
   - Before committing to git, always run formatting and both linters (ruff and flake8)
   - Use `make lint-all` to run all linting tools in the correct sequence

4. **Rule Management**:
   - All rules must be added to CLAUDE.md
   - Before adding a new rule, check for duplicates or contradictions

5. **Development Workflow**:
   - **Creating Tests**: When creating tests for existing code, never modify the code itself
   - **New Feature Development**: When implementing new functionality, first write the code, then run existing tests, fix issues if needed, and finally create tests for the new code
   - **Code Refactoring**: When refactoring existing code, always run tests after changes to ensure the functionality remains intact
   - **Task-Driven Testing**: For complex testing tasks, first create a TODO_*.md file with a step-by-step plan, then follow this plan working on each step sequentially

### Code Generation Rules

1. **Code Implementation Approval**: Never start working with code until explicit approval from the developer. Do not write code directly in chat without a specific request.

2. **[Add future code generation rules here]**

### Documentation Rules

1. **[Add future documentation rules here]**