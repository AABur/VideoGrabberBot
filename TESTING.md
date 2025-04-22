# VideoGrabberBot Testing Documentation

This document provides an overview of the testing approach and guidelines for VideoGrabberBot.

## Test Organization

The tests are organized in the following structure:

- `tests/` - Root directory for all tests
  - `conftest.py` - Global pytest fixtures and configuration
  - `test_*.py` - Unit tests for individual modules
  - `integration/` - Integration tests
    - `conftest.py` - Integration-specific fixtures
    - `test_*.py` - Integration test modules

## Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation. They're located in the `tests/` directory and named according to the module they test (e.g., `test_formats.py` tests `bot/services/formats.py`).

### Integration Tests

Integration tests verify that multiple components work correctly together. They're located in the `tests/integration/` directory and focus on specific workflows like command interactions and download processing.

## Fixtures

The project uses fixtures for test isolation and setup. Key fixtures include:

### Global Fixtures (in `tests/conftest.py`)

- `reset_storage` - Resets URL storage between tests (autouse)
- `mock_video_formats`, `mock_audio_formats` - Provide consistent test format data
- `clear_format_cache` - Clears function caches between tests (autouse)
- `mock_config` - Provides controlled environment with mocked configuration
- `mock_telegram_user`, `mock_telegram_message` - Mock Telegram entities
- `authorized_user_mock`, `unauthorized_user_mock` - Mock authorization status
- `isolated_url_storage` - Completely isolates URL storage for specific tests
- `temp_directory` - Creates temporary directory for file operations
- `reset_modules` - Resets imported modules to their initial state

### Integration Fixtures (in `tests/integration/conftest.py`)

- `temp_db` - Creates temporary database for testing
- `mock_bot`, `mock_dispatcher` - Mock Telegram bot and dispatcher
- `authorized_user`, `unauthorized_user` - Create mock users with different permissions
- `mock_message`, `mock_callback_query` - Create mock Telegram messages and callbacks
- `reset_queue` - Resets download queue between tests
- `integration_setup` - Comprehensive setup for integration tests

## Test Isolation

To ensure test isolation:

1. Fixtures reset shared state between tests (storage, queues, caches)
2. Tests use isolated environments (temp directories, in-memory DBs)
3. Tests are designed to be independent of execution order
4. Mocks are used to prevent external dependencies

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Tests for a Specific Module

```bash
uv run pytest tests/test_formats.py
```

### Run Tests with Coverage

```bash
uv run pytest --cov=bot --cov-report=term-missing
```

## Test Guidelines

When writing new tests:

1. **Isolation**: Each test should be independent and not affect other tests
2. **Fixtures**: Use fixtures for setup and teardown, avoid state in test classes
3. **Mocking**: Mock external dependencies and use `AsyncMock` for async functions
4. **Descriptive Names**: Use descriptive test names that explain what is being tested
5. **Small Tests**: Keep tests small and focused on one aspect of functionality
6. **Readability**: Follow the Arrange-Act-Assert pattern for clarity

## Recent Improvements

The testing infrastructure was recently improved with:

1. Better test isolation for modules:
   - Added dedicated fixtures for resetting global state
   - Improved cache clearing for functions with `@lru_cache`
   - Ensured URL storage is reset between tests

2. Enhanced test patterns:
   - Split complex tests into smaller, focused tests
   - Added tests for edge cases and error conditions
   - Made tests more predictable regardless of execution order

3. Added more comprehensive tests:
   - Expanded coverage for format selection and URL processing
   - Added tests for large numbers of URLs and storage edge cases
   - Improved error handling tests

## Common Issues and Solutions

- **Test Order Dependencies**: If tests fail in some orders but pass in others, check for shared state not being reset properly.
- **Cache Issues**: Remember to clear caches for functions with `@lru_cache` before and after tests.
- **Async Testing**: Use `@pytest.mark.asyncio` for async tests and `AsyncMock` for mocking async functions.
- **Integration Test Failures**: These often indicate real issues with component interaction rather than test problems.

## Future Improvements

Planned improvements to the testing infrastructure:

1. Increase test coverage for error handling scenarios
2. Add performance tests for download queue with many tasks
3. Improve documentation of fixtures and testing patterns
4. Add more comprehensive API mocking for external services