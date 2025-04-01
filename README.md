# VideoGrabberBot

A Telegram bot for downloading videos and audio from YouTube.

## Features

- Downloads videos from YouTube
- Supports multiple video formats (SD, HD, Full HD, Original)
- Supports audio extraction (MP3 320kbps)
- Access control through invitation links or admin approval
- Asynchronous download queue system
- Persistent storage of user preferences

## Requirements

- Python 3.13+
- Telegram Bot API token
- Make (for development commands)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/VideoGrabberBot.git
   cd VideoGrabberBot
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

3. Configure environment variables:
   Create a `.env` file with your Telegram bot token:
   ```
   TELEGRAM_TOKEN=your_telegram_token
   ```

## Running the bot

```bash
make run
```

Or manually:

```bash
uv run python run.py
```

## Development

### Make Commands

The project includes a Makefile for common development tasks. To see all available commands:

```bash
make help
```

Key commands:

- `make run` - Run the bot
- `make tests` - Run all tests with coverage
- `make test test_file.py::test_function_name` - Run a specific test
- `make check` - Run all checks (format, lint, type check)
- `make format` - Format code with ruff
- `make lint` - Lint code with ruff
- `make mypy` - Type check with mypy

### Manual Commands

If you prefer not to use Make:

- Run the bot: `uv run python run.py`
- Run all tests: `uv run pytest`
- Run a specific test: `uv run pytest tests/test_file.py::test_function_name`
- Test with coverage: `uv run pytest --cov=bot --cov-report=term-missing`
- Type checking: `uv run mypy .`
- Lint code: `uv run ruff check .`
- Format code: `uv run ruff format .`

### Project Structure

- `bot/` - Main bot code
  - `handlers/` - Telegram message handlers
  - `services/` - Core functionality (download, queue, storage)
  - `telegram_api/` - Telegram API client
  - `utils/` - Utility functions
- `tests/` - Unit and integration tests
- `data/` - Database and temporary files storage

## Technologies

- [aiogram](https://docs.aiogram.dev/) - Telegram Bot framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [aiosqlite](https://aiosqlite.omnilib.dev/) - Async SQLite database
- [loguru](https://loguru.readthedocs.io/) - Logging

## License

See the [LICENSE](LICENSE) file for details.