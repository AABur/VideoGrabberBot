# TODO — Автодеплой на NAS (Synology)

- Цель: локальная разработка → `git push nas` → автосборка и перезапуск бота на NAS.
- Роли удалённых репозиториев:
  - `origin` (GitHub): зеркало/резерв без секретов.
  - `nas` (Synology): деплой (через git hook `post-receive`).


## План
- Подготовка: определить переменные, проверить пользователя/доступы/докер, очистить артефакты.
- Выполнение: создать bare‑репозиторий и hook на NAS, подготовить рабочую директорию.
- Развертывание: настроить remotes/алиасы локально и выполнить первый пуш.
- Проверка: убедиться, что контейнер поднялся, логи/здоровье ок, пуши триггерят автодеплой.

## Репозиторные полезности
- Файл примера конфигурации: `.nas_deploy.env.example` → скопировать в `.nas_deploy.env` и заполнить.
- Скрипт начальной настройки: `scripts/nas_bootstrap.sh` — создаёт bare‑репо, ставит hook, настраивает remote `nas` и алиас `push_nas`.
- Утилита удалённого запуска: `scripts/nas_exec.sh -- '<cmd>'` — выполнить команду на NAS в `$APP_DIR`.
- Makefile цели:
  - `make nas-bootstrap` — выполнить bootstrap скрипт.
  - `make nas-push` — деплой (push main:main на NAS).
  - `make nas-status` / `make nas-logs` / `make nas-restart` / `make nas-stop` — управление контейнером.


## Подготовка
- Переменные (уточнить у владельца NAS):
  - NAS_HOST: например, `192.168.1.10` или DNS‑имя.
  - NAS_USER: пользователь деплоя, например `deploy` (член группы `docker`).
  - APP_DIR: рабочая директория, например `/volume1/docker/apps/videograbberbot`.
  - GIT_DIR: bare‑репозиторий, например `/volume1/git/videograbberbot.git`.
- Проверка существующих пользователей/прав:
  - `ssh NAS_USER@NAS_HOST 'id -u && id && groups'`
  - если нет пользователя `deploy`: создать через DSM или CLI; добавить в группу docker: `sudo usermod -aG docker deploy`
  - директории и права: `ssh nas 'ls -ld /volume1 /volume1/apps || true'`
- Проверка Docker/Compose:
  - `ssh nas 'docker --version && (docker compose version || docker-compose --version)'`
- Очистка артефактов (если ранее были неудачные установки):
  - Контейнеры: `ssh nas 'docker ps -a --format "{{.Names}}" | grep -E "videograbber-bot" && docker rm -f videograbber-bot || true'`
  - Старые каталоги: `ssh nas 'test -d /volume1/apps/OLD_PATH && sudo rm -rf /volume1/apps/OLD_PATH || true'`
  - Старые git‑репы: `ssh nas 'test -d /volume1/git/videograbber.git && mv /volume1/git/videograbber.git /volume1/git/videograbber.git.bak.$(date +%s) || true'`
  - Примечание: прежде чем удалять — убедиться, что там нет нужных данных (например, `.env`).


## Выполнение (на NAS)
- Создать директории и выдать права:
  - `ssh nas 'mkdir -p $GIT_DIR $APP_DIR && chown -R $USER:$USER $GIT_DIR $APP_DIR'`
- Инициализировать bare‑репозиторий приёма пушей:
  - `ssh nas 'git init --bare $GIT_DIR'`
