"""Script to run the bot in test mode."""

import asyncio
import os
import sys

# Add project root to the path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(project_root))

from loguru import logger  # noqa: E402

from bot.main import main  # noqa: E402

if __name__ == "__main__":
    logger.info("Starting bot in test mode...")
    asyncio.run(main())
