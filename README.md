# VideoGrabberBot

A Telegram bot for downloading videos and audio from YouTube with format selection options.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+">
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

- Python 3.11+
- Telegram Bot API token (from [BotFather](https://t.me/botfather))
- [uv](https://github.com/astral-sh/uv) - Python package installer and environment manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AABur/VideoGrabberBot.git
   cd VideoGrabberBot
   ```

2. **Initialize the project**:
   ```bash
   # For regular usage
   make init
   
   # For development (includes dev dependencies)
   make init-dev
   ```

3. **Configure the bot**:
   Edit the created `.env` file with your tokens:
   ```
   TELEGRAM_TOKEN=your_telegram_token
   ADMIN_USER_ID=your_telegram_user_id
   ```

4. **Run the bot**:
   ```bash
   make run
   ```

## Docker Deployment

For containerized deployment, you can use Docker and Docker Compose.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AABur/VideoGrabberBot.git
   cd VideoGrabberBot
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env file with your bot token and admin user ID
   ```

3. **Build and run**:
   ```bash
   # Development environment
   make docker-dev
   
   # Production environment
   make docker-prod
   ```

4. **Check logs**:
   ```bash
   make docker-logs
   ```

### Docker Commands

```bash
# Start development environment
make docker-dev

# Start production environment
make docker-prod

# Build Docker image
make docker-build

# View logs
make docker-logs

# Check container status
make docker-status

# Stop containers
make docker-stop

# Clean up Docker resources
make docker-clean
```

### Production Deployment

For production deployment, use the production compose file:

```bash
# Copy environment file
cp .env.example .env
# Edit .env with production values

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f videograbber-bot

# Alternative: Use deployment script
./deploy.sh prod start
./deploy.sh prod logs
```

### Deployment Script

The project includes a convenient deployment script (`deploy.sh`) for managing Docker containers:

```bash
# Development environment
./deploy.sh dev build      # Build image
./deploy.sh dev start      # Start services
./deploy.sh dev stop       # Stop services
./deploy.sh dev restart    # Restart services
./deploy.sh dev logs       # View logs
./deploy.sh dev status     # Check status

# Production environment
./deploy.sh prod build     # Build image
./deploy.sh prod start     # Start services
./deploy.sh prod stop      # Stop services
./deploy.sh prod restart   # Restart services
./deploy.sh prod logs      # View logs
./deploy.sh prod status    # Check status
```

The production configuration includes:
- Enhanced resource limits
- Better logging configuration
- Host volume mounts for persistent data
- Optimized health checks

### Data Persistence

Docker volumes are used to persist bot data:
- `bot_data`: Contains database and downloaded files
- `bot_logs`: Contains application logs

To backup data:
```bash
# Create backup of bot data
docker run --rm -v videograbberbot_bot_data:/data -v $(pwd):/backup ubuntu tar czf /backup/bot_data_backup.tar.gz -C /data .

# Restore from backup
docker run --rm -v videograbberbot_bot_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/bot_data_backup.tar.gz -C /data
```

## Development

### Setup

```bash
# Initialize development environment
make init-dev

# Check dependencies
make deps-check
```

### Available Commands

All development tasks are available through Makefile. Run `make help` to see all available commands:

```bash
# Project initialization
make init          # Initialize project after cloning
make init-dev      # Initialize with dev dependencies

# Running
make run           # Run the bot

# Testing  
make tests         # Run all tests with coverage
make test          # Run specific test (e.g., make test test_config.py)

# Code quality
make format        # Format code with ruff
make lint          # Lint code with ruff  
make lint-wps      # Lint with wemake-python-styleguide
make lint-all      # Run all linting tools
make mypy          # Type checking
make check         # Run all checks (format, lint, type check)

# Docker
make docker-dev    # Start development environment
make docker-prod   # Start production environment
make docker-build  # Build Docker image
make docker-logs   # View logs
make docker-status # Check status
make docker-stop   # Stop containers
make docker-clean  # Clean up

# Utilities
make clean         # Clean temporary files
make deps-check    # Check dependencies
make help          # Show all available commands
```

## Project Structure

```
VideoGrabberBot/
├── bot/                    # Main bot code
│   ├── handlers/           # Telegram message handlers
│   ├── services/           # Core functionality
│   ├── telegram_api/       # Telegram API client
│   └── utils/              # Utility functions
├── tests/                  # Test suite
│   └── integration/        # Integration tests
├── data/                   # Database and temp files
├── Dockerfile              # Container image definition
├── docker-compose.dev.yml  # Development container orchestration
├── docker-compose.prod.yml # Production container orchestration
├── .dockerignore           # Files to exclude from Docker context
├── .env.example            # Environment variables template
├── deploy.sh               # Deployment automation script
├── .flake8                 # wemake-python-styleguide configuration
├── Makefile                # Development workflow commands
└── CLAUDE.md               # Development guidelines
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