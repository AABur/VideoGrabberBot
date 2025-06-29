# Развертывание VideoGrabberBot на Synology NAS DS423+

## Описание задачи

### Цель
Развернуть контейнеризованное приложение VideoGrabberBot на Synology NAS DS423+ для семейного использования в production.

### Текущее состояние
- ✅ Приложение успешно контейнеризовано и работает в локальной Docker среде
- ✅ Docker реализация завершена (Stage 2 дорожной карты проекта)
- ✅ Все тесты проходят, проверки качества кода выполнены
- ⏳ Готово к production развертыванию на Synology NAS

### Требования
- Развернуть на Synology NAS DS423+ с DSM 7.0+
- Обеспечить сохранность данных при перезапуске контейнера
- Настроить правильное резервное копирование и мониторинг
- Предоставить семье доступ к Telegram боту
- Соблюдать лучшие практики безопасности

### Критерии успеха
- Контейнер VideoGrabberBot стабильно работает на NAS
- База данных и логи корректно сохраняются
- Бот отвечает на команды в Telegram
- Автоматический запуск после перезагрузки NAS
- Стратегия резервного копирования реализована

---

## Реализация решения

### Предварительные требования

- [ ] **Synology NAS DS423+** с DSM 7.0 или новее
- [ ] **Административный доступ** к Synology NAS
- [ ] **Стабильное интернет-соединение** для загрузки Docker образов
- [ ] **SSH доступ включен** (опционально, но рекомендуется для диагностики)
- [ ] **Достаточно места** (минимум 5GB свободного места для Docker и данных приложения)
- [ ] **Telegram Bot Token** от BotFather
- [ ] **Admin Telegram User ID** для контроля доступа к боту

### Шаг 1: Подготовка Synology NAS

#### 1.1 Обновление DSM до последней версии
```bash
# Войти в веб-интерфейс DSM по IP адресу NAS
# Перейти в Панель управления > Обновление и восстановление > Обновление DSM
# Скачать и установить доступные обновления
```

#### 1.2 Включение пакета Docker
```bash
# Открыть Центр пакетов в DSM
# Найти "Docker" и установить пакет Docker
# Дождаться завершения установки
```

#### 1.3 Создание структуры хранения
```bash
# Создать структуру общих папок через Файловую станцию:
/volume1/docker-apps/
└── videograbberbot/
    ├── data/          # Для базы данных SQLite и данных приложения
    ├── logs/          # Для логов приложения
    └── env/           # Для конфигурации окружения
```

### Шаг 2: Настройка окружения

#### 2.1 Создание файла окружения
Создать `/volume1/docker-apps/videograbberbot/env/.env`:

```env
# Конфигурация Telegram бота
TELEGRAM_TOKEN=ваш_токен_бота_здесь
ADMIN_USER_ID=ваш_telegram_user_id

# Конфигурация приложения
DATA_DIR=/app/data
LOG_LEVEL=INFO

# Опционально: конфигурация часового пояса
TZ=Asia/Dubai
```

#### 2.2 Установка правильных разрешений
```bash
# Через SSH (если включен):
sudo chown -R admin:users /volume1/docker-apps/videograbberbot
sudo chmod -R 755 /volume1/docker-apps/videograbberbot

# Или через Файловую станцию:
# Клик правой кнопкой на папку videograbberbot > Свойства > Разрешения
# Убедиться, что у admin полный контроль
```

### Шаг 3: Развертывание контейнера

#### Вариант A: Развертывание через Docker UI (рекомендуется для начинающих)

1. **Открыть приложение Docker** в DSM
2. **Перейти во вкладку Контейнер** > Нажать **Создать**
3. **Настроить параметры контейнера:**
   - **Имя контейнера**: `videograbberbot`
   - **Образ**: Имя вашего Docker образа
   - **Настройки томов:**
     - `/app/data` → `/volume1/docker-apps/videograbberbot/data`
     - `/app/logs` → `/volume1/docker-apps/videograbberbot/logs`
   - **Переменные окружения:**
     - Добавить переменные из файла `.env`
   - **Политика перезапуска**: Если не остановлен

#### Вариант B: Развертывание через Docker Compose (продвинутый)

Создать `/volume1/docker-apps/videograbberbot/docker-compose.yml`:

```yaml
version: '3.8'

services:
  videograbberbot:
    image: videograbberbot:latest
    container_name: videograbberbot
    restart: unless-stopped
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - ADMIN_USER_ID=${ADMIN_USER_ID}
      - DATA_DIR=/app/data
      - TZ=Asia/Dubai
    volumes:
      - /volume1/docker-apps/videograbberbot/data:/app/data
      - /volume1/docker-apps/videograbberbot/logs:/app/logs
    env_file:
      - /volume1/docker-apps/videograbberbot/env/.env
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

Развертывание через SSH:
```bash
ssh admin@ip-вашего-nas
cd /volume1/docker-apps/videograbberbot
sudo docker-compose up -d
```

### Шаг 4: Проверка и тестирование

#### 4.1 Проверка статуса контейнера
```bash
# Через Docker UI: вкладка Контейнер > Проверить статус контейнера
# Через SSH:
sudo docker ps
sudo docker logs videograbberbot
```

#### 4.2 Тестирование функциональности бота
```bash
# Отправить команду /start боту в Telegram
# Отправить YouTube URL для тестирования функции загрузки
# Проверить, что файлы создаются в директории data/temp
```

#### 4.3 Тест сохранности данных
```bash
# Перезапустить контейнер и проверить, что база данных остается целой
sudo docker restart videograbberbot
# Проверить, что бот помнит авторизованных пользователей
```

### Шаг 5: Настройка резервного копирования и мониторинга

#### 5.1 Настройка автоматического резервного копирования
```bash
# Через Панель управления > Планировщик заданий
# Создать ежедневное задание резервного копирования для директории videograbberbot/data
# Запланировать на время низкой нагрузки (например, 3:00 утра)
```

#### 5.2 Скрипт ручного резервного копирования
Создать `/volume1/docker-apps/scripts/backup-videograbberbot.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/volume1/backups/videograbberbot"
DATA_DIR="/volume1/docker-apps/videograbberbot/data"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/videograbberbot-backup-$DATE.tar.gz" -C "$DATA_DIR" .

