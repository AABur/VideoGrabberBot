# Python Project Development Guidelines

## Environment Setup
- Python version: >=3.11 (specific version specified in pyproject.toml)
- Python version management: Uses `uv` for Python version and dependency management ([Python installation documentation](https://docs.astral.sh/uv/guides/install-python/))
- Dependencies are managed with `uv` and defined in pyproject.toml ([dependency management documentation](https://docs.astral.sh/uv/guides/projects/#managing-dependencies))
- Development installation: `uv pip install -e .`
- Install development dependencies: `uv pip install -e ".[dev]"`

## Commands
- Run all unit tests: `uv run pytest`
- Run single unit test: `uv run pytest tests/test_file.py`
- Run tests with coverage: `uv run pytest --cov=src --cov-report=term-missing`
- Type check: `uv run mypy .`
- Lint code with Ruff: `uv run ruff check .`
- Format code: `uv run ruff format .`
- Lint code with wemake-python-styleguide: `uv run flake8 . --select=WPS`
- Complete linting: `uv run ruff check && uv run ruff format && uv run flake8 . --select=WPS`

## Development Workflow
- **Creating Tests**: When creating tests for existing code, never modify the code itself
- **New Feature Development**: First write the code, then run existing tests, fix issues if needed, and finally create tests for the new code
- **Code Refactoring**: Always run tests after changes to ensure the functionality remains intact
- **Task-Driven Development**: For complex tasks, first create a TODO_*.md file with a step-by-step plan, then follow this plan working on each step sequentially
- Run tests and linter after making significant changes to verify functionality
- After important functionality is added, update README.md accordingly
- Testing strategy and guidelines are detailed in TESTING.md

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
- **Language**: Always use English for ALL code, comments, and docstrings

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
1. Run `uv run ruff check && uv run ruff format && uv run flake8 . --select=WPS`
2. Fix any issues reported by both linters
3. Run tests to verify functionality

The linters work together - Ruff handles most formatting and basic linting, while wemake-python-styleguide adds additional stricter checks.

## Testing Guidelines
- **Testing Framework**: pytest with pytest-asyncio for async tests, pytest-mock for mocking
- NEVER change code and tests simultaneously
- When adding tests for existing code, do not modify the code itself
- When writing new code, run existing tests and create new tests afterward
- When refactoring code, always run existing tests to verify functionality
- Maintain minimum test coverage of 85%
- All testing related documentation and guidelines are maintained in TESTING.md

## Documentation
- Project documentation, installation instructions, and usage examples are maintained in README.md
- API documentation is generated from docstrings
- For large projects, additional documentation can be placed in the `docs/` directory
- Use Markdown for all documentation files
- Documentation should be kept up to date as the codebase evolves

## Claude Interaction Guidelines

This section contains rules and guidelines for working with Claude on this project. These rules should be followed during all interactions related to project development.

### Communication Rules

1. **Language**:
   - All project artifacts (code, comments, documentation, commit messages) must be in English

2. **Message Tags**:
   - Use special tags in messages for Claude to recognize specific instructions:
     - `#rule: [rule content]` — for adding a new rule
     - `#reminder: [content]` — for important reminders

### Project-Specific Rules

1. **Version Control**:
   - All changes to project files must be saved to git after developer confirmation
   - Do not commit changes automatically without explicit approval
   - Don't add "Generated with Claude Code" or "Co-Authored-By: Claude" to commit messages
   - Do not include "Test plan" sections in PR descriptions

2. **Code Generation Rules**:
   - Never start working with code until explicit approval from the developer
   - Do not write code directly in chat without a specific request
   - Do not add comments that describe changes, progress, or historical modifications
   - Avoid comments like "new function," "added test," "now we changed this," or "previously used X, now using Y"
   - Comments should only describe the current state and purpose of the code, not its history or evolution
   - If unable to fix a linting error after 3 attempts, stop and discuss the problem with the developer
   - If fixing code requires modifying tests, stop and explain the situation to the developer

3. **Rule Management**:
   - All rules must be added to CLAUDE.md
   - Before adding a new rule, check for duplicates or contradictions