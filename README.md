# VideoGrabberBot

A Telegram bot for downloading videos and audio from YouTube and Instagram.

## Features

- Downloads videos from YouTube and Instagram
- Supports multiple video formats (SD, HD, Full HD, Original)
- Supports audio extraction (MP3 320kbps)
- Access control through invitation links or admin approval

## Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/your-username/VideoGrabberBot.git
   cd VideoGrabberBot
   \`\`\`

2. Create a virtual environment and install dependencies:
   \`\`\`bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   uv pip install -e ".[dev]"
   \`\`\`

3. Configure environment variables:
   Create a \`.env\` file with your Telegram bot token:
   \`\`\`
   TELEGRAM_TOKEN=your_telegram_token
   \`\`\`

## Running the bot

\`\`\`bash
python -m bot.main
\`\`\`

## Development

- Lint: \`ruff check .\`
- Format: \`ruff format .\`
- Type check: \`mypy bot\`
- Test: \`pytest\`
