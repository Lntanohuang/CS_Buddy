# CS Buddy — RAG 知识库 & 三层记忆系统 设计文档

> 版本: v1.0
> 更新日期: 2026-04-25

---

## 一、总体架构

```
用户消息
  │
  ├──→ [短期记忆] LLM Context Window（最近 N 条原始消息）
  │
  ├──→ [中期记忆] 滑动窗口 + LLM 增量摘要 → MongoDB session_summaries
  │
  ├──→ [长期记忆] 结构化 Profile (MongoDB) + 事件向量检索 (FAISS)
  │
  └──→ [RAG 知识库] Markdown 切片 → FAISS 向量检索 → 注入 Prompt
                                                       │
                                                       ↓
                                              retrieval_logs（全链路可观测）
```

---

## 二、RAG 知识库

### 2.1 数据源

| 课程 | 文件数 | 格式 | 大小 |
|------|--------|------|------|
| 计算机操作系统 | 11 个 md（含课后习题） | Markdown H1/H2/H3 | ~270 KB |
| 计算机组成原理 | 1 个 md | Markdown H1-H4 | ~430 KB |

原始文档位于 `computerResources/`。

### 2.2 切片策略

```
Markdown 文件
  ↓
MarkdownHeaderTextSplitter（按 H1/H2/H3 切分）
  ↓
chunk > 800 字？ → RecursiveCharacterTextSplitter（800 字，100 overlap）
  ↓
Document（page_content + metadata）
```

每个 chunk 的 metadata：
- `source`: 文件名
- `course`: "操作系统" / "计算机组成原理"
- `header_1` / `header_2` / `header_3`: 章节标题层级

### 2.3 Embedding & 检索

| 配置项 | 值 |
|--------|-----|
| Embedding 模型 | 讯飞星火 `embedding-3`（与 LLM 共用 API） |
| 向量数据库 | FAISS（本地文件持久化） |
| 索引位置 | `server/knowledge_index/`（gitignore） |
| 检索 Top-K | 3 |
| 相似度阈值 | 0.72（低于不返回，优雅降级） |
| 首次构建 | 启动时懒加载，第一次调用 `search_knowledge` 时自动构建 |

### 2.4 检索流程

```
用户提问 → Agent 决定调用 search_knowledge tool
  ↓
query → Embedding → FAISS similarity_search_with_relevance_scores(top_k=3)
  ↓
过滤 score < 0.72 的结果
  ↓
格式化返回：【课程 - 文件名】+ 知识片段
  ↓
Agent 结合知识片段生成回答
```

### 2.5 文件结构

```
server/app/rag/
├── __init__.py
├── loader.py          # Markdown 加载 + 切片
├── embeddings.py      # Embedding 模型配置
├── store.py           # FAISS 索引 build/load
└── retriever.py       # 对外检索接口（lazy init）
```

### 2.6 与 XDAN 方案的对比

| 维度 | XDAN（法律调解） | CS Buddy（教育） |
|------|-----------------|------------------|
| 检索路线 | 双路：向量 + ReAct 结构化 | 单路：向量检索 |
| Embedding | BGE-M3（自部署） | 讯飞 embedding-3（赛题要求） |
| 向量库 | MongoDB + 内存计算 | FAISS 本地持久化 |
| 查询理解 | LLM 并行提炼查询 | 直接用原文（知识库小，后续可加） |
| 阈值策略 | 0.75，只取 Top-1 | 0.72，取 Top-3 |
| 降级策略 | 返回空串，不阻塞生成 | 同（返回"未找到"，LLM 用自身知识） |

---

## 三、三层记忆系统

### 3.1 短期记忆（Short-term Memory）

| 属性 | 值 |
|------|-----|
| 存储位置 | LLM 上下文窗口 |
| 生命周期 | 当前对话轮次 |
| 容量 | 模型 context window（星火 4.0Ultra: 128K tokens） |
| 实现方式 | LangGraph `messages` state（已有，无需额外开发） |

保留最近 N 条原始消息（滑动窗口），超出部分触发中期摘要提取。

### 3.2 中期记忆（Mid-term Memory）

#### 核心机制：滑动窗口 + 增量摘要

