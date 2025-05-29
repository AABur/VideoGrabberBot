# Docker Study Plan для VideoGrabberBot

## Обзор обучения

Этот план разработан для изучения Docker на практическом примере VideoGrabberBot. Каждый урок сочетает теорию с практическими задачами из TODO.md проекта.

**Как использовать:**
- 📚 Изучаете теорию в уроке
- 🛠️ Выполняете соответствующие задачи из TODO.md
- ✅ Отмечаете выполненные пункты в TODO.md

**Связь с TODO.md:**
- Урок 1-2 → Подэтап 2.1 (Basic Docker setup)
- Урок 3 → Подэтап 2.2-2.3 (Environment и persistence)  
- Урок 4 → Подэтап 2.4 (Docker Compose)
- Урок 5 → Подэтап 2.5 (Production optimization)
- Урок 6 → Подэтап 2.6-2.7 (Deployment и testing)

## Урок 1: Основы Docker (30-45 минут)

### Что такое Docker?
Docker - это платформа для разработки, доставки и запуска приложений в контейнерах.

**Ключевые концепции:**
- **Контейнер**: Изолированная среда выполнения со всеми зависимостями
- **Образ (Image)**: Шаблон для создания контейнеров
- **Dockerfile**: Инструкции для создания образа
- **Volume**: Постоянное хранилище данных
- **Network**: Сетевое взаимодействие между контейнерами

### Практика 1: Установка и проверка Docker

1. **Установка Docker Desktop**
   - Скачать с официального сайта docker.com
   - Установить и запустить Docker Desktop
   - Проверить установку командой `docker --version`

2. **Первые команды Docker**
   ```bash
   # Проверить версию
   docker --version
   
   # Запустить тестовый контейнер
   docker run hello-world
   
   # Посмотреть запущенные контейнеры
   docker ps
   
   # Посмотреть все контейнеры (включая остановленные)
   docker ps -a
   ```

### 🛠️ Практические задачи (связь с TODO 2.1):
После изучения теории выполните:
- Установить Docker Desktop
- Запустить hello-world контейнер  
- Изучить вывод команды `docker ps -a`

---

## Урок 2: Создание первого Dockerfile (45-60 минут)

**🎯 Цель:** Создать базовый Dockerfile для VideoGrabberBot
**📋 TODO задачи:** Подэтап 2.1 - пункты 1-4

### Что такое Dockerfile?
Dockerfile - это текстовый файл с инструкциями для создания Docker образа.

**Основные инструкции:**
- `FROM`: базовый образ
- `WORKDIR`: рабочая директория
- `COPY`: копирование файлов
- `RUN`: выполнение команд
- `CMD`: команда по умолчанию
- `EXPOSE`: открытие портов
- `ENV`: переменные окружения

### Практика 2: Простой Dockerfile для нашего бота

```dockerfile
# Базовый образ Python
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml ./

# Установка зависимостей
RUN pip install -e .

# Копирование кода приложения
COPY . .

# Команда запуска
CMD ["python", "run.py"]
```

### 🛠️ Практические задачи (связь с TODO 2.1):
1. ✅ Создать Dockerfile для VideoGrabberBot
2. ✅ Добавить .dockerignore файл
3. Собрать образ: `docker build -t videograbberbot .`
4. Протестировать базовый запуск контейнера
5. ✅ Настроить Python environment и установку зависимостей

---

## Урок 3: Переменные окружения и тома (45 минут)

**🎯 Цель:** Настроить конфигурацию и постоянное хранение данных
**📋 TODO задачи:** Подэтап 2.2-2.3 (Environment configuration, Data persistence)

### Переменные окружения в Docker
Используются для передачи конфигурации в контейнер без изменения кода.

### Тома (Volumes)
Механизм для сохранения данных между перезапусками контейнера.

### Практика 3: Улучшенный Dockerfile

