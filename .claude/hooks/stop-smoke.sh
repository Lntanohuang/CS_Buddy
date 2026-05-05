#!/usr/bin/env bash
# Stop hook: 会话结束前跑 smoke。
# 注：V1 verify --fast 已建好(scripts/verify.sh),但 cases.yaml 还在 calibration 期,
# 真 gate 装早了反而干扰 case 调优——所以这里暂时只跑 smoke。
# 等 5 次 baseline 跑稳后,把下面那行改回 `bash "$ROOT/scripts/verify.sh" --fast`。
# 关键守护：stop_hook_active=true 时直接放行，避免无限循环。
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
