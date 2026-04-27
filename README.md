# CS Buddy — AI 个性化计算机学习伴侣

> 第十五届中国软件杯 A3 赛题参赛作品

CS Buddy 是一个基于多智能体协同的个性化学习平台，通过 AI 导师实时对话、智能测评、学习路径规划和个性化画像，帮助计算机专业学生高效学习。

---

## 核心功能

| 功能模块 | 说明 | 对应赛题要求 |
|---------|------|-------------|
| AI 对话课堂 | 基于 RAG 知识库的流式对话，支持讲解/出题/追问 3 种 Skill | 智能体交互能力 |
| 智能测评 | 自动出题 + 评分 + 薄弱点分析 | 多模态测评 |
| 学习路径 | 根据画像动态生成/调整学习路径 | 个性化学习路径 |
| 学习画像 | 七维用户画像 + 知识掌握度雷达图 | 用户画像建模 |
| 通知中心 | 学习提醒 + 测评结果 + 路径更新推送 | 遗忘曲线提醒 |

## 技术栈

### 前端
- Vue 3 + Composition API + TypeScript
- Pinia 状态管理 + Vue Router
- Element Plus + 自定义 Notion 式设计系统
- Vite 构建

### 后端
- FastAPI + Uvicorn（异步 REST API + SSE 流式输出）
- LangGraph（Agent 编排）+ LangChain（LLM 集成）
- 讯飞星火 4.0Ultra（LLM）+ text2vec-base-chinese（Embedding）
- FAISS（向量检索）+ MongoDB（数据持久化）

### AI 架构
- **RAG 知识库**：Markdown 按标题切片 → 本地 Embedding → FAISS 向量检索
- **三层记忆系统**：短期（上下文窗口）+ 中期（增量摘要）+ 长期（结构化 Profile + 事件向量检索）
- **全链路可观测**：retrieval_logs 记录每次检索的 query/chunks/latency/feedback

---

## 项目结构

```
CS_Buddy/
├── web/                          # 前端（Vue 3）
│   ├── src/
│   │   ├── api/                  # 后端 API 调用封装
│   │   ├── components/           # UI 组件
│   │   ├── layouts/              # 布局（Sidebar + Topbar）
│   │   ├── stores/               # Pinia 状态管理
│   │   ├── views/                # 页面视图
│   │   ├── mock/                 # Mock 数据（逐步替换为真实 API）
│   │   └── types/                # TypeScript 类型定义
│   └── vite.config.ts
├── server/                       # 后端（FastAPI）
│   ├── app/
│   │   ├── agent/                # LangGraph Agent
│   │   │   ├── graph.py          # Agent 图定义
│   │   │   ├── tools.py          # Agent 工具（RAG 检索 + 画像查询）
│   │   │   ├── skills/           # Skill Prompt（clarify/explain/quiz）
│   │   │   └── state.py          # Agent 状态定义
│   │   ├── rag/                  # RAG 知识库模块
│   │   │   ├── loader.py         # Markdown 切片
│   │   │   ├── embeddings.py     # Embedding 模型配置
│   │   │   ├── store.py          # FAISS 索引管理
│   │   │   └── retriever.py      # 检索接口
│   │   ├── db/                   # MongoDB 数据层
│   │   │   ├── mongo.py          # 连接管理
│   │   │   ├── collections.py    # Collection 定义
│   │   │   └── retrieval_logger.py # 检索日志记录
│   │   ├── routers/              # API 路由
│   │   ├── models/               # Pydantic Schema
│   │   └── config.py             # 配置管理
│   └── .env                      # 环境变量（gitignore）
├── computerResources/            # 知识库原始文档
│   ├── Computer-operating-system-notes/  # 操作系统（11 个 md）
│   └── computer-organization/            # 计算机组成原理（1 个 md）
└── docs/                         # 设计文档
    ├── PRD.md                    # 产品需求文档
    ├── TDD.md                    # 技术设计文档
    ├── DEV_PLAN.md               # 开发计划
    └── rag-and-memory-design.md  # RAG & 记忆系统设计
```

---

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.11（推荐 Conda）
- MongoDB 7+（Docker 方式最简单）
- 讯飞星火 API Key（[申请地址](https://console.xfyun.cn/)）

### 1. 启动 MongoDB

```bash
docker run -d --name csbuddy-mongo -p 27027:27017 mongo:7
```

### 2. 启动后端

```bash
cd server

# 创建并激活 conda 环境
conda create -n csbuddy python=3.12
conda activate csbuddy

# 安装依赖
pip install -e .
pip install faiss-cpu langchain-community langchain-text-splitters sentence-transformers motor pymongo

# 配置环境变量
cat > .env << 'EOF'
OPENAI_API_KEY=你的讯飞星火APIKey
OPENAI_MODEL=4.0Ultra
OPENAI_BASE_URL=https://spark-api-open.xf-yun.com/v1
MONGO_URI=mongodb://localhost:27027
MONGO_DB=csbuddy
EOF

# 启动（端口 8010）
uvicorn app.main:app --reload --port 8010
```

首次启动时，第一次聊天会自动构建 FAISS 索引（Embedding 643 个知识库 chunk，约需 1-2 分钟）。

### 3. 启动前端

```bash
cd web
npm install
npm run dev
# 浏览器打开 http://localhost:5193
```

### 4. 验证

1. 打开 `http://localhost:5193`，登录进入聊天页
2. 输入：`讲讲进程和线程的区别`
3. 应看到 AI 基于知识库内容的流式回答

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/api/v1/chat/stream` | SSE 流式对话 |

### POST /api/v1/chat/stream

**请求体**：
```json
{
  "session_id": "sess_xxx",
  "message": "什么是死锁"
}
```

**SSE 事件**：
```
data: {"type": "token", "content": "死锁是指..."}
data: {"type": "done", "data": {"message_id": "xxx"}}
data: {"type": "error", "content": "错误信息"}
```

**Skill 自动路由**：
- 包含 `出题`/`练习`/`quiz` → quiz skill
- 包含 `讲讲`/`解释`/`什么是`/`原理`/`怎么`/`如何`/`区别` → explain skill
- 其他 → clarify skill（追问收集信息）

---

## 端口规划

| 服务 | 端口 |
|------|------|
| 前端 Dev Server | 5193 |
| 后端 API | 8010 |
| MongoDB | 27027 |

---

## 设计文档

- [RAG & 三层记忆系统设计](docs/rag-and-memory-design.md) — 知识库架构、三层记忆、全链路可观测
- [产品需求文档](docs/PRD.md)
- [技术设计文档](docs/TDD.md)
- [开发计划](docs/DEV_PLAN.md)

---

## 开发进度

- [x] 前端 UI 全套页面（5 个页签 + 登录/注册/引导）
- [x] FastAPI + LangGraph 后端骨架
- [x] 3 个 Skill（clarify/explain/quiz）+ Eval 框架
- [x] 讯飞星火 4.0Ultra 接入 + 全量 Eval 测试（97% 通过）
- [x] 前端对接后端 SSE 聊天流
- [x] RAG 知识库（Markdown 切片 + FAISS 向量检索）
- [x] MongoDB 基础设施 + retrieval_logs
- [ ] 三层记忆系统实现（中期摘要 + 长期 Profile）
- [ ] 前端对接真实后端（测评/路径/画像/通知）
- [ ] 多 Agent 协同架构
- [ ] 完整知识库（≥5 种资源类型）
- [ ] 部署到腾讯云

---

## 团队

第十五届中国软件杯 A3 赛题参赛团队
