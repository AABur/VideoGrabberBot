# VideoGrabberBot

A Telegram bot for downloading videos and audio from YouTube with format selection options.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.13%2B-blue" alt="Python 3.13+">
  <img src="https://img.shields.io/badge/framework-aiogram-blue" alt="Aiogram">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT">
</p>

## Disclaimer

**This project is a personal educational initiative, created solely for learning purposes and is not intended for commercial use.** It was developed to practice modern Python development techniques, asynchronous programming, and Telegram API interactions. Please respect copyright laws and platforms' terms of service when using this software.

## Features

- **Video Downloads**: Get videos from YouTube in multiple formats:
  - SD (480p)
  - HD (720p)
  - Full HD (1080p)
  - Original (Maximum available quality)
- **Audio Extraction**: Extract high-quality MP3 (320kbps) audio from videos
- **Access Control**: Restrict bot usage through invitation links or admin approval
- **Queue System**: Asynchronous download queue for handling multiple requests
- **Error Handling**: Comprehensive error handling with admin notifications
- **Modern Architecture**: Built with asyncio, aiogram, and yt-dlp

## How It Works

1. **Send a YouTube link** to the bot
2. **Choose a format** from the provided options
3. **Wait for download** to complete
4. **Receive the file** directly in your Telegram chat

## Quick Start

### Requirements

- Python 3.13+
- Telegram Bot API token (from [BotFather](https://t.me/botfather))
- [uv](https://github.com/astral-sh/uv) - Python package installer and environment manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AABur/VideoGrabberBot.git
   cd VideoGrabberBot
   ```

2. **Set up environment with uv**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **For development, install dev dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

4. **Configure the bot**:
   Create a `.env` file with:
   ```
   TELEGRAM_TOKEN=your_telegram_token
   ADMIN_USER_ID=your_telegram_user_id
   ```

5. **Run the bot**:
   ```bash
   uv run python run.py
   ```

## Development

### Commands

```bash
# Run the bot
uv run python run.py

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=bot --cov-report=term-missing --cov-report=html

# Run a specific test
uv run pytest tests/test_file.py::test_function_name

# Type checking
uv run mypy .

# Format code
uv run ruff format .

# Lint code with Ruff
uv run ruff check .

# Lint code with wemake-python-styleguide
uv run flake8 . --select=WPS

# Complete linting sequence (format & lint with both linters)
uv run ruff check && uv run ruff format && uv run flake8 . --select=WPS
```

### Makefile Commands

The project includes a Makefile for simplified development workflow:

```bash
# Format and lint code (Ruff only)
make lint

# Run all linting tools (format, ruff check, and wemake-python-styleguide)
make lint-all

# Run type checking
make mypy

# Run all tests with coverage
make tests

# Run the bot
make run
```

## Project Structure

```
VideoGrabberBot/
├── bot/                # Main bot code
│   ├── handlers/       # Telegram message handlers
│   ├── services/       # Core functionality
│   ├── telegram_api/   # Telegram API client
│   └── utils/          # Utility functions
├── tests/              # Test suite
│   └── integration/    # Integration tests
├── data/               # Database and temp files
├── .flake8             # wemake-python-styleguide configuration
├── Makefile            # Development workflow commands
└── CLAUDE.md           # Development guidelines
```

## Code Quality

This project uses multiple tools to ensure high code quality:

- **Type Checking**: Static type checking with mypy
- **Linting**: 
  - Primary linter: Ruff for fast checking and auto-fixes
  - Secondary linter: wemake-python-styleguide for strict enforcement of best practices
  - The tools work together - Ruff handles most linting and formatting, while wemake-python-styleguide adds stricter checks
- **Formatting**: Automatic code formatting with Ruff
- **Testing**: Comprehensive test suite with pytest

## Technologies

- [aiogram](https://docs.aiogram.dev/) - Modern Telegram Bot framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Powerful YouTube downloader
- [aiosqlite](https://aiosqlite.omnilib.dev/) - Async SQLite database
- [loguru](https://loguru.readthedocs.io/) - Advanced logging
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- [ruff](https://github.com/astral-sh/ruff) - Fast Python linter and formatter
- [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide) - The strictest and most opinionated Python linter

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

This is a personal educational project, but suggestions and improvements are welcome. Please feel free to open an issue or submit a pull request.