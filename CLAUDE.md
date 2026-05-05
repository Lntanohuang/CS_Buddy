# LearnPal — Agent 守则

## 1. 项目地图

| 部分 | 路径 | 命令 | 端口 |
|---|---|---|---|
| Server (FastAPI) | `server/` | `cd server && $LEARNPAL_PYTHON -m uvicorn app.main:app --port 8010` | 8010 |
| Web (Vue 3 + Vite) | `web/` | `npm --prefix web run dev` | 5193 |
| MongoDB | 外部 | `mongodb://localhost:27017` (db: `cs_buddy`) | 27017 |
| LLM | 讯飞星火 v1 兼容 | 读 `server/.env` 的 `OPENAI_API_KEY` | — |

核心 API: `POST /api/v1/chat/stream` (SSE，事件类型 `token` / `done` / `error`)。
健康端点: `GET /health`。
Web 路由: `/login → /app/chat`（mock 登录，存 localStorage `user`）。

## 2. Definition of Done（必读）

任何代码改动**必须**满足以下五条才能向用户报告"完成"：

1. **静态检查**：相关文件 lint / type 检查 0 error。
2. **预检通过**：`bash scripts/preflight.sh` 返回 0。
3. **冒烟通过**：`bash scripts/smoke.sh` 返回 0（含 server 启动、SSE 流测试、Playwright e2e、日志扫错）。
4. **单元测试**：相关测试通过（如果有的话）。
5. **本机无法验证的明说**：缺凭证、缺数据库、缺外部服务时，**显式告诉用户哪一步无法验证**，**不允许只在回复里"声明已修复"**。

> Stop hook 会自动在你结束会话前跑 #2 + #3。失败时会被推回去继续修，**不要试图绕过**。

## 3. 反向规则（What NOT to do）

- ❌ 不要在 smoke 失败时改 smoke.sh "让它通过"——先改业务代码
- ❌ 不要 mock 掉真实 LLM 调用以"加快冒烟"——冒烟的价值就是验真实链路
- ❌ 不要在 PR 描述里写"已通过测试"，但实际没跑 smoke
- ❌ 不要为单次任务擅自加新依赖——先和用户确认
- ❌ 不要修改 `e2e/*.spec.ts` 或 `scripts/smoke.sh` 而不告诉用户——这些是**契约**
- ❌ 不要为了让 Stop hook 放行而设 `SKIP_SMOKE=1`——这是逃生开关，不是日常用

## 4. 逃生开关

LLM 偶发 timeout 或网络抖动让 smoke 假阳性时，**用户**可以临时关闭冒烟阻断：

```bash
export SKIP_SMOKE=1
# 这次会话内 Stop hook 不再跑 smoke
unset SKIP_SMOKE  # 用完关掉
```

或永久关闭：编辑 `.claude/settings.local.json` 注释掉 Stop hook 段落。

**agent 不允许自己设 `SKIP_SMOKE`**。只有用户能。

## 5. Python 环境

Server 用的是 conda 环境 **`Langchain-sgg`**，不是 `server/.venv`（后者是空的，已知问题）。脚本默认路径：

```
/opt/anaconda3/envs/Langchain-sgg/bin/python
```

要换环境时设 `LEARNPAL_PYTHON` 环境变量覆盖：
```bash
export LEARNPAL_PYTHON=/path/to/your/python
```

`preflight.sh` / `smoke.sh` / `post-edit.sh` 都通过这个变量定位解释器。

## 6. 已知架构注意

- `server/app/agent/graph.py` 是 LangGraph 流，节点改动会同时影响 SSE 流形态
- `server/app/routers/chat.py` 用关键词路由到 `quiz` / `explain` / `clarify` 三个 skill
- `web` 当前是 mock-only 后端集成（除 chat stream 外），其他 API 没接通——agent 看 `web/src/mock/` 别误以为已经接 API
- `server/.env` 在 Claude Code 的 deny 列表里，**agent 永远读不到**——只能让用户改

## 7. TODO（未来工作）

- **Eval 层**：当前 smoke 只验"管道通"，**不验 LLM 答案质量**。后续 prompt/模型改动需要加 Promptfoo 或自建打分器。**改动 prompt 时提醒用户考虑 eval**。
- **更多 spec**：当前只有 `chat.spec.ts`，覆盖 `quiz` / `clarify` skill 的 spec 待补。
- **PostToolUse 扩展**：当前仅对 `.py` 跑 `py_compile`，未来可加 ruff 或 mypy。
