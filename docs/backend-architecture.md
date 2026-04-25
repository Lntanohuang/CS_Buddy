# CS Buddy 后端架构文档

> 版本: v1.0
> 更新日期: 2026-04-25

---

## 一、技术栈

| 层 | 技术 | 用途 |
|----|------|------|
| Web 框架 | FastAPI + Uvicorn | 异步 REST API + SSE 流式输出 |
| Agent 编排 | LangGraph + LangChain | 状态图 + Tool 调用 + 流式事件 |
| LLM | 讯飞星火 4.0Ultra | 对话生成（OpenAI 兼容接口） |
| Embedding | text2vec-base-chinese | 本地中文向量化（768 维） |
| 向量检索 | FAISS (faiss-cpu) | 知识库 + 记忆事件检索 |
| 数据库 | MongoDB 7 (Motor 异步) | 画像 / 摘要 / 日志持久化 |
| 流式输出 | sse-starlette | Server-Sent Events |

---

## 二、目录结构

```
server/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口 + 生命周期管理
│   ├── config.py                  # Pydantic Settings（环境变量）
│   │
│   ├── agent/                     # LangGraph Agent
│   │   ├── graph.py               # Agent 状态图（tutor → tools → tutor）
│   │   ├── state.py               # AgentState TypedDict
│   │   ├── tools.py               # Agent 工具（search_knowledge + get_profile）
│   │   └── skills/                # Skill Prompt 定义
│   │       ├── __init__.py        # SKILLS dict
│   │       ├── clarify.py         # 追问技能（收集用户意图）
│   │       ├── explain.py         # 讲解技能（知识点解释）
│   │       ├── quiz.py            # 出题技能（JSON 格式题目）
│   │       ├── evals/             # Eval 测试用例
│   │       │   └── evals.json     # 9 个评测用例
│   │       ├── scripts/           # 评测脚本
│   │       │   ├── run_eval.py    # 运行评测
│   │       │   └── grade_eval.py  # 启发式打分
│   │       └── agents/
│   │           └── grader.md      # LLM 打分指令（未来用）
│   │
│   ├── rag/                       # RAG 知识库
│   │   ├── loader.py              # Markdown 按标题切片
│   │   ├── embeddings.py          # Embedding 模型（text2vec-base-chinese）
│   │   ├── store.py               # FAISS 索引 build / load / get_or_build
│   │   └── retriever.py           # 对外检索接口（lazy init, L2 阈值过滤）
│   │
│   ├── db/                        # MongoDB 数据层
│   │   ├── mongo.py               # Motor 异步连接管理（单例）
│   │   ├── collections.py         # 5 个 Collection 定义
│   │   └── retrieval_logger.py    # 检索日志异步写入
│   │
│   ├── routers/
│   │   └── chat.py                # POST /chat/stream（SSE 聊天流）
│   │
│   └── models/
│       └── schemas.py             # Pydantic 请求/响应 Schema
│
├── knowledge_index/               # FAISS 持久化索引（gitignore）
├── .env                           # 环境变量（gitignore）
└── pyproject.toml                 # 依赖定义
```

---

## 三、Agent 架构

### 3.1 LangGraph 状态图

```
         ┌──────────┐
         │  tutor   │ ← 入口节点
         │ (LLM +   │
         │  tools)  │
         └────┬─────┘
              │
       有 tool_calls?
       ┌──────┴──────┐
       │ YES         │ NO
       ▼             ▼
  ┌─────────┐    ┌──────┐
  │  tools  │    │  END │
  │ (执行)  │    └──────┘
  └────┬────┘
       │
       └──→ tutor（循环）
```

### 3.2 Agent State

```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]  # 消息历史
    user_profile: dict | None                              # 用户画像
    active_skill: str | None                               # 当前激活的 Skill
```

### 3.3 Skills

