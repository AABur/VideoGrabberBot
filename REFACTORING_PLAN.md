# План рефакторинга VideoGrabberBot (Пет-проект)

## Цель рефакторинга

Упростить и улучшить проект VideoGrabberBot, убрав переусложнения и сосредоточившись на качестве кода, стабильности и простоте поддержки для пет-проекта.

## Основные принципы

- **Простота над производительностью** - не переусложнять для несуществующих проблем
- **Стабильность** - исправить только критичные проблемы
- **Поддерживаемость** - улучшить читаемость и структуру кода
- **Тестируемость** - сохранить высокое покрытие тестами

## Текущее состояние (анализ отчетов)

### ✅ Сильные стороны проекта
- Отличная архитектура и модульность (9/10)
- Высокое покрытие тестами 97.5%
- Современные практики Python
- Хорошая безопасность
- Качественная документация

### ⚠️ Проблемы требующие внимания
1. **URL_STORAGE утечка памяти** - критичная проблема
2. **Блокирующие yt-dlp операции** - блокируют весь бот
3. **Небезопасный доступ к queue._queue** - race conditions
4. **Переусложненная конкурентная система** - избыточна для пет-проекта

## План рефакторинга по приоритетам

### Приоритет 1: КРИТИЧНЫЕ исправления (1-2 дня)

#### 1.1 Исправить утечку памяти URL_STORAGE

**Проблема**: `URL_STORAGE` растет бесконечно, никогда не очищается

**Простое решение**:
```python
# bot/services/storage.py
import time
from typing import Dict, Tuple, Optional

# TTL-хранилище с автоочисткой
URL_STORAGE: Dict[str, Tuple[str, Optional[str], float]] = {}
URL_TTL_SECONDS = 3600  # 1 час

def store_url(url: str) -> str:
    """Store URL with TTL."""
    url_id = str(uuid.uuid4())[:8]
    URL_STORAGE[url_id] = (url, None, time.time())
    _cleanup_expired()  # Простая очистка при каждом добавлении
    return url_id

def _cleanup_expired() -> None:
    """Remove expired URLs."""
    current_time = time.time()
    expired_keys = [
        url_id for url_id, (_, _, timestamp) in URL_STORAGE.items()
        if current_time - timestamp > URL_TTL_SECONDS
    ]
    for key in expired_keys:
        del URL_STORAGE[key]
```

#### 1.2 Исправить блокирующие yt-dlp операции

**Проблема**: yt-dlp блокирует event loop

**Простое решение**:
```python
# bot/services/async_downloader.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Простой executor для yt-dlp
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="yt-dlp")

async def download_video_async(url: str, ydl_opts: dict) -> dict:
    """Download video in thread pool."""
    loop = asyncio.get_event_loop()
    
    def _sync_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            ydl.download([url])
            return info
    
    return await loop.run_in_executor(_executor, _sync_download)
```

#### 1.3 Убрать небезопасный доступ к queue._queue

**Проблема**: Прямой доступ к `queue._queue` небезопасен

**Простое решение**:
```python
# bot/services/queue.py - заменить проблемные методы
class DownloadQueue:
    def __init__(self):
        self.queue: asyncio.Queue[DownloadTask] = asyncio.Queue()
        self._pending_tasks: list[DownloadTask] = []
        self._lock = asyncio.Lock()
    
    async def add_task(self, task: DownloadTask) -> int:
        async with self._lock:
            await self.queue.put(task)
            self._pending_tasks.append(task)
            return len(self._pending_tasks)
    
    async def get_queue_size(self) -> int:
        async with self._lock:
            return len(self._pending_tasks)
    
    async def is_user_in_queue(self, chat_id: int) -> bool:
        async with self._lock:
            return any(task.chat_id == chat_id for task in self._pending_tasks)
```

### Приоритет 2: УПРОЩЕНИЕ архитектуры (1 день)

#### 2.1 Упростить конкурентную систему

**Проблема**: Слишком сложная система для пет-проекта

**Решение**: Использовать простую очередь с семафором
```python
# bot/services/simple_queue.py
import asyncio
from dataclasses import dataclass

@dataclass
class DownloadTask:
    chat_id: int
    url: str
    format_string: str

class SimpleDownloadQueue:
    def __init__(self, max_concurrent: int = 2):
        self.queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks = set()
    
    async def add_task(self, task: DownloadTask) -> int:
        await self.queue.put(task)
        asyncio.create_task(self._process_task(task))
        return self.queue.qsize()
    
    async def _process_task(self, task: DownloadTask):
        async with self.semaphore:
            self.active_tasks.add(task)
            try:
                # Обработка задачи
                await self._download_task(task)
            finally:
                self.active_tasks.discard(task)
```

