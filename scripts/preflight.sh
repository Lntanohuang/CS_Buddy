#!/usr/bin/env bash
# Preflight: 最快失败检查。.env / venv / Mongo / Node。
# 退出码非 0 表示前置条件不满足，smoke 没必要继续。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "❌ preflight: $1" >&2; exit 1; }
ok()   { echo "✅ $1"; }

# 1. server/.env 存在且含 OPENAI_API_KEY 非占位
[ -f "$ROOT/server/.env" ] || fail "server/.env 不存在 (从 .env.example 复制)"
if ! grep -qE '^OPENAI_API_KEY=' "$ROOT/server/.env"; then
  fail "server/.env 缺 OPENAI_API_KEY"
fi
if grep -qE '^OPENAI_API_KEY=(sk-xxx|your_|"")' "$ROOT/server/.env"; then
  fail "server/.env 的 OPENAI_API_KEY 是占位值"
fi
ok ".env 检查通过"

# 2. Python 解释器（优先 LEARNPAL_PYTHON，缺省 conda Langchain-sgg）
PY="${LEARNPAL_PYTHON:-/opt/anaconda3/envs/Langchain-sgg/bin/python}"
[ -x "$PY" ] || fail "Python 解释器不可用: $PY (用 LEARNPAL_PYTHON 环境变量覆盖)"
ok "Python 解释器: $PY ($("$PY" --version))"

# 3. 关键依赖可导入
"$PY" -c "import fastapi, uvicorn, sse_starlette, langchain, langgraph; from langgraph.checkpoint.mongodb import MongoDBSaver" 2>/dev/null \
  || fail "server 依赖未装齐 (在 conda 环境 Langchain-sgg 下 pip install ...)"
ok "Server 依赖完整"

# 4. MongoDB 连通
if command -v mongosh >/dev/null 2>&1; then
  mongosh --quiet --eval "db.runCommand({ping:1})" "mongodb://localhost:27017/cs_buddy" \
    >/dev/null 2>&1 || fail "MongoDB 不可达 (mongodb://localhost:27017)"
else
  "$PY" -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000).admin.command('ping')" 2>/dev/null \
    || fail "MongoDB 不可达"
fi
ok "MongoDB 连通"

# 5. Node + web/node_modules
command -v node >/dev/null 2>&1 || fail "Node 未安装"
[ -d "$ROOT/web/node_modules" ] || fail "web/node_modules 不存在 (cd web && npm install)"
ok "Node + web 依赖就绪"

# 6. Playwright 已装（仅检查，不强制——首次设置时会装）
if [ -f "$ROOT/node_modules/@playwright/test/package.json" ]; then
  ok "Playwright 已装"
else
  echo "⚠️  Playwright 未装 (root)，e2e 步骤会跳过。装: npm install"
fi

echo ""
echo "🟢 Preflight 全部通过"
