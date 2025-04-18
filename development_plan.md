# Development Plan for VideoGrabberBot

## Disclaimer

**This project is a personal educational initiative created solely for learning purposes and is not intended for commercial use.** The development plan outlined below serves as a learning framework for practicing Python programming, async development, and Telegram bot implementation.

## Development Phases

### 1. Initial Setup and Bot Registration

- **Bot Registration in Telegram:**
  - Create a bot via BotFather, obtain the TELEGRAM_TOKEN and save it in the .env file.
- **Repository and Project Structure Setup:**
  - Create a Git repository with the necessary directory structure (see project architecture).
  - Configure .gitignore file to exclude virtual environment, .env file, and temporary files.
- **Dependency Management:**
  - Initialize the project using uv and create pyproject.toml with dependencies (aiogram, yt-dlp, mypy, pytest, ruff, loguru, etc.).

### 2. Configuration, Database, and Logging Setup

- **Configuration (config.py):**
  - Implement loading of variables from .env (e.g., TELEGRAM_TOKEN).
  - Set up paths for temporary files and connection to SQLite database for user storage.
- **Database (db.py module):**
  - Create tables for authorized users and invitations.
  - Implement functions for adding/removing and checking access.
- **Logging (logging.py module with Loguru):**
  - Configure Loguru with logging levels (DEBUG, INFO, WARNING, ERROR).
  - Integrate logging into all main modules.
  - Implement function for sending error notifications to the administrator via Telegram.

*Note: Unit tests (pytest) will be created in parallel with each module to verify correct operation.*

### 3. Telegram Bot Initialization and Basic Handlers

- **aiogram Initialization:**
  - Create Bot and Dispatcher objects in the telegram_api/client.py module.
  - Connect basic command handlers.
- **Basic Commands (handlers/commands.py):**
  - /start, /help – display help information.
  - /invite – generate a unique invitation link.
  - /adduser – admin command for adding users by their Telegram User Name.
- **Authorization Check:**
  - Implement access verification through SQLite database in each handler.
- **Integration Tests:**
  - Create tests to verify the correct operation of basic commands and authorization.
- **Functionality Testing:**
  - Ability to run the bot in test mode to check command operation in a real chat.

### 4. Download Functionality Implementation (Basic Version)

- **Download Function:**
  - In services/downloader.py, implement a basic function for downloading content from YouTube (using yt-dlp) without format selection.
  - Handle file transmission through Telegram (as a document, considering support for files up to 2 GB).
- **Parallel Testing:**
  - Write unit tests for the download function (using mocks for yt-dlp).
  - Log the start, completion, and possible errors of downloads.

### 5. Format Selection Implementation

- **Format List Formation (services/formats.py):**
  - Implement logic for generating a list of available formats:
    - Video: SD (480p), HD (720p), Full HD (1080p), Original.
    - Audio: MP3 (320 kbps).
- **Format Selection Handler (handlers/download.py):**
  - After receiving a link, request a list of formats and send an InlineKeyboard with options.
  - Process the callback query related to format selection and queue the download task.
- **Testing:**
  - Create tests to verify the correct formation of the format list and InlineKeyboard operation.
  - Log user selection and task queuing.

### 6. Download Task Queue Implementation

- **Task Queue:**
  - Implement a queue mechanism for sequential request execution.
  - When a new request arrives, if the bot is busy, notify the user about queuing.
- **Queue Logging:**
  - Log task addition to the queue, start of processing, and completion.
- **Tests:**
  - Write tests simulating sequential request execution to ensure the queue works correctly.

### 7. YouTube Integration Optimization

- **Download Logic Optimization:**
  - In handlers/download.py, optimize processing of YouTube links.
  - In services/downloader.py, improve support for downloading content from YouTube via yt-dlp.
- **Parallel Testing:**
  - Write additional tests for YouTube functionality.
  - Log all download actions.

### 8. Error Handling and Administrator Notification

- **Exception Handling:**
  - Add try/except with error logging in all critical blocks (download, format selection, database operations).
  - Use Loguru for detailed error recording (including call stack).
- **Administrator Notification:**
  - Send notification messages to the administrator via aiogram when critical errors occur.
- **Error Testing:**
  - Create tests simulating errors (e.g., invalid URL, yt-dlp failure) and verify that the administrator receives notifications.

### 9. Integration Testing and New Functionality Verification

- **Integration Tests:**
  - Create an environment for integration testing, allowing the bot to be run and sequential operation of all modules to be verified.
  - Test complete scenarios – from receiving a command to sending a file, including queue processing.
- **Real-time Verification:**
  - Provide the ability to quickly launch a test version of the bot for manual verification of new functionality in Telegram.
  - Use CI/CD (if required) for automated test execution with each code change.

### 10. Documentation and Deployment

- **Documentation:**
  - Update README.md with detailed instructions for installation, configuration, and project launch.
  - Describe the deployment process directly from the GitHub repository (e.g., through automated pull and script execution).
- **Final Integration Testing:**
  - Conduct comprehensive testing of all functions in the test environment.
  - Prepare the project for deployment and ensure the ability to quickly update code via GitHub.