# Оставлять только последние 7 резервных копий
find $BACKUP_DIR -name "videograbberbot-backup-*.tar.gz" -mtime +7 -delete
```

#### 5.3 Настройка мониторинга
```bash
# Настроить уведомления в Панель управления > Уведомления
# Настроить email уведомления для:
# - События остановки/запуска контейнера
# - Высокое использование ресурсов
# - Завершение/сбой резервного копирования
```

### Шаг 6: Усиление безопасности

#### 6.1 Безопасность токена бота
```bash
# Убедиться, что файл .env имеет ограниченные разрешения:
chmod 600 /volume1/docker-apps/videograbberbot/env/.env

# Никогда не коммитить токены в систему контроля версий
# Перегенерировать токен при компрометации через BotFather
```

#### 6.2 Безопасность NAS
```bash
# Включить 2FA для admin аккаунта в Панель управления > Пользователи и группы
# Использовать сильные пароли
# Поддерживать DSM в актуальном состоянии
# Настроить правила файрвола при необходимости
```

### Шаг 7: Руководство по диагностике

#### Частые проблемы и решения

**Проблема: Контейнер не запускается**
```bash
# Проверить логи на ошибки:
sudo docker logs videograbberbot

# Частые причины:
# - Неправильный TELEGRAM_TOKEN
# - Неверный формат ADMIN_USER_ID
# - Проблемы с разрешениями подключенных томов
```

**Проблема: Бот не отвечает**
```bash
# Проверить сетевое соединение:
sudo docker exec videograbberbot ping api.telegram.org

# Проверить токен бота:
curl -X GET "https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe"

# Проверить логи приложения:
sudo docker logs videograbberbot | grep -i error
```

**Проблема: Ошибки базы данных**
```bash
# Проверить подключение томов:
sudo docker exec videograbberbot ls -la /app/data

# Проверить разрешения на запись:
sudo docker exec videograbberbot touch /app/data/test.txt

# Проверка целостности базы данных:
sqlite3 /volume1/docker-apps/videograbberbot/data/bot.db "PRAGMA integrity_check;"
```

### Шаг 8: Процедуры обслуживания

#### 8.1 Регулярные задачи обслуживания
```bash
# Еженедельно: Проверять статус контейнера и логи
# Ежемесячно: Проверять целостность резервных копий
# Ежеквартально: Обновлять Docker образ при наличии
# Ежегодно: Пересматривать и обновлять настройки безопасности
```

#### 8.2 Процедура обновления
```bash
# Загрузить последний образ:
sudo docker pull videograbberbot:latest

# Остановить текущий контейнер:
sudo docker-compose down

# Запустить с новым образом:
sudo docker-compose up -d

# Проверить функциональность:
sudo docker logs videograbberbot
```

#### 8.3 Аварийное восстановление
```bash
# Восстановить из резервной копии:
sudo tar -xzf videograbberbot-backup-YYYYMMDD_HHMMSS.tar.gz \
  -C /volume1/docker-apps/videograbberbot/data/

# Пересоздать контейнер при необходимости:
sudo docker rm -f videograbberbot
sudo docker-compose up -d
```

---

## Чеклист развертывания

### Перед развертыванием
- [ ] DSM обновлен до последней версии
- [ ] Пакет Docker установлен и запущен
- [ ] Структура хранения создана
- [ ] Файл окружения настроен с правильными токенами
- [ ] Разрешения установлены корректно

### Развертывание
- [ ] Контейнер создан с правильной конфигурацией
- [ ] Тома подключены корректно
- [ ] Переменные окружения установлены
- [ ] Контейнер запускается успешно
- [ ] Бот отвечает на команды

### После развертывания
- [ ] Стратегия резервного копирования реализована
- [ ] Мониторинг настроен
- [ ] Усиление безопасности применено
- [ ] Документация обновлена
- [ ] Члены семьи могут получить доступ к боту

### Проверка
- [ ] Контейнер автоматически запускается после перезагрузки NAS
- [ ] База данных сохраняется при перезапусках
- [ ] Логи правильно собираются
- [ ] Функция загрузки работает
- [ ] Уведомления об ошибках доходят до администратора

---

## Метрики успеха

- **Время работы**: Контейнер работает непрерывно без сбоев
- **Функциональность**: Все команды бота работают как ожидается
- **Производительность**: Загрузки завершаются в разумное время
- **Надежность**: Отсутствие потери данных при перезапусках контейнера
- **Обслуживаемость**: Легко обновлять и диагностировать

---

## Следующие шаги после развертывания

1. **Мониторинг производительности**: Отслеживать использование ресурсов и оптимизировать при необходимости
2. **Обучение пользователей**: Научить членов семьи использовать бота
3. **Улучшение функций**: Рассмотреть добавление веб-интерфейса (в будущем)
4. **Масштабирование**: Оценить необходимость балансировки нагрузки (при росте использования)
5. **Интеграция**: Изучить интеграцию с другими сервисами NAS

Этот документ задача-решение предоставляет полную дорожную карту для успешного развертывания VideoGrabberBot на Synology NAS DS423+ с соблюдением производственных практик.