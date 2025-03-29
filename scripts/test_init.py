"""Script to test initialization of database and logging."""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь, чтобы импорты работали
sys.path.append(str(Path(__file__).parent.parent))

from bot.utils.logging import setup_logger
from bot.utils.db import init_db


async def test_initialization():
    """Test basic initialization of logging and database."""
    setup_logger()  # Настроить логирование
    await init_db()  # Инициализировать базу данных
    print("✅ Initialization completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_initialization())