```dockerfile
FROM python:3.11-slim

# Создание пользователя (безопасность)
RUN useradd --create-home --shell /bin/bash bot

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка Python зависимостей
COPY pyproject.toml ./
RUN pip install -e .

# Копирование кода
COPY . .

# Создание директорий для данных
RUN mkdir -p /app/data /app/data/temp && \
    chown -R bot:bot /app

# Переключение на пользователя bot
USER bot

# Том для постоянных данных
VOLUME ["/app/data"]

# Переменные окружения
ENV BOT_TOKEN=""
ENV ADMIN_USER_ID=""

# Проверка здоровья
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import bot.main; print('OK')" || exit 1

CMD ["python", "run.py"]
```

### Практические задания:
1. Создать .env файл с переменными
2. Запустить контейнер с томом: `docker run -v $(pwd)/data:/app/data videograbberbot`
3. Передать переменные окружения: `docker run --env-file .env videograbberbot`

---

## Урок 4: Docker Compose (60 минут)

### Что такое Docker Compose?
Инструмент для определения и запуска многоконтейнерных приложений.

### Практика 4: docker-compose.yml

```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: videograbberbot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_USER_ID=${ADMIN_USER_ID}
    volumes:
      - bot_data:/app/data
      - ./logs:/app/logs
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "python", "-c", "import bot.main; print('OK')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  bot_data:
    driver: local

networks:
  bot_network:
    driver: bridge
```

### Практические задания:
1. Создать docker-compose.yml
2. Запустить: `docker-compose up -d`
3. Посмотреть логи: `docker-compose logs -f`
4. Остановить: `docker-compose down`

---

## Урок 5: Оптимизация и production (60-90 минут)

### Multi-stage builds
Создание оптимизированных образов с минимальным размером.

### Практика 5: Production Dockerfile

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml ./
RUN pip install --user -e .

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash bot

# Copy installed packages from builder
COPY --from=builder /root/.local /home/bot/.local

WORKDIR /app

# Copy application
COPY . .

# Set up directories and permissions
RUN mkdir -p /app/data /app/data/temp /app/logs && \
    chown -R bot:bot /app

USER bot

# Make sure local packages are in PATH
ENV PATH=/home/bot/.local/bin:$PATH

VOLUME ["/app/data", "/app/logs"]

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import bot.main; print('OK')" || exit 1

CMD ["python", "run.py"]
```

### Практические задания:
1. Создать production Dockerfile
2. Настроить логирование
3. Тестировать restart policies
4. Настроить мониторинг ресурсов

---

## Урок 6: Deployment и мониторинг (45 минут)

### Практика 6: Полная настройка для production

1. **Создание deployment скриптов**
2. **Настройка мониторинга**
3. **Backup и restore процедуры**
4. **Логирование и отладка**

### Итоговые задания:
1. Развернуть бот в production окружении
2. Настроить автоматический restart
3. Проверить работу всех функций бота
4. Создать процедуры backup/restore

---

## Полезные команды Docker

```bash
# Основные команды
docker build -t image_name .           # Собрать образ
docker run -d --name container_name image_name  # Запустить контейнер
docker exec -it container_name bash    # Войти в контейнер
docker logs -f container_name          # Просмотр логов
docker stop container_name             # Остановить контейнер
docker rm container_name               # Удалить контейнер
docker rmi image_name                  # Удалить образ

# Docker Compose
docker-compose up -d                   # Запустить все сервисы
docker-compose down                    # Остановить все сервисы
docker-compose logs -f service_name    # Логи конкретного сервиса
docker-compose exec service_name bash  # Войти в сервис

# Очистка
docker system prune                    # Очистить неиспользуемые ресурсы
docker volume prune                    # Удалить неиспользуемые тома
```

## Ресурсы для дополнительного изучения

- [Официальная документация Docker](https://docs.docker.com/)
- [Docker Compose reference](https://docs.docker.com/compose/compose-file/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/dev-best-practices/)
- [Docker security best practices](https://docs.docker.com/engine/security/)

## Ожидаемые результаты

После прохождения этого плана вы будете уметь:
- Создавать Docker образы для Python приложений
- Настраивать постоянное хранение данных
- Использовать Docker Compose для управления приложением
- Развёртывать бот в production окружении
- Отлаживать проблемы в контейнерах
- Применять лучшие практики безопасности и оптимизации