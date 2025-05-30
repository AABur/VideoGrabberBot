# Docker Guide - Практический конспект уроков 1-3

Конспект изученного материала по Docker на примере VideoGrabberBot.

## Структура проекта

```
VideoGrabberBot/
├── bot/                 # Основной код бота
│   ├── config.py       # Конфигурация (поддерживает Docker и локальную среду)
│   ├── main.py         # Точка входа бота
│   └── handlers/       # Обработчики команд
├── Dockerfile          # Инструкции для создания Docker образа
├── .dockerignore       # Исключаемые из сборки файлы
├── .env.example        # Шаблон переменных окружения
├── .env               # Реальные переменные (не коммитится)
├── Makefile           # Команды для управления Docker
├── data/              # Персистентные данные (монтируется как volume)
│   ├── bot.db         # База данных SQLite
│   └── temp/          # Временные загрузки
└── run.py             # Запуск бота
```

## Урок 1: Основы Docker

### Что изучили
- **Docker** - платформа для контейнеризации приложений
- **Контейнер** - изолированная среда со всеми зависимостями
- **Образ (Image)** - шаблон для создания контейнеров

### Практические команды
```bash
# Проверка установки
docker --version

# Тест Docker
docker run hello-world

# Просмотр контейнеров
docker ps -a

# Просмотр образов
docker images
```

## Урок 2: Создание Dockerfile

### Что изучили
- **Dockerfile** - текстовый файл с инструкциями для создания образа
- Основные инструкции: FROM, WORKDIR, COPY, RUN, CMD, ENV

### Наш Dockerfile (финальная версия)
```dockerfile
# Use official Python image
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash bot

# Install uv package manager
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy all source code first
COPY . .

# Install dependencies and package
RUN uv pip install --system -e .

# Create directories for data and set permissions
RUN mkdir -p /app/data /app/data/temp /app/logs && \
    chown -R bot:bot /app

# Switch to non-root user
USER bot

# Configure environment variables
ENV DATA_DIR=/app/data
ENV TEMP_DIR=/app/data/temp
ENV DB_PATH=/app/data/bot.db

# Configure volumes for persistent data
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); import bot.config; print('OK')" || exit 1

# Default command
CMD ["python", "run.py"]
```

### .dockerignore
```
.git
.venv
venv
__pycache__
*.pyc
.pytest_cache
htmlcov
.coverage
.DS_Store
.claude
```

### Команды сборки и запуска
```bash
# Сборка образа
docker build -t videograbberbot .

# Запуск контейнера
docker run -d --name videograbberbot videograbberbot

# Просмотр логов
docker logs -f videograbberbot

# Остановка и удаление
docker stop videograbberbot
docker rm videograbberbot
```

## Урок 3: Environment Variables и Data Persistence

### Environment Variables

**Проблема:** Токены и настройки не должны быть захардкожены в коде.

**Решение:** Использование переменных окружения.

#### .env.example (шаблон)
```bash
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_telegram_user_id_here

# Application Configuration
BOT_NAME=VideoGrabberBot
LOG_LEVEL=INFO
```

#### Передача переменных в контейнер
```bash
# Через --env-file
docker run -d --name videograbberbot --env-file .env videograbberbot

# Через -e (для отдельных переменных)
docker run -d -e TELEGRAM_TOKEN=xxx -e ADMIN_USER_ID=123 videograbberbot
```

### Data Persistence (Volumes)

**Проблема:** Данные в контейнере исчезают при его удалении.

**Решение:** Docker volumes - монтирование папок хоста в контейнер.

#### Настройка в bot/config.py
```python
# File system paths - support both local and Docker environments
BASE_DIR: Path = Path(__file__).parent.parent.absolute()

# Use environment variables if set (Docker), otherwise use local paths
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", str(DATA_DIR / "temp")))
DB_PATH: Path = Path(os.getenv("DB_PATH", str(DATA_DIR / "bot.db")))
```

**Ключевое решение:** 
- В Docker: ENV переменные установлены в Dockerfile (`/app/data`)
- Локально: ENV переменные не установлены, используются относительные пути (`./data`)

#### Команда с volume
```bash
# Монтирование локальной папки data в контейнер
docker run -d --name videograbberbot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  videograbberbot
```

**Результат:** База данных `bot.db` сохраняется на хосте в папке `data/`

## Интеграция с Makefile

Добавили удобные команды:

```makefile
docker-build: ## Build Docker image
	docker build -t videograbberbot .

docker-run: ## Run bot in Docker container (detached) with volume and env
	docker run -d --name videograbberbot --env-file .env -v $(shell pwd)/data:/app/data videograbberbot

docker-stop: ## Stop and remove Docker container
	docker stop videograbberbot || true
	docker rm videograbberbot || true

docker-logs: ## Show Docker container logs
	docker logs -f videograbberbot

docker-restart: docker-stop docker-build docker-run ## Full restart
```

## Основные команды для работы

### Разработка
```bash
# Локальный запуск
make run

# Тесты
make tests

# Полная проверка кода
make lint-all
```

### Docker workflow
```bash
# Сборка
make docker-build

# Запуск с volume и env
make docker-run

# Просмотр логов
make docker-logs

# Полный перезапуск
make docker-restart

# Остановка
make docker-stop

# Статус
make docker-status
```

## Проверка работы

### 1. Сборка и запуск
```bash
make docker-build
make docker-run
```

### 2. Проверка логов
```bash
make docker-logs
# Должно показать успешный запуск без ошибок
```

### 3. Проверка persistence
```bash
# Проверить создание файлов
ls -la data/
# Должны быть: bot.db, temp/

# Перезапустить контейнер
make docker-restart

# Данные должны сохраниться
ls -la data/
```

## Решенные проблемы

### Конфликт путей
**Проблема:** Локальный .env содержал `TEMP_DIR=bot/data/temp`, но Docker ожидает `/app/data/temp`

**Решение:** Убрали пути из .env файла, оставили только в Dockerfile ENV

### Безопасность
- Контейнер запускается от пользователя `bot`, не от root
- Минимальный базовый образ `python:3.13-slim`
- ffmpeg установлен для обработки видео

### Health Check
Автоматическая проверка работоспособности контейнера каждые 30 секунд.

## Итоги

Получили работающую Docker-контейнеризацию с:
- ✅ Автоматической сборкой через Dockerfile
- ✅ Переменными окружения для конфигурации
- ✅ Постоянным хранением данных через volumes
- ✅ Интеграцией с Makefile для удобства
- ✅ Совместимостью с локальной разработкой