```
消息 1-10  →  正常对话（短期记忆处理）
消息 11    →  触发摘要提取（消息 1-10）
消息 12-20 →  正常对话
消息 21    →  触发增量摘要（消息 11-20 + 上次摘要）
...
```

#### 消息阈值触发

- **阈值**: 每 10 条新消息触发一次
- **提取方式**: LLM 对比当前会话内容与已有摘要
- **去重策略**: ADD / UPDATE / NOOP

```
LLM 提取指令：
"对比已有摘要和最近 10 条消息，对每条新信息判断：
 - ADD: 全新信息，加入摘要
 - UPDATE: 已有信息需要更新（如掌握度变化）
 - NOOP: 已有信息无变化，跳过"
```

#### MongoDB Collection: `session_summaries`

```json
{
  "_id": ObjectId,
  "session_id": "sess_xxx",
  "user_id": "usr_xxx",
  "summary": "用户正在学习进程调度，已掌握三态模型，对优先级反转仍有困惑...",
  "key_topics": ["进程调度", "优先级反转", "三态模型"],
  "turn_count": 20,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### 3.3 长期记忆（Long-term Memory）

分为两类存储，各取所长：

#### A. 结构化 Profile（MongoDB）— 事实 & 偏好

适合**直接读写、精确查询**的数据：

```json
// Collection: user_profiles
{
  "_id": ObjectId,
  "user_id": "usr_xxx",
  "major": "计算机科学与技术",
  "current_level": "INTERMEDIATE",
  "learning_goal": "EXAM_PREP",
  "preferred_style": "PRACTICE",
  "cognitive_style": "PRACTICAL",
  "knowledge_mastery": {
    "进程": 0.85,
    "存储管理": 0.62,
    "文件系统": 0.45
  },
  "error_patterns": [
    "混淆进程和线程的区别",
    "页面置换算法选择错误"
  ],
  "preferences": {
    "response_length": "detailed",
    "language": "zh-CN",
    "code_examples": true
  },
  "weak_points": ["死锁检测", "虚拟内存"],
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**为什么用 MongoDB 而不是 ES？**
- JSON 文档天然匹配嵌套结构（`knowledge_mastery` 是动态 key-value）
- 部署轻量（`docker run mongo`，~200MB 内存 vs ES 需 1-2GB JVM）
- XDAN 项目验证过的技术选型
- 3 人使用规模完全不需要 ES 的分布式能力

#### B. 事件型记忆（FAISS 向量检索）— 学习事件 & 交互片段

适合**语义相似匹配**的数据：

```json
// 内存 / FAISS 索引，元数据存 MongoDB collection: memory_events
{
  "_id": ObjectId,
  "user_id": "usr_xxx",
  "event_type": "learning_insight",   // learning_insight / error_pattern / preference_signal
  "content": "用户在进程调度章节第3次犯优先级反转的错误，建议下次用银行家算法类比讲解",
  "session_id": "sess_xxx",
  "created_at": ISODate
}
```

**检索方式**：用户新消息 → embedding → FAISS 检索相关历史事件 → 注入 Agent 上下文

#### 事实 vs 事件 的划分标准

| 类型 | 存储 | 示例 | 检索方式 |
|------|------|------|---------|
| 事实 | MongoDB 结构化 | "用户是大二，目标考研" | 精确查询 `db.user_profiles.findOne({user_id})` |
| 偏好 | MongoDB 结构化 | "喜欢用类比解释" | 精确查询 |
| 事件 | FAISS 向量 | "第3次搞混 DFS 和 BFS" | 语义检索（用户问 BFS 时自动召回） |

### 3.4 记忆提取与沉淀流程

```
用户发消息（第 N 条）
  │
  ├─ N % 10 == 0？（消息阈值）
  │    │
  │    ↓ YES
  │  LLM 增量摘要提取（最近 10 条 + 上次摘要）
  │    │
  │    ├─ 输出 ADD/UPDATE/NOOP 标记
  │    │
  │    ├─ UPDATE session_summaries（中期记忆）
  │    │
  │    ├─ 发现事实/偏好变化？
  │    │    ↓ YES
  │    │  UPDATE user_profiles（长期-结构化）
  │    │
  │    └─ 发现有价值事件？
  │         ↓ YES
  │       ADD memory_events + embed → FAISS（长期-向量）
  │
  └─ Agent 生成回答前
       │
       ├─ 读取 user_profiles（结构化画像）
       ├─ FAISS 检索 memory_events（相关历史事件）
       ├─ 读取 session_summary（当前会话摘要）
       └─ 注入 system prompt → 个性化回答
```

---

## 四、全链路可观测：retrieval_logs

### 4.1 数据结构

```json
// Collection: retrieval_logs
{
  "_id": ObjectId,
  "session_id": "sess_xxx",
  "user_id": "usr_xxx",
  "query": "进程和线程有什么区别",
  "skill": "explain",
  "retrieved_chunks": [
    {
      "content": "进程是操作系统进行资源分配...",
      "source": "计算机操作系统（三）——进程.md",
      "course": "操作系统",
      "score": 0.89
    }
  ],
  "memory_context": {
    "profile_loaded": true,
    "events_retrieved": 2,
    "session_summary_loaded": true
  },
  "response_length": 1200,
  "feedback": null,          // 用户反馈：thumbs_up / thumbs_down / null
  "latency_ms": 3200,
  "timestamp": ISODate
}
```

### 4.2 用途

| 用途 | 怎么用 |
|------|--------|
| **检索质量回归** | 统计 score 分布，找出低分高频 query，补充知识库 |
| **记忆效果验证** | 对比有/无记忆上下文时的用户反馈差异 |
| **Prompt 调优** | 分析 response 质量与 skill/chunk 的关系 |
| **知识库迭代** | 找出"未命中"的 query，判断是切片问题还是知识缺失 |
| **阈值调优** | 根据 feedback 统计，调整 0.72 相似度阈值 |

---

## 五、MongoDB Collections 总览

| Collection | 用途 | 写入频率 |
|------------|------|---------|
| `user_profiles` | 用户结构化画像 | 低（摘要触发时更新） |
| `session_summaries` | 会话增量摘要 | 中（每 10 条消息） |
| `memory_events` | 事件型记忆（配合 FAISS） | 低（摘要提取时产生） |
| `retrieval_logs` | RAG 全链路日志 | 高（每次检索） |
| `chat_messages` | 消息持久化（未来） | 高（每条消息） |

---

## 六、技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| LLM | 讯飞星火 4.0Ultra | 对话生成 + 摘要提取 |
| Embedding | 讯飞 embedding-3 | 知识库 + 记忆事件向量化 |
| 向量索引 | FAISS (faiss-cpu) | 知识库检索 + 事件记忆检索 |
| 文档数据库 | MongoDB | Profile + 摘要 + 日志 |
| Agent 编排 | LangGraph | 状态管理 + tool 调用 |
| 后端框架 | FastAPI | REST API + SSE |
| MongoDB 驱动 | motor (异步) + pymongo (同步) | 异步 API + 同步索引构建 |

---

## 七、部署配置

### 环境变量（.env）

```env
# LLM & Embedding
OPENAI_API_KEY=xxx
OPENAI_MODEL=4.0Ultra
OPENAI_BASE_URL=https://spark-api-open.xf-yun.com/v1

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=csbuddy
```

### Docker Compose（腾讯云部署）

```yaml
services:
  mongodb:
    image: mongo:7
    ports:
      - "27027:27017"    # +10 端口策略
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./server
    ports:
      - "8010:8010"
    env_file: ./server/.env
    depends_on:
      - mongodb
```

---

## 八、迭代路线

| 阶段 | 内容 | 状态 |
|------|------|------|
| P1 | RAG 知识库（FAISS + Markdown 切片） | ✅ 已实现 |
| P2 | MongoDB 基础设施 + retrieval_logs | 🔜 下一步 |
| P3 | 短期/中期记忆（滑动窗口 + 增量摘要） | 待开发 |
| P4 | 长期记忆（Profile 持久化 + 事件向量检索） | 待开发 |
| P5 | 用户反馈收集 + 检索质量回归分析 | 待开发 |
| P6 | 查询理解（LLM 改写 query，借鉴 XDAN） | 待开发 |
