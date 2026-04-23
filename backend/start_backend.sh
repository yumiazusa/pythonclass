#!/usr/bin/env sh
set -eu

# 用法:
#   ./start_backend.sh
#   ./start_backend.sh 8081
#   ./start_backend.sh 8081 0.0.0.0 app.main:app
#
# 参数:
#   $1 port (默认 8081)
#   $2 host (默认 0.0.0.0)
#   $3 app  (默认 app.main:app)

PORT="${1:-8081}"
HOST="${2:-0.0.0.0}"
APP_MODULE="${3:-app.main:app}"
APP_ENV="${APP_ENV:-development}"
UVICORN_WORKERS="${UVICORN_WORKERS:-2}"

if [ ! -d "app" ]; then
  echo "请在 backend 目录执行该脚本。当前目录: $(pwd)"
  exit 1
fi

echo "[start_backend] 检查端口占用: ${PORT}"

if command -v ss >/dev/null 2>&1; then
  ss -ltnp 2>/dev/null | grep -E ":${PORT}[[:space:]]" || true
fi

if command -v fuser >/dev/null 2>&1; then
  # 有占用则释放端口（包含 reload 子进程）
  fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
elif command -v lsof >/dev/null 2>&1; then
  PIDS="$(lsof -ti tcp:"${PORT}" || true)"
  if [ -n "${PIDS}" ]; then
    echo "${PIDS}" | xargs kill -TERM >/dev/null 2>&1 || true
    sleep 1
    PIDS_REMAIN="$(lsof -ti tcp:"${PORT}" || true)"
    if [ -n "${PIDS_REMAIN}" ]; then
      echo "${PIDS_REMAIN}" | xargs kill -KILL >/dev/null 2>&1 || true
    fi
  fi
else
  echo "[start_backend] 未找到 fuser/lsof，跳过自动释放端口。"
fi

if [ "${APP_ENV}" = "production" ]; then
  if [ "${UVICORN_WORKERS}" -lt 1 ] 2>/dev/null; then
    UVICORN_WORKERS=1
  fi
  echo "[start_backend] 生产模式启动: python3 -m uvicorn ${APP_MODULE} --host ${HOST} --port ${PORT} --workers ${UVICORN_WORKERS}"
  exec python3 -m uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}" --workers "${UVICORN_WORKERS}"
else
  echo "[start_backend] 开发模式启动: python3 -m uvicorn ${APP_MODULE} --reload --host ${HOST} --port ${PORT}"
  exec python3 -m uvicorn "${APP_MODULE}" --reload --host "${HOST}" --port "${PORT}"
fi
