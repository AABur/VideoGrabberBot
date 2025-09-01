# VideoGrabberBot: Technical Specification

This specification describes the architecture and functionality of VideoGrabberBot, a Telegram bot for downloading videos and audio from YouTube with format selection options.

## Overview

VideoGrabberBot allows users to download videos and audio from YouTube by sending links to the bot. It offers multiple format options (SD, HD, Full HD, Original for video; MP3 for audio) and delivers the files directly in the Telegram chat. Access to the bot is restricted through an authorization system, and all operations are logged with comprehensive error handling.

## Functional Requirements

### 1. Media Source Support

- **YouTube Integration**:
  - Process standard YouTube URLs (youtube.com, youtu.be, m.youtube.com, youtube-nocookie.com)
  - Extract video information using yt-dlp
  - Support for both short and long videos (up to Telegram's file size limit of 2GB)

### 2. Format Selection System

- **Video Formats**:
  - SD (480p): `best[height<=480]` format parameter
  - HD (720p): `best[height<=720]` format parameter
  - Full HD (1080p): `best[height<=1080]` format parameter
  - Original: `best` format parameter (maximum available quality)

- **Audio Format**:
  - MP3 (320kbps): `bestaudio/best` format parameter

- **Selection Interface**:
  - Present format options via Telegram's InlineKeyboard
  - Allow user to select desired format with a single tap
  - Provide feedback on selected format during download

### 3. Access Control System

- **User Authorization Mechanisms**:
  - Admin-only access for initial setup (configurable via ADMIN_USER_ID)
  - Invitation link system for granting access to new users
  - Direct user addition by admin (using /adduser command)

- **Persistent User Storage**:
  - Store authorized users in SQLite database
  - Track invitation creation and usage

### 4. Download Queue Management

- **Asynchronous Processing**:
  - Queue system for handling multiple download requests
  - Sequential processing to prevent resource contention
  - Status updates for queued downloads

- **Task Tracking**:
  - Track current download status
  - Allow cancellation of queued downloads
  - Provide queue position updates

### 5. Error Handling & Notification

- **Comprehensive Error Management**:
  - Handle network failures, API changes, and invalid URLs
  - Provide clear error messages to users
  - Notify admin of critical failures

- **Logging System**:
  - Detailed logging of all operations
  - Error stack traces for debugging
  - Admin notifications for critical issues

## Technical Architecture

### Core Components

1. **Bot Framework Layer**:
   - Uses aiogram for Telegram Bot API interactions
   - Event-driven architecture with router system
   - Asynchronous message handling

2. **Handler Layer**:
   - Command handlers (`commands.py`)
   - Download URL processor (`download.py`)
   - Callback query processor for format selection

3. **Service Layer**:
   - Download service (`downloader.py`): Interface to yt-dlp
   - Format service (`formats.py`): Format option management
   - Queue service (`queue.py`): Download task queue
   - Storage service (`storage.py`): Temporary URL storage

4. **Data Layer**:
   - Database utilities (`db.py`)
   - SQLite storage for users and invites
   - Temporary file storage for downloads

5. **Utility Layer**:
   - Logging configuration
   - Error notification
   - Configuration management

### Component Interactions

```
User -> Telegram -> Bot Framework -> Handlers -> Services -> External APIs
                                                 |
                                                 v
                                              Database
```

1. User sends a YouTube URL to the bot via Telegram
2. Bot framework passes message to URL handler
3. Handler verifies user authorization via database
4. Handler displays format options via InlineKeyboard
5. User selects a format, triggering a callback
6. Handler adds download task to queue
7. Queue processor executes download via yt-dlp
8. Downloaded file is sent back to user via Telegram

## Database Schema

### Users Table

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,       -- Telegram user ID
    username TEXT,                -- Telegram username
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    added_by INTEGER,             -- ID of user who added this user
    is_active BOOLEAN DEFAULT TRUE
)
```

### Invites Table

```sql
CREATE TABLE IF NOT EXISTS invites (
    id TEXT PRIMARY KEY,          -- Unique invite code
    created_by INTEGER,           -- ID of user who created the invite
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_by INTEGER,              -- ID of user who used the invite
    used_at TIMESTAMP,            -- When the invite was used
    is_active BOOLEAN DEFAULT TRUE
)
```

### Settings Table

```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Implementation Details

### Download Process

1. **URL Validation**:
   - Verify URL is from supported platform (YouTube)
   - Check for valid video ID format

2. **Format Extraction**:
   - Parse available formats using yt-dlp
   - Filter and group formats based on resolution/quality
   - Present simplified options to user

3. **Download Execution**:
   - Create temporary directory for download
   - Configure yt-dlp with selected format parameter
   - Monitor download progress
   - Verify downloaded file integrity

4. **File Delivery**:
   - Send file as document via Telegram
   - Include metadata (title, source)
   - Clean up temporary files after sending

### Authentication Flow

1. **Initial Setup**:
   - Admin ID is set via environment variable
   - Admin has full access to all commands

2. **User Authorization**:
   - New users can join via invite links
   - Admin can directly add users with /adduser command
   - All user access is verified on each command

3. **Invite Generation**:
   - Admin or authorized user creates invite
   - Unique UUID is generated and stored in database
   - Invite link includes bot username and invite code
   - Invites can be used only once

## Environment Requirements

### Runtime Dependencies

- Python 3.11+
- aiogram 3.19.0+
- yt-dlp 2025.3.27+
- aiosqlite 0.21.0+
- loguru 0.7.3+
- python-dotenv 1.1.0+

### Development Dependencies

- mypy 1.15.0+
- pytest 8.3.5+
- pytest-asyncio 0.26.0+
- pytest-cov 5.0.0+
- pytest-mock 3.14.0+
- ruff 0.11.2+
- wemake-python-styleguide 1.1.0+

### Configuration

Required environment variables:
- `TELEGRAM_TOKEN`: Bot API token from BotFather
- `ADMIN_USER_ID`: Telegram user ID of the administrator

### File System Structure

```
data/                  # Data directory (created automatically)
├── bot.db             # SQLite database
└── temp/              # Temporary download directory
```

## Deployment Guidance

### Direct Deployment

1. Clone the repository
2. Install Python 3.11+
3. Install uv package manager
4. Set up environment with `uv venv` and activate
5. Install dependencies with `uv pip install -e .`
6. For development: `uv pip install -e ".[dev]"`
7. Create .env file with required configuration
8. Run with `uv run python run.py`

### Hosting Requirements

- Adequate disk space for temporary download files
- Internet connectivity with access to YouTube
- Sufficient bandwidth for file uploads to Telegram

## Security Considerations

- Bot token is stored in .env file (not in source control)
- Access control prevents unauthorized usage
- Temporary files are cleaned up after sending
- No sensitive user data is collected or stored
- Rate limiting is handled by Telegram's Bot API

### Authorization System
- All user interactions require authorization validation
- Authorization checks implemented in both URL processing and callback handling
- Prevents bypass attacks through direct callback manipulation

### Recent Security Improvements
- Fixed callback query authorization bypass vulnerability (January 2025)
- Added comprehensive security test coverage (43 security tests)
- Implemented defense-in-depth for all user-facing endpoints
- All handlers now validate user authorization before processing

## Limitations

- Maximum file size: 2GB (Telegram Bot API limitation)
- Processing time dependent on video length/quality
- Queue system handles requests sequentially
- Single admin user configuration
- YouTube only support (no other platforms)