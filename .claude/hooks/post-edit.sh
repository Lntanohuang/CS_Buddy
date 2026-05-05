#!/usr/bin/env bash
# PostToolUse hook: Edit/Write 完毕后跑轻量检查。
# Python: py_compile (毫秒级，零依赖)
# 其他类型：跳过 — 由 smoke.sh 在最终阶段验证。
# 失败时 exit 2 让 Claude 看到，并继续修。
set -uo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

ROOT="/Users/erichuang/Code/LearnPal"
PY="${LEARNPAL_PYTHON:-/opt/anaconda3/envs/Langchain-sgg/bin/python}"

case "$FILE_PATH" in
  *.py)
    if [ -x "$PY" ]; then
      if ! "$PY" -m py_compile "$FILE_PATH" 2>&1; then
        echo "❌ py_compile 失败: $FILE_PATH" >&2
        exit 2
      fi
    fi
    ;;
  *)
    # .ts / .vue / 其他: 不在 PostToolUse 做（vue-tsc 慢），交给 smoke 阶段
    ;;
esac

exit 0
