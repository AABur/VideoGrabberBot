# VideoGrabberBot: Простое развертывание на Synology DS423+

## Подготовка

### Системные требования
- ✅ **DS423+** - поддерживает Container Manager  
- ✅ **6GB RAM** - достаточно (бот использует ~512MB)
- ✅ **DSM 7.2+** - для Container Manager

### Что нужно сделать перед установкой
1. Установить **Container Manager** из Package Center
2. Создать пользователя для Docker
3. Настроить папки
4. Получить PUID/PGID значения

## Пошаговая инструкция

### Шаг 1: Создание пользователя Docker

1. **Control Panel** → **User & Group** → **User**
2. **Create** → **Create user**
3. Заполните:
   - **Username**: `dockeruser`
   - **Password**: создайте надежный пароль
   - **Email**: оставьте пустым
4. **User Groups**: добавьте в группу `users`
5. **Assign shared folders**: НЕ назначайте доступ к папкам (сделаем позже)
6. **Assign application privileges**: снимите все галочки кроме Container Manager
7. **User speed limit**: оставьте по умолчанию
8. **Apply**

### Шаг 2: Создание структуры папок

1. **File Station** → перейдите в `/volume1/`
2. Создайте папку `docker`
3. Внутри `docker` создайте папку `videograbberbot`
4. Внутри `videograbberbot` создайте:
   ```
   videograbberbot/
   ├── data/     # База данных и файлы
   ├── logs/     # Логи приложения
   └── config/   # Конфигурация (.env файл)
   ```

### Шаг 3: Настройка прав доступа

1. **Правой кнопкой** на папку `videograbberbot` → **Properties**
2. **Permission** → **Create** → **Customize**
3. **User or group**: выберите `dockeruser`
4. **Permissions**: `Read/Write`
5. **Apply to this folder, sub-folders and files**
6. **OK**

### Шаг 4: Получение PUID и PGID

1. **Control Panel** → **Terminal & SNMP** → включите **SSH service**
2. Подключитесь через SSH (используйте Putty или терминал):
   ```bash
   ssh admin@[IP_вашего_NAS]
   ```
3. Выполните команду:
   ```bash
   id dockeruser
   ```
4. **Запишите значения**:
   - `uid=1026` → PUID=1026
   - `gid=100` → PGID=100
   (ваши значения могут отличаться)

### Шаг 5: Создание .env файла

1. **File Station** → перейдите в `/volume1/docker/videograbberbot/config/`
2. **Create** → **Create file** → назовите `.env`
3. Откройте файл и добавьте:
   ```
   # Telegram Bot Configuration
   BOT_TOKEN=YOUR_BOT_TOKEN_HERE
   ADMIN_USER_ID=YOUR_TELEGRAM_USER_ID_HERE
   
   # Database Configuration
   DATABASE_PATH=/app/data/bot.db
   
   # Logging Configuration
   LOG_LEVEL=INFO
   LOG_FILE=/app/logs/bot.log
   ```
4. **Сохраните** файл

### Шаг 6: Развертывание контейнера

1. **Container Manager** → **Project** → **Create**
2. **Project name**: `videograbberbot`
3. **Path**: `/volume1/docker/videograbberbot`
4. Создайте файл **docker-compose.yml**:
   ```yaml
   version: '3.8'
   
   services:
     videograbberbot:
       image: videograbberbot:latest
       container_name: videograbberbot
       restart: unless-stopped
       environment:
         - PUID=1026
         - PGID=100
         - TZ=Europe/Moscow
       env_file:
         - ./config/.env
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
         - ./config:/app/config
       networks:
         - bridge
   ```
5. **Build** (если у вас локальный образ) или **Start**

### Шаг 7: Загрузка образа Docker

**Вариант A: Построить образ локально**
1. Скопируйте проект на NAS
2. В **Container Manager** → **Project** → **Build**

**Вариант B: Использовать готовый образ** (когда будет опубликован)
1. **Container Manager** → **Registry** → поиск образа
2. **Download** образа

## Управление ботом

### Через Container Manager
- **Start/Stop**: Project → videograbberbot → действия
- **Логи**: Container → videograbberbot → Details → Log
- **Мониторинг**: Overview → статистика ресурсов

### Через Telegram
- `/start` - запуск бота
- `/help` - список команд
- Отправка YouTube ссылки - начало загрузки

### Через SSH (для отладки)
```bash
# Просмотр логов
docker logs videograbberbot

# Перезапуск контейнера
docker restart videograbberbot
```

## Резервное копирование

### Автоматический бэкап через Task Scheduler

1. **Control Panel** → **Task Scheduler** → **Create** → **User-defined script**
2. **General**:
   - **Task**: `VideoGrabberBot Backup`
   - **User**: `root`
3. **Schedule**: выберите частоту (рекомендуется ежедневно в 2:00)
4. **Task Settings** → **User-defined script**:
   ```bash
   #!/bin/bash
   
   # Backup directory
   BACKUP_DIR="/volume1/backups/videograbberbot"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   # Create backup directory
   mkdir -p "$BACKUP_DIR"
   
   # Backup database
   cp /volume1/docker/videograbberbot/data/bot.db "$BACKUP_DIR/bot_${DATE}.db"
   
   # Backup config
   cp /volume1/docker/videograbberbot/config/.env "$BACKUP_DIR/env_${DATE}.backup"
   
   # Remove backups older than 30 days
   find "$BACKUP_DIR" -name "bot_*.db" -mtime +30 -delete
   find "$BACKUP_DIR" -name "env_*.backup" -mtime +30 -delete
   ```
5. **OK**

## Решение проблем

### Контейнер не запускается
1. Проверьте логи в Container Manager
2. Убедитесь что .env файл содержит корректные данные
3. Проверьте права доступа к папкам

### Ошибки доступа к файлам
1. Проверьте PUID/PGID значения
2. Убедитесь что dockeruser имеет права на папки
3. Перезапустите контейнер

### Бот не отвечает в Telegram
1. Проверьте BOT_TOKEN в .env файле
2. Убедитесь что контейнер запущен
3. Проверьте интернет-соединение NAS

### Низкая производительность
1. Мониторьте использование ресурсов в Container Manager
2. При необходимости увеличьте лимиты памяти
3. Используйте SSD для ускорения операций с базой данных

## Обслуживание

### Еженедельно
- Проверьте логи на ошибки
- Убедитесь что бэкапы создаются

### Ежемесячно  
- Обновите образ Docker (если доступны обновления)
- Проверьте использование дискового пространства
- Очистите старые временные файлы

### При обновлении
1. Остановите контейнер
2. Сделайте бэкап данных
3. Обновите образ
4. Запустите контейнер
5. Проверьте функциональность