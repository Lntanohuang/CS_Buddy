# LearnPal 冒烟测试速查

## 一句话

`bash scripts/smoke.sh` —— 30~60 秒内验证"项目能起 + 关键路径通"。失败时不要改脚本绕过，要改业务代码。

## 文件结构

```
LearnPal/
├── CLAUDE.md                         # Agent 守则（Definition of Done）
├── docs/SMOKE.md                     # 本文件
│
├── playwright.config.ts              # Playwright 配置（自管 Vite）
├── package.json                      # 仅装 @playwright/test
│
├── e2e/
│   ├── chat.spec.ts                  # chat 主路径 e2e（修改前请告知用户）
│   └── fixtures/test-data.json       # 测试数据：mock user + prompt
│
├── scripts/
│   ├── preflight.sh                  # 预检：.env / Python / 依赖 / Mongo / Node
│   └── smoke.sh                      # 主脚本：preflight → 启动 server → /health → SSE → Playwright → 扫日志
│
└── .claude/
    ├── settings.local.json           # 含 PostToolUse + Stop hook
    └── hooks/
        ├── post-edit.sh              # 写完 .py 后跑 py_compile
        └── stop-smoke.sh             # 会话结束前跑 smoke.sh（带 stop_hook_active 守卫 + SKIP_SMOKE 逃生）
```

## 怎么用

### 手动跑
```bash
bash scripts/smoke.sh
```

### 自动跑（已配置）
- 每次 Edit/Write `.py` → PostToolUse hook 自动 `py_compile` 该文件
- agent 会话想结束 → Stop hook 自动跑完整 smoke

### 逃生开关（仅用户用，agent 不允许）
```bash
export SKIP_SMOKE=1   # 这次会话内 Stop hook 跳过冒烟
unset SKIP_SMOKE      # 用完关掉
```

## 配置

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `LEARNPAL_PYTHON` | `/opt/anaconda3/envs/Langchain-sgg/bin/python` | Python 解释器路径（conda env Langchain-sgg） |
| `SKIP_SMOKE` | unset | 设 `1` 让 Stop hook 跳过冒烟 |
| `NO_PROXY` | 自动加 `localhost,127.0.0.1` | smoke.sh 内部加，不影响讯飞 LLM 远程调用 |

## 冒烟首次跑——发现的真实问题

冒烟脚本第一次跑时连续抓到 **4 个真实问题**（这就是冒烟的价值）：

| # | 问题 | 位置 | 状态 |
|---|---|---|---|
| 1 | `server/.venv` 没装核心依赖（缺 fastapi/uvicorn/sse-starlette/motor 等） | server | ✅ 改用 conda `Langchain-sgg` 环境 |
| 2 | `langchain` 主包缺失（仅有间接依赖） | conda env | ✅ `pip install langchain` |
| 3 | curl 受系统代理 `http_proxy=127.0.0.1:15236` 影响，访问 localhost 返回 503 | smoke.sh | ✅ 加 `NO_PROXY=localhost` + `curl --noproxy '*'` |
| 4 | **`server/app/agent/graph.py:38` 用 `model.invoke()` 不是流式调用，导致 LangGraph 不发 `on_chat_model_stream` 事件，SSE 永远收不到 token** | server | ✅ 已修复：模型实现 LangChain 流式接口，`tutor_node` 通过 `astream()` 汇总最终消息 |

> 问题 4 是真实的产品 bug。修复点：`SparkOpenAICompatModel` 继承 `BaseChatModel` 并实现 `_stream()`，`tutor_node` 改为 async 并使用 `model.astream()`，现有 `chat.py` 的 `on_chat_model_stream` 订阅逻辑保持不变。

## 当前 smoke 状态

- ✅ Preflight 全部通过
- ✅ Server 启动 + /health 通
- ✅ SSE token + done 事件正常
- ✅ Playwright e2e 通过

**当前整套 smoke 可通过。**

## 扩展指南

### 加新 e2e
1. 在 `e2e/` 下加 `*.spec.ts`
2. fixtures 写到 `e2e/fixtures/`
3. 不需要改 `playwright.config.ts`

### 改 LLM 测试 prompt
编辑 `e2e/fixtures/test-data.json` 的 `chat.prompt`。SSE 测试 prompt 在 `scripts/smoke.sh` 里硬编码（"什么是进程"），改的话两个都改。

### 加更多预检项
在 `scripts/preflight.sh` 里加 `fail`/`ok` 调用即可。最快失败原则：把最容易出问题的检查放最前面。

### 关闭某个 hook
编辑 `.claude/settings.local.json` 注释掉对应 `hooks.PostToolUse` 或 `hooks.Stop` 段落。

## 设计原则（来自 Martin Fowler 《Harness Engineering》）

- **Guides（前馈）**：CLAUDE.md 告诉 agent 怎么做才对
- **Sensors（反馈）**：smoke.sh + hook 在事后自动验证
- **两者都要**——光给规则不验证，规则就是空话
- **每次踩坑回写到 smoke.sh / CLAUDE.md**——这是 harness 的成长机制