- Добавить hook `post-receive` (автодеплой):
  - Создать файл `$GIT_DIR/hooks/post-receive` со следующим содержимым и сделать исполняемым `chmod +x`:
    
    #!/bin/sh
    set -eu
    BRANCH=main
    GIT_DIR="$GIT_DIR"
    WORK_TREE="$APP_DIR"
    PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    read oldrev newrev refname
    [ "$refname" = "refs/heads/$BRANCH" ] || exit 0
    echo "[deploy] Checkout $BRANCH -> $WORK_TREE"
    mkdir -p "$WORK_TREE"
    GIT_WORK_TREE="$WORK_TREE" git --git-dir="$GIT_DIR" checkout -f "$BRANCH"
    cd "$WORK_TREE"
    if [ ! -f .env ] && [ -f .env.example ]; then
      cp .env.example .env
      echo "[deploy] Created .env from template. Edit secrets in $WORK_TREE/.env"
    fi
    if docker compose version >/dev/null 2>&1; then DC="docker compose"; elif command -v docker-compose >/dev/null 2>&1; then DC="docker-compose"; else echo "[deploy] ERROR: docker compose not found"; exit 1; fi
    echo "[deploy] Build…"; $DC build --pull videograbber-bot
    echo "[deploy] Up…"; $DC up -d --remove-orphans videograbber-bot
    docker image prune -f >/dev/null 2>&1 || true
    echo "[deploy] Done."

- Секреты: после первого деплоя отредактировать `$APP_DIR/.env` (не хранить секреты в GitHub).


## Развертывание (с локальной машины)
- SSH‑алиас для удобства (`~/.ssh/config`):
  - `Host nas` / `HostName NAS_HOST` / `User NAS_USER` / `IdentityFile ~/.ssh/id_ed25519`
- Добавить remotes:
  - `git remote add origin git@github.com:ORG/VideoGrabberBot.git`
  - `git remote add nas nas:$GIT_DIR`
- Алиас команды деплоя:
  - `git config alias.push_nas 'push nas main:main'`
- Первый пуш (создаст `.env` из шаблона, если его нет):
  - `git push_nas`
- Заполнить секреты на NAS и запустить заново (только один раз):
  - `ssh nas 'nano $APP_DIR/.env'`
  - `ssh nas 'cd $APP_DIR && /usr/local/bin/docker compose up -d --build'`
- Пара утилитарных алиасов (локально):
  - `alias vps='ssh nas "cd $APP_DIR && /usr/local/bin/docker compose ps"'`
  - `alias vlog='ssh nas "cd $APP_DIR && /usr/local/bin/docker compose logs -f --tail=200 videograbber-bot"'`
  - `alias vrestart='ssh nas "cd $APP_DIR && /usr/local/bin/docker compose restart videograbber-bot"'`
  - `alias vstop='ssh nas "cd $APP_DIR && /usr/local/bin/docker compose stop videograbber-bot"'`


## Проверка
- Статус контейнера: `vps` — должен быть `running`, `restart: unless-stopped`.
- Логи: `vlog` — убедиться, что бот стартует без ошибок (config ok, токен загружен).
- Healthcheck: `docker inspect --format='{{json .State.Health}}' videograbber-bot | jq` (если jq установлен) — статус `healthy`.
- Функционал: отправить тестовую ссылку боту в Telegram, проверить ответы/выгрузку.
- Автодеплой: сделать пустой коммит, `git push_nas`, убедиться по логам, что hook отработал (build/up).
- Роллбек (при необходимости): `git revert <bad_commit>` → `git push_nas` (вернёт код на стабильный уровень).


## Чистка и обслуживание
- Очистка старых артефактов:
  - Неиспользуемые образы: `ssh nas 'docker image prune -f'`
  - Оставшиеся контейнеры/сети: `ssh nas 'docker system prune -f'` (с осторожностью).
- Бэкап:
  - Использовать Hyper Backup для `$APP_DIR` и docker volumes (данные/логи) или периодический `rsync`.
- Обновление yt-dlp:
  - Локально обновить зависимости (или пересобрать образ), затем `git push_nas` (hook сделает `build --pull`).


## Требуются уточнения (заполнить перед запуском)
- Точные значения: `NAS_HOST`, `NAS_USER`, `APP_DIR`, `GIT_DIR`.
- Наличие Compose v2 на NAS (или fallback на `docker-compose`).
- Нужно ли сохранять какие‑либо старые директории/файлы с предыдущего развёртывания (если да — куда бэкапнуть).