#### 2.2 Убрать избыточный мониторинг

**Что убрать**:
- Сложные метрики производительности
- Health checks
- Детальную статистику воркеров

**Что оставить**:
- Базовое логирование
- Простые счетчики успеха/ошибок

### Приоритет 3: УЛУЧШЕНИЯ качества кода (1 день)

#### 3.1 Улучшить обработку ошибок

**Текущая проблема**: Слишком общие исключения

**Решение**:
```python
# bot/exceptions.py
class VideoGrabberError(Exception):
    """Base exception for VideoGrabber."""
    pass

class DownloadError(VideoGrabberError):
    """Download-related errors."""
    pass

class ValidationError(VideoGrabberError):
    """Input validation errors."""
    pass

# Использование в коде
try:
    await download_video(url)
except DownloadError as e:
    logger.error(f"Download failed: {e}")
    await message.answer("❌ Ошибка загрузки видео")
except ValidationError as e:
    logger.warning(f"Invalid input: {e}")
    await message.answer("❌ Некорректная ссылка")
```

#### 3.2 Добавить простые лимиты ресурсов

```python
# bot/config.py - добавить простые лимиты
MAX_FILE_SIZE_MB = 100  # 100MB максимум
MAX_QUEUE_SIZE = 20     # Максимум 20 задач в очереди
MAX_CONCURRENT_DOWNLOADS = 2  # Максимум 2 одновременные загрузки

# Простая проверка в downloader.py
async def validate_download(video_info: dict) -> None:
    file_size = video_info.get('filesize') or video_info.get('filesize_approx', 0)
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Файл слишком большой: {file_size // (1024*1024)}MB")
```

### Приоритет 4: ОЧИСТКА кода (1 день)

#### 4.1 Убрать неиспользуемый код

**Что убрать**:
- Сложные системы мониторинга
- Избыточные абстракции
- Неиспользуемые утилиты

**Что оставить**:
- Основную функциональность
- Тесты
- Базовое логирование

#### 4.2 Упростить конфигурацию

```python
# bot/config.py - упрощенная конфигурация
import os
from dataclasses import dataclass

@dataclass
class BotConfig:
    telegram_token: str
    admin_user_id: int
    max_file_size_mb: int = 100
    max_concurrent_downloads: int = 2
    temp_dir: str = "data/temp"
    db_path: str = "data/bot.db"

def load_config() -> BotConfig:
    return BotConfig(
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        admin_user_id=int(os.getenv("ADMIN_USER_ID", "0")),
    )
```

## Что НЕ ТРОГАЕМ (работает хорошо)

1. **Структуру проекта** - она отличная
2. **Тесты** - покрытие 97.5%, не сломать
3. **Базовую архитектуру** - handlers/services/utils
4. **Безопасность** - авторизация, валидация URL
5. **Логирование** - loguru работает отлично
6. **Docker файлы** - пользователь сказал не трогать пока

## Что УДАЛЯЕМ после рефакторинга

1. **concurrent_queue.py** - слишком сложно для пет-проекта
2. **Сложные системы мониторинга** - избыточно
3. **Connection pooling** - SQLite и так быстрый для пет-проекта
4. **Продвинутые метрики** - не нужны для личного использования

## Временные рамки

| День | Задачи | Результат |
|------|--------|-----------|
| **День 1** | Приоритет 1: критичные исправления | Стабильная работа без блокировок |
| **День 2** | Приоритет 2: упрощение архитектуры | Простая и понятная система |
| **День 3** | Приоритет 3-4: улучшения и очистка | Чистый поддерживаемый код |

## Ожидаемые результаты

### После рефакторинга получим:
- ✅ **Стабильность** - нет утечек памяти и блокировок
- ✅ **Простота** - понятный код без переусложнений  
- ✅ **Производительность** - достаточная для пет-проекта
- ✅ **Поддерживаемость** - легко развивать дальше
- ✅ **Надежность** - сохранено высокое покрытие тестами

### Метрики улучшений:
- Убрано ~40% избыточного кода
- Исправлены 3 критичные проблемы
- Сохранено 97.5% покрытие тестами
- Время рефакторинга: 3 дня vs 4-6 недель из оригинальных планов

## Заключение

Этот план рефакторинга сосредоточен на **реальных проблемах** пет-проекта, а не на гипотетическом масштабировании. Мы исправляем критичные баги, упрощаем архитектуру и сохраняем все преимущества текущего кода.

Результат - стабильный, простой и поддерживаемый Telegram-бот для личного использования.