#!/usr/bin/env bash
# Smoke: 真实启动 server + SSE 流测试 + Playwright e2e + 日志扫错。
# 目标 < 60s。退出码 0 = 全部通过。
set -uo pipefail

# 代理处理：保留代理（讯飞 API 需要），但让 localhost 旁路
# 注意：不 unset http_proxy/https_proxy，那样讯飞 LLM 调用会失败
export NO_PROXY="${NO_PROXY:-}localhost,127.0.0.1,::1"
export no_proxy="$NO_PROXY"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_LOG="/tmp/learnpal-smoke-server.log"
SERVER_PID=""
START_TS=$(date +%s)

cleanup() {
  local exit_code=$?
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  # 防御性清理：杀任何残留 uvicorn (8010)
  pkill -f "uvicorn app.main:app --port 8010" 2>/dev/null || true
  local elapsed=$(( $(date +%s) - START_TS ))
  if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🟢 Smoke 全部通过 (${elapsed}s)"
  else
    echo ""
    echo "🔴 Smoke 失败 (${elapsed}s) — 看上方日志"
    if [ -f "$SERVER_LOG" ]; then
      echo "--- server.log 末尾 30 行 ---"
      tail -n 30 "$SERVER_LOG" >&2 || true
    fi
  fi
  exit $exit_code
}
trap cleanup EXIT INT TERM

# 0. Preflight
echo "🔍 Preflight..."
bash "$ROOT/scripts/preflight.sh" || exit 1
echo ""

# 1. 启动 uvicorn
echo "🚀 启动 server..."
> "$SERVER_LOG"
PY="${LEARNPAL_PYTHON:-/opt/anaconda3/envs/Langchain-sgg/bin/python}"
(
  cd "$ROOT/server" && \
  "$PY" -m uvicorn app.main:app --port 8010 --log-level warning \
) > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

# 2. 等 /health（最多 30s）
echo "⏳ 等 /health..."
for i in $(seq 1 60); do
  if curl --noproxy '*' -fs http://localhost:8010/health >/dev/null 2>&1; then
    echo "✅ Server 就绪 (${i}*0.5s)"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "❌ Server 进程死了" >&2
    exit 1
  fi
  sleep 0.5
  if [ "$i" -eq 60 ]; then
    echo "❌ Server 30s 内没起来" >&2
    exit 1
  fi
done

# 3. SSE 流测试
echo ""
echo "📡 SSE 流测试 (prompt: 什么是进程)..."
SSE_OUT=$(mktemp)
FIRST_TOKEN_MS=""

# 用 timeout + curl -N 流式拉，写到临时文件，并捕首 token 时刻
(
  exec 3>"$SSE_OUT"
  start_ms=$(python3 -c "import time;print(int(time.time()*1000))")
  echo "$start_ms" >&3
  curl --noproxy '*' -Ns --max-time 25 \
    -H 'Accept: text/event-stream' \
    -H 'Content-Type: application/json' \
    -d '{"session_id":"smoke-'"$$"'","message":"什么是进程"}' \
    http://localhost:8010/api/v1/chat/stream 2>/dev/null \
  | while IFS= read -r line; do
      echo "$line" >&3
      if [ -z "$FIRST_TOKEN_MS" ] && echo "$line" | grep -q '"type":"token"'; then
        now_ms=$(python3 -c "import time;print(int(time.time()*1000))")
        echo "FIRST_TOKEN_MS=$((now_ms - start_ms))" >&3
        FIRST_TOKEN_MS=set
      fi
    done
)

# 解析结果
if ! grep -q '"type":"token"' "$SSE_OUT"; then
  echo "❌ SSE 没收到任何 token 事件" >&2
  echo "--- SSE 输出 ---" >&2
  cat "$SSE_OUT" >&2
  rm -f "$SSE_OUT"
  exit 1
fi

FT_MS=$(grep '^FIRST_TOKEN_MS=' "$SSE_OUT" | head -1 | cut -d= -f2)
TOKEN_COUNT=$(grep -c '"type":"token"' "$SSE_OUT")
HAS_DONE=$(grep -c '"type":"done"' "$SSE_OUT" || echo 0)
rm -f "$SSE_OUT"

echo "✅ 收到 $TOKEN_COUNT 个 token, done=$HAS_DONE, first-token=${FT_MS}ms"
if [ -n "$FT_MS" ] && [ "$FT_MS" -gt 8000 ]; then
  echo "⚠️  first-token > 8s，LLM 可能退化"
fi

# 4. Playwright e2e（如果装了）
echo ""
if [ -f "$ROOT/node_modules/@playwright/test/package.json" ]; then
  echo "🎭 Playwright e2e..."
  (cd "$ROOT" && npx playwright test --reporter=line) || exit 1
else
  echo "⚠️  跳过 Playwright (未装)"
fi

# 5. 扫 server.log 找 ERROR / Exception / Traceback
echo ""
echo "🔍 扫 server.log..."
if grep -iE '(^|[[:space:]])(error|exception|traceback)' "$SERVER_LOG" \
    | grep -viE '(retrieval log|memory)' >/tmp/learnpal-smoke-errors 2>/dev/null; then
  if [ -s /tmp/learnpal-smoke-errors ]; then
    echo "❌ server.log 含错误：" >&2
    cat /tmp/learnpal-smoke-errors >&2
    rm -f /tmp/learnpal-smoke-errors
    exit 1
  fi
fi
rm -f /tmp/learnpal-smoke-errors
echo "✅ 日志 clean"

exit 0
