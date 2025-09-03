#!/usr/bin/env bash
set -euo pipefail

# Bootstrap NAS autodeploy: creates bare repo, installs post-receive hook,
# and configures local git remote/alias.
#
# Usage:
#   scripts/nas_bootstrap.sh [ENV_FILE]
#
# By default reads .nas_deploy.env at repo root.

ROOT_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
ENV_FILE="${1:-$ROOT_DIR/.nas_deploy.env}"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

# Required variables (override via env or .nas_deploy.env):
NAS_HOST="${NAS_HOST:-}"
NAS_USER="${NAS_USER:-}"
NAS_ALIAS="${NAS_ALIAS:-nas}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-}"
GIT_DIR="${GIT_DIR:-}"

require_var() {
  local name="$1"; local value="$2"
  if [[ -z "$value" ]]; then
    echo "[nas-bootstrap] ERROR: $name is required. Set it in $ENV_FILE or env." >&2
    exit 1
  fi
}

require_var NAS_HOST "$NAS_HOST"
require_var NAS_USER "$NAS_USER"
require_var APP_DIR "$APP_DIR"
require_var GIT_DIR "$GIT_DIR"

# Determine SSH target: prefer alias if present in ~/.ssh/config, else user@host
SSH_TARGET="$NAS_USER@$NAS_HOST"
if ssh -G "$NAS_ALIAS" >/dev/null 2>&1; then
  SSH_TARGET="$NAS_ALIAS"
fi

echo "[nas-bootstrap] Using SSH target: $SSH_TARGET"

ssh_ok=0
ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_TARGET" 'echo ok' >/dev/null 2>&1 || ssh_ok=$?
if [[ $ssh_ok -ne 0 ]]; then
  echo "[nas-bootstrap] ERROR: SSH to $SSH_TARGET failed. Configure SSH access first (see TODO_NAS_DEPLOY.md)." >&2
  exit 2
fi

echo "[nas-bootstrap] Ensuring directories exist: $APP_DIR, $GIT_DIR"
ssh "$SSH_TARGET" "mkdir -p '$APP_DIR' '$GIT_DIR' && chown -R \"\$(id -un)\":\"\$(id -gn)\" '$APP_DIR' '$GIT_DIR' || true"

echo "[nas-bootstrap] Checking Docker/Compose on NAS"
ssh "$SSH_TARGET" "docker --version >/dev/null && (docker compose version >/dev/null 2>&1 || docker-compose --version >/dev/null 2>&1)" || {
  echo "[nas-bootstrap] WARNING: Docker or Compose is not available on NAS. Hook will fail until installed." >&2
}

echo "[nas-bootstrap] Initializing bare repo at $GIT_DIR (if missing)"
ssh "$SSH_TARGET" "test -d '$GIT_DIR/refs' || git init --bare '$GIT_DIR'"

echo "[nas-bootstrap] Installing post-receive hook"
ssh "$SSH_TARGET" GIT_DIR_ENV="$GIT_DIR" APP_DIR_ENV="$APP_DIR" BRANCH="$BRANCH" bash -s <<'REMOTE_EOF'
set -euo pipefail
GIT_DIR_ENV=${GIT_DIR_ENV:-}
APP_DIR_ENV=${APP_DIR_ENV:-}
BRANCH=${BRANCH:-main}
if [[ -z "${GIT_DIR_ENV}" || -z "${APP_DIR_ENV}" ]]; then
  echo "[deploy] ERROR: GIT_DIR_ENV or APP_DIR_ENV not set for hook install" >&2
  exit 1
fi
HOOK_PATH="$GIT_DIR_ENV/hooks/post-receive"
cat >"$HOOK_PATH" <<HOOK
#!/bin/sh
set -eu
BRANCH=$BRANCH
GIT_DIR="$GIT_DIR_ENV"
WORK_TREE="$APP_DIR_ENV"
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
HOOK
chmod +x "$HOOK_PATH"
echo "[deploy] Hook installed at $HOOK_PATH"
REMOTE_EOF

echo "[nas-bootstrap] Configuring local git remote 'nas'"
if git remote get-url nas >/dev/null 2>&1; then
  git remote set-url nas "$SSH_TARGET:$GIT_DIR"
else
  git remote add nas "$SSH_TARGET:$GIT_DIR"
fi

echo "[nas-bootstrap] Adding convenient git alias 'push_nas'"
git config alias.push_nas 'push nas main:main'

cat <<OUT
[nas-bootstrap] Bootstrap complete.
- Remote:    nas -> $SSH_TARGET:$GIT_DIR
- Work tree: $APP_DIR

Next steps:
1) First deploy:   git push_nas
2) Edit secrets:   ssh $SSH_TARGET 'nano $APP_DIR/.env' (once)
3) Manage:         make nas-status | nas-logs | nas-restart | nas-stop
OUT