| Skill | 触发关键词 | System Prompt 核心指令 |
|-------|-----------|----------------------|
| **clarify** | 默认（无明确意图时） | 问 1-2 个追问，收集用户的话题/水平/目标 |
| **explain** | 讲讲/解释/什么是/原理/怎么/如何/区别 | Markdown 输出，代码示例，类比解释，中文 |
| **quiz** | 出题/练习/quiz | 3 题 JSON 数组，SINGLE_CHOICE 或 FILL_BLANK |

### 3.4 Tools

| Tool | 功能 | 实现状态 |
|------|------|---------|
| `search_knowledge` | RAG 知识库检索 | 已接入 FAISS（643 chunks） |
| `get_profile` | 用户画像查询 | Mock（待接入 MongoDB） |

---

## 四、API 接口

### 4.1 已实现

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 `{"status": "ok"}` |
| POST | `/api/v1/chat/stream` | SSE 流式对话 |

### 4.2 SSE 事件协议

```
event: message
data: {"type": "token", "content": "这是一段"}

event: message
data: {"type": "token", "content": "流式输出"}

event: message
data: {"type": "done", "data": {"message_id": "uuid"}}
```

错误：
```
data: {"type": "error", "content": "服务暂时不可用：xxx"}
```

### 4.3 待实现接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/register` | 用户注册 |
| GET/PUT | `/api/v1/profile` | 用户画像 CRUD |
| POST | `/api/v1/eval/start` | 发起测评（调用 quiz skill） |
| POST | `/api/v1/eval/submit` | 提交测评答案 + 评分 |
| GET | `/api/v1/path` | 获取学习路径 |
| POST | `/api/v1/path/generate` | 根据画像生成路径 |
| GET | `/api/v1/notifications` | 获取通知列表 |
| POST | `/api/v1/chat/feedback` | 用户反馈（thumbs_up/down） |

---

## 五、数据层

### 5.1 MongoDB Collections

| Collection | 用途 | 写入频率 |
|------------|------|---------|
| `user_profiles` | 用户结构化画像 | 低 |
| `session_summaries` | 会话增量摘要 | 中（每 10 条消息） |
| `memory_events` | 事件型记忆 | 低 |
| `retrieval_logs` | RAG 全链路日志 | 高（每次聊天） |
| `chat_messages` | 消息持久化 | 高（每条消息） |

### 5.2 retrieval_logs 字段

```json
{
  "session_id": "sess_xxx",
  "user_id": "usr_xxx",
  "query": "进程和线程有什么区别",
  "skill": "explain",
  "retrieved_chunks": [...],
  "memory_context": null,
  "response_length": 1200,
  "feedback": null,
  "latency_ms": 3200,
  "timestamp": "2026-04-25T10:30:00Z"
}
```

---

## 六、配置

### 环境变量（.env）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | (必填) | 讯飞星火 API Key |
| `OPENAI_MODEL` | `gpt-4o-mini` | 模型名（星火用 `4.0Ultra`） |
| `OPENAI_BASE_URL` | `None` | API Base URL |
| `MONGO_URI` | `mongodb://localhost:27017` | MongoDB 连接串 |
| `MONGO_DB` | `csbuddy` | 数据库名 |

### 端口规划

| 服务 | 端口 |
|------|------|
| 后端 API | 8010 |
| 前端 Dev Server | 5193 |
| MongoDB | 27027 |

---

## 七、Eval 框架

用于验证 Skill 质量的自动化评测系统。

### 文件

- `evals/evals.json` — 9 个测试用例（3 per skill），包含 prompt + expectations
- `scripts/run_eval.py` — 调用 LangGraph Agent 跑全部 eval
- `scripts/grade_eval.py` — 启发式规则打分

### 运行

```bash
cd server
conda activate csbuddy
python -m app.agent.skills.scripts.run_eval
python -m app.agent.skills.scripts.grade_eval eval-results/results_xxx.json
```

### 最近结果

- 星火 4.0Ultra：**97% 通过率**（33/34 expectations）
- 唯一失败：BST 性质描述措辞不匹配（检测规则过严，非模型问题）
