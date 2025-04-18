# Technical Specification: VideoGrabberBot

## Disclaimer

**This project is a personal educational initiative created solely for learning purposes and is not intended for commercial use.** The specifications below serve as technical requirements for an educational programming exercise, aimed at practicing Python development skills, asynchronous programming, and Telegram bot development.

## Project Overview

VideoGrabberBot is a Telegram bot designed to download videos and audio from YouTube based on provided links. The bot offers users a choice of download formats: for video - SD (480p), HD (720p), Full HD (1080p), and Original (maximum available quality, including 2K/4K); for audio - MP3 (320 kbps). The downloaded file is sent directly to the chat. Access to the bot is granted either through a unique invitation link or by administrator approval (based on Telegram User Name). User information is stored in an SQLite database. In case of errors, the bot notifies the administrator. Deployment is done directly from the GitHub repository without using Docker.

## Functional Requirements

### Source Support
- **YouTube:** Use the yt-dlp library for content extraction and downloading. Possibility of further expansion to support other platforms through yt-dlp.

### Format Selection Before Download
- **Video Formats:**
  - SD (480p): for weak internet connections, traffic savings.
  - HD (720p): good balance of quality and file size.
  - Full HD (1080p): high quality for modern devices.
  - Original: maximum available quality (including 2K/4K).
- **Audio Format:**
  - MP3 (320 kbps): high sound quality, universal format.
- After sending a link, the bot extracts available options and forms a message with buttons (InlineKeyboard) for selecting a specific format.

### Limited Access
- Access to the bot is implemented either through a unique invitation link or through a mechanism for adding users by the administrator using their Telegram User Name.
- Information about users with access is stored in an SQLite database.
- When an unauthorized user contacts the bot, it should notify them of the impossibility of using the service.

### Logging and Error Handling
- Use Loguru for logging. Loguru provides modern formatting, asynchronous support, and low overhead.
- All key events (startup, receiving requests, start and end of downloads) are logged.
- In case of errors - in addition to user notifications - the bot sends a notification message to the administrator (e.g., with error details and stack trace).

### Task Queue
- For a limited number of users and infrequent simultaneous use, implement a task queue to ensure sequential execution of requests without conflicts.
- When a new request arrives while the bot is busy, the user may receive a notification about the request being queued.

### Working with Large Files
- The project should support processing files up to 2 GB.
- For sending such files, use the document transmission method via Telegram (since the media message format has limitations).
- If necessary, implement alternative approaches (e.g., sending a link to the file after saving it on the server) to enable working with large files.

## Non-Functional Requirements and Development Tools

### Dependency and Environment Management
- Use uv for dependency management and creating an isolated environment. Project configuration is done in the pyproject.toml file with all dependencies specified (e.g., aiogram, yt-dlp, mypy, pytest, ruff).

### Static Typing
- Code is equipped with type annotations (at least in function signatures) and checked with mypy.

### Testing
- pytest is used for unit and integration testing.
- Main modules are tested: download functions, format selection, authorization check, and request queue processing.

### Linter and Formatter
- Ruff is used for code style checking and automatic formatting.

### Version Control
- The project is stored in a Git repository with a well-thought-out commit history. The .gitignore file excludes virtual environment, secret files (e.g., .env), and other temporary files.

### Configuration
- Secret data (e.g., TELEGRAM_TOKEN) is stored in a .env file, which is not added to the repository.
- Additional settings (e.g., path to SQLite database for storing users) are also configured through environment variables.

### Logging
- Use Loguru for logging configuration. All logs, including errors, are formatted in a modern way. In case of errors, in addition to local logging, the bot notifies the administrator.

### Telegram Library Choice
- Use aiogram as the only library for interacting with the Telegram Bot API, providing asynchronicity and modern API.

### Deployment
- Deployment is done directly from the GitHub repository. The project should include instructions for deployment without using Docker.

## Project Architecture

### General Approach

The project is structured as a modular Python package, with clear separation of functionality between bot components (message handling, download business logic, utilities, database and logging work). The following directory structure is proposed:

```
VideoGrabberBot/                # Root project directory
├── bot/                       # Main bot package
│   ├── __init__.py
│   ├── main.py                # Entry point: aiogram initialization, bot launch
│   ├── config.py              # Loading configuration from .env, setting up paths (e.g., database)
│   ├── handlers/              # Package with command and message handlers
│   │   ├── __init__.py
│   │   ├── commands.py        # Command handlers (/start, /help, /invite, /adduser)
│   │   └── download.py        # Link processing, format selection (InlineKeyboard) and callback query handling
│   ├── services/              # Business logic for working with external libraries
│   │   ├── __init__.py
│   │   ├── downloader.py      # Functions for interacting with yt-dlp: getting formats, downloading files
│   │   └── formats.py         # Logic for forming a list of available formats (SD, HD, Full HD, Original for video and MP3 for audio)
│   ├── utils/                 # Helper utilities
│   │   ├── __init__.py
│   │   ├── logging.py         # Logging configuration through Loguru
│   │   └── db.py              # Module for working with SQLite database (storing authorized users, invitations)
│   └── telegram_api/          # Abstraction over aiogram (initialization of Bot, Dispatcher)
│       ├── __init__.py
│       └── client.py          # Initialization of Bot and Dispatcher objects
├── tests/                     # Tests (pytest)
│   ├── __init__.py
│   ├── test_downloader.py     # Tests for download functions and format list formation
│   └── test_handlers.py       # Tests for handlers (authorization check, task queue)
├── pyproject.toml             # Project configuration file (uv, Ruff, mypy, pytest)
├── .env                     # File with environment variables (TELEGRAM_TOKEN, database settings, etc.)
├── README.md                # Project documentation, installation and deployment instructions from GitHub
└── .gitignore               # Ignoring virtual environment, .env, and other temporary files
```

### Main Components and Their Tasks

#### main.py:
- aiogram initialization: creating a Bot object (with token loaded from .env) and Dispatcher.
- Connecting command handlers and callback queries.
- Initializing download task queue.
- Launching the bot (long polling or webhook, depending on deployment).

#### Configuration (config.py):
- Loading secret variables (e.g., TELEGRAM_TOKEN) from the .env file.
- Reading settings for connecting to SQLite database (e.g., database file path).
- Other global settings (e.g., directory for temporary files).

#### Handlers (handlers/):
- commands.py:
  - Implementation of basic commands:
    - /start – welcome message, explanation of how the bot works.
    - /help – usage guide.
    - /invite – generation of a unique invitation link for access.
    - /adduser – admin command for adding users through Telegram User Name.
- download.py:
  - Processing messages containing links to videos/audio.
  - Extracting the platform from the URL (YouTube or Instagram).
  - Getting a list of available formats through service call.
  - Sending a message to the user with selection buttons (InlineKeyboard) for each option:
    - For video: SD (480p), HD (720p), Full HD (1080p), Original.
    - For audio: MP3 (320 kbps).
  - Processing callback request: after the user selects a specific format – queuing the download task.

#### Services (services/):
- downloader.py:
  - Working with the yt-dlp library:
    - Function for getting information about available formats (with filtering options according to specification).
    - Function for downloading a file with a specified format, with options specified (e.g., format parameter).
    - Error handling during downloads: catching exceptions, logging the error, and notifying the administrator.
- formats.py:
  - Logic for forming a user-friendly list with format options, including human descriptions for each option.

#### Utilities (utils/):
- logging.py:
  - Configuring Loguru for logging: defining format, log levels, output to file and console.
  - Function for sending error notifications to the administrator (through a separate message in Telegram).
- db.py:
  - Functions for working with SQLite: creating a database, tables for storing users and invitations, adding/removing users, querying the database.
  - Providing access to data about authorized users, which allows checking if a user has the right to use the bot.

#### Telegram API Interaction (telegram_api/client.py):
- Abstracting and initializing aiogram objects (Bot and Dispatcher).
- Possible encapsulation of update handling and message sending logic.