# VideoGrabberBot Refactoring Plan

## Этап 1. Improve Code Organization

Подэтап 1.1. Add development rules to CLAUDE.md
- [x] Add rule about not changing code and tests simultaneously
- [x] Add rule about test coverage requirements (85%+)
- [x] Add rule about test-first development workflow

Подэтап 1.2. Optimize video format handling (formats.py)
- [x] Improve type hints with TypedDict
- [x] Refactor get_format_options() for better performance
- [x] Simplify get_available_formats() function
- [x] Run tests to verify changes

Подэтап 1.3. Fix downloader service linting issues
- [x] Fix 5 of 8 linting errors (WPS420, WPS110, WPS335, WPS458, WPS505)
- [x] Fix test imports after code changes (separate commit required)
- [x] Refactor download_youtube_video function to reduce complexity:
  - [x] WPS210: Reduce local variables by extracting helper functions
  - [x] WPS213: Reduce expressions by breaking down complex logic
  - [x] WPS229: Shorten try block by extracting main process logic
- [x] Break function into smaller, focused helper functions:
  - [x] _create_or_update_status_message() - handle status messages
  - [x] _create_ydl_options() - create yt-dlp configuration
  - [x] _download_video_file() - handle actual file download
  - [x] _send_downloaded_file() - send file to user
  - [x] _execute_download_process() - main process orchestration
  - [x] _handle_download_error() - error handling and notifications
- [x] Maintain all existing functionality and tests (6/6 tests passing)

Подэтап 1.4. Fix queue service linting issues (queue.py) 
- [x] Fix WPS338: Correct method ordering (public before private)
- [x] Fix WPS231: Reduce cognitive complexity in _process_queue
- [x] Fix WPS237: Simplify complex f-strings  
- [x] Fix WPS220: Reduce deep nesting by extracting helper methods
- [x] All tests passing after refactoring

Подэтап 1.5. Fix handlers linting issues (commands.py, download.py)
- [x] Fix WPS110: Rename 'result' variable to more specific name
- [x] Fix WPS237: Simplify complex f-strings by extracting variables
- [x] Fix WPS504: Remove negated conditions where possible 
- [x] Fix WPS347: Handle vague import (F) with noqa comment
- [x] Fix WPS210: Reduce local variables by extracting helper functions
- [x] Fix WPS213: Reduce expressions by breaking down complex functions
- [x] Fix WPS336: Replace string concatenation with f-strings
- [x] Fix WPS202: Reduce module members by combining helper functions
- [x] All 24 handler tests passing after refactoring

Подэтап 1.6. Fix scripts and run files linting issues
- [x] Fix WPS453: Make run.py executable to match shebang
- [x] Fix WPS221: Reduce Jones Complexity in scripts/run_bot.py by simplifying path logic
- [x] Fix WPS421: Replace print calls with logger calls in scripts/test_init.py
- [x] Fix WPS421: Replace print calls with logger calls in scripts/test_run.py  
- [x] Fix WPS473: Reduce empty lines in function definition
- [x] All unit tests passing after script changes (91/91 tests)

## 🎉 ЭТАП 1 ЗАВЕРШЕН: Code Quality Improvements Complete!

**Summary of completed work:**
- ✅ All linting errors fixed across entire codebase (0 WPS errors remaining)
- ✅ Comprehensive refactoring of all modules with complex functions broken down
- ✅ All 91 unit tests passing, functionality preserved
- ✅ Code maintainability and readability significantly improved
- ✅ Consistent coding standards enforced throughout project

Подэтап 1.7. Future optimization opportunities (storage.py)
- [ ] Implement time-based expiration for temporary data
- [ ] Improve error handling and edge cases
- [ ] Add automatic cleanup mechanism
- [ ] Ensure backward compatibility with existing code
- [ ] Verify with tests

## Этап 2. Handle Dependency Management

Подэтап 2.1. Resolve circular imports
- [ ] Audit all import statements in the project
- [ ] Identify modules with circular dependencies
- [ ] Refactor to use dependency injection where appropriate
- [ ] Consider adding a service locator pattern

Подэтап 2.2. Improve module initialization
- [ ] Evaluate current initialization sequence
- [ ] Restructure initialization to avoid side effects
- [ ] Add proper error handling during initialization

## Этап 3. Enhance Error Handling

Подэтап 3.1. Add comprehensive error handling
- [ ] Create custom exception classes
- [ ] Implement contextual error messages
- [ ] Add retry mechanism for network operations
- [ ] Improve user-facing error messages

Подэтап 3.2. Enhance logging
- [ ] Review current logging levels and messages
- [ ] Add structured logging for better analysis
- [ ] Implement log rotation and management

## Этап 4. Performance Optimizations

Подэтап 4.1. Optimize download queue
- [ ] Implement more efficient task scheduling
- [ ] Add priority queue support
- [ ] Implement concurrency limits
- [ ] Add download progress tracking

Подэтап 4.2. Optimize database operations
- [ ] Review and optimize database queries
- [ ] Implement connection pooling
- [ ] Add caching for frequently used data

## Этап 5. Documentation

Подэтап 5.1. Update project documentation
- [ ] Review and update README.md
- [ ] Add detailed API documentation
- [ ] Create user guide for bot commands
- [ ] Document architecture and design decisions