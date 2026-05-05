#!/usr/bin/env bash
# Verify: preflight + smoke + eval generation + LLM judge + assertions + summary.
set -uo pipefail

export NO_PROXY="${NO_PROXY:-}localhost,127.0.0.1,::1"
export no_proxy="$NO_PROXY"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_LOG="/tmp/learnpal-verify-server.log"
SERVER_PID=""
START_TS=$(date +%s)
MODE="--fast"
K=2
> "$SERVER_LOG"

cleanup() {
  local exit_code=$?
  if [ -n "$SERVER_PID" ] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  pkill -f "uvicorn app.main:app --port 8010" 2>/dev/null || true
  local elapsed=$(( $(date +%s) - START_TS ))
  if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🟢 Verify (${MODE}) 全部通过 (${elapsed}s)"
  else
    echo ""
    echo "🔴 Verify (${MODE}) 失败 (${elapsed}s) — 看上方日志"
    if [ -f "$SERVER_LOG" ]; then
      echo "--- verify server.log 末尾 30 行 ---" >&2
      tail -n 30 "$SERVER_LOG" >&2 || true
    fi
  fi
  exit $exit_code
}
trap cleanup EXIT INT TERM

while [ $# -gt 0 ]; do
  case "$1" in
    --fast)
      MODE="--fast"
      K=2
      ;;
    --full)
      MODE="--full"
      K=3
      ;;
    *)
      echo "未知参数: $1" >&2
      exit 2
      ;;
  esac
  shift
done

PY="${LEARNPAL_PYTHON:-/opt/anaconda3/envs/Langchain-sgg/bin/python}"

echo "🔍 Preflight..."
bash "$ROOT/scripts/preflight.sh" || exit 1
echo ""

echo "💨 Smoke..."
bash "$ROOT/scripts/smoke.sh" || exit 1
echo ""

# smoke.sh 用 SIGTERM 关 server，pkill 是异步的；
# 主动等端口 8010 真正释放，再起 eval server，避免新进程撞 "address already in use" 秒死
pkill -f "uvicorn app.main:app --port 8010" 2>/dev/null || true
echo "⏳ 等端口 8010 释放..."
for i in $(seq 1 20); do
  if ! lsof -ti :8010 >/dev/null 2>&1; then
    echo "✅ 端口已释放 (${i}*0.5s)"
    break
  fi
  sleep 0.5
  if [ "$i" -eq 20 ]; then
    echo "❌ 端口 8010 10s 内没释放" >&2
    exit 1
  fi
done
echo ""

echo "🚀 启动 eval server..."
(
  cd "$ROOT/server" && \
  "$PY" -m uvicorn app.main:app --port 8010 --log-level warning \
) > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

echo "⏳ 等 /health..."
for i in $(seq 1 60); do
  if curl --noproxy '*' -fs http://localhost:8010/health >/dev/null 2>&1; then
    echo "✅ Eval server 就绪 (${i}*0.5s)"
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "❌ Eval server 进程死了" >&2
    exit 1
  fi
  sleep 0.5
  if [ "$i" -eq 60 ]; then
    echo "❌ Eval server 30s 内没起来" >&2
    exit 1
  fi
done

echo ""
echo "🧪 生成 eval 样本 (k=${K})..."
(
  cd "$ROOT" && \
  "$PY" evals/scripts/run_eval.py \
    --cases evals/cases.yaml \
    --n 12 \
    --k "$K" \
    --out evals/results/latest.jsonl \
    --server-url http://localhost:8010
) || exit 1

echo ""
echo "⚖️  LLM judge..."
(
  cd "$ROOT" && \
  "$PY" evals/scripts/judge.py \
    --latest evals/results/latest.jsonl \
    --rubric evals/rubrics/unified_judge.txt \
    --judge-model lite
) || exit 1

echo ""
echo "✅ 断言 eval..."
(
  cd "$ROOT" && \
  "$PY" evals/scripts/assert_eval.py \
    --latest evals/results/latest.jsonl \
    --history evals/results/history.jsonl
) || exit 1

echo ""
echo "📊 汇总 eval..."
(
  cd "$ROOT" && \
  "$PY" evals/scripts/summarize.py \
    --latest evals/results/latest.jsonl \
    --history evals/results/history.jsonl
) || exit 1

exit 0
