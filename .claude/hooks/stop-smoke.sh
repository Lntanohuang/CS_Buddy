#!/usr/bin/env bash
# Stop hook: 会话结束前跑 smoke。
# 注：V1 verify --fast 已建好(scripts/verify.sh),但 cases.yaml 还在 calibration 期,
# 真 gate 装早了反而干扰 case 调优——所以这里暂时只跑 smoke。
# 等 5 次 baseline 跑稳后,把下面那行改回 `bash "$ROOT/scripts/verify.sh" --fast`。
# 关键守护：stop_hook_active=true 时直接放行，避免无限循环。
# 关键守护：本轮无 Edit/Write/NotebookEdit 时跳过（防纯讨论会话浪费 ~15s + 抗 LLM API 抖动）。
# 逃生开关：SKIP_SMOKE=1 时直接放行（用户用，agent 不允许设）。
set -uo pipefail

INPUT=$(cat)

# 逃生开关 1：用户设了环境变量
if [ "${SKIP_SMOKE:-0}" = "1" ]; then
  echo "⏭️  SKIP_SMOKE=1，跳过冒烟" >&2
  exit 0
fi

# 守护 2：已经因 hook 阻断过一次，直接放行（防死循环）
ACTIVE=$(echo "$INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null)
if [ "$ACTIVE" = "true" ]; then
  echo "ℹ️  stop_hook_active=true，放行（避免循环）" >&2
  exit 0
fi

ROOT="/Users/erichuang/Code/LearnPal"

# 仅在 LearnPal 仓库下触发——其他项目不跑
CWD=$(echo "$INPUT" | jq -r '.cwd // ""' 2>/dev/null)
case "$CWD" in
  "$ROOT"|"$ROOT"/*) ;;
  *)
    # 不在 LearnPal 范围，放行
    exit 0
    ;;
esac

# 守护 3：本轮（自上一条真用户消息以来）没动过 Edit/Write/NotebookEdit → 跳过冒烟
# 已知盲点：bash 写入（git checkout / mv / rm）不算改动；权衡选了 false negative
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null)
PY="${LEARNPAL_PYTHON:-/opt/anaconda3/envs/Langchain-sgg/bin/python}"
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] && [ -x "$PY" ]; then
  CHANGED=$("$PY" - "$TRANSCRIPT" <<'PYEOF'
import json, sys
path = sys.argv[1]
edits_after = False
with open(path, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") == "user":
            content = (entry.get("message") or {}).get("content")
            is_real_user = isinstance(content, str) or (
                isinstance(content, list)
                and content
                and content[0].get("type") != "tool_result"
            )
            if is_real_user:
                edits_after = False
        elif entry.get("type") == "assistant":
            content = (entry.get("message") or {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "tool_use" and block.get("name") in (
                        "Edit",
                        "Write",
                        "NotebookEdit",
                    ):
                        edits_after = True
print("yes" if edits_after else "no")
PYEOF
)
  if [ "$CHANGED" = "no" ]; then
    echo "ℹ️  本轮无 Edit/Write/NotebookEdit,跳过冒烟" >&2
    exit 0
  fi
fi

# 跑冒烟（calibration 期；稳定后切到 verify --fast）
if bash "$ROOT/scripts/smoke.sh" >&2; then
  exit 0
else
  cat <<'EOF' >&2

🛑 Smoke 失败 — Stop hook 阻断会话结束。
   请修复上述错误后重试。
   逃生（仅在确认 smoke 假阳性时使用）: export SKIP_SMOKE=1
EOF
  exit 2
fi
