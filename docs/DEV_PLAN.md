# CS Buddy（CS Buddy）开发顺序计划

> **文档版本**：v2.0  
> **创建日期**：2026-04-13  
> **更新日期**：2026-04-13  
> **作者**：技术项目负责人  
> **关联文档**：[PRD v2.0](./PRD.md) · [TDD v2.0](./TDD.md)  
> **变更说明**：v1.0 → v2.0 重大升级。Agent 数量从 4 扩展至 9（新增 DocAgent / MindmapAgent / QuizAgent / VideoAgent / CodeAgent）；注册流程简化 + 引导式对话画像构建；VideoAgent 流水线（LLM 脚本 → 讯飞 TTS → Remotion 渲染）；长期记忆系统（MD 文件 + ES 向量索引）；主动推送系统；多模态辅导；多维度评估即时联动。

---

## 1. 开发阶段划分

### 总览

```
阶段0             阶段1                   阶段2                         阶段3                   阶段4
工程脚手架 ──────▶ 认证+欢迎对话+对话骨架 ──▶ 5资源Agent+路径规划 ─────────▶ 评估+推送+辅导 ──────▶ VideoAgent完善+打磨+MVP
(1 周)             (2 周)                   (3 周)                        (2 周)                  (2 周)
可验证：             可验证：                  可验证：                       可验证：                 可验证：
三层启动+互通        简化注册→引导对话→         对话触发Doc/Mindmap/Quiz/      完整学习闭环              视频渲染可用
Docker/ES/Remotion  画像建立→Mock流式对话      Code资源→路径生成→前端展示     +多维评估+推送通知        +长期记忆完善+MVP交付
```

**总工期**：约 10 周（单人串行约 150 人天；3-4 人并行约 10 周）

---

### 阶段 0：工程脚手架与基础设施（第 1 周）

**目标**：搭建三层项目骨架 + Remotion sidecar 服务、开发环境和 CI 流程，各层可独立启动并互相通信。新增 Elasticsearch 用户记忆向量索引和 Remotion 渲染服务。

**阶段结束可验证**：
- 前端 `npm run dev` 可访问空白页面
- 后端 `mvn spring-boot:run` 可启动，`GET /actuator/health` 返回 200
- AI 层 `uvicorn main:app` 可启动，`GET /health` 返回 200
- Remotion sidecar `node server.js` 可启动，`GET :8020/health` 返回 200
- 后端可成功调用 AI 层的 health 端点
- Docker Compose 一键拉起 MySQL + Redis + Elasticsearch
- 数据库表已通过 Flyway 迁移创建（含 `notification` 表）
- ES 索引 `zhiban-user-memory` + `zhiban-learning-log` + `zhiban-resource-cache` 已创建

**涉及模块**：前端 / 后端 / AI 层 / Sidecar / DevOps

---

### 阶段 1：认证 + 欢迎引导对话 + 对话骨架（第 2-3 周）

**目标**：完成简化注册（仅邮箱+密码）+ 登录全流程，实现引导式欢迎对话（ProfileAgent + OrchestratorAgent 协作，5-8 轮对话建立初始画像），搭建对话页面 + SSE 流式通信链路。AI 层使用 Mock 回复，重点打通前端 → Spring Boot → AI 层的完整数据链路。

**阶段结束可验证**：
- 用户可完成简化注册（邮箱+密码，无问卷）→ 自动跳转欢迎对话页
- 欢迎对话页有欢迎动画效果，AI 以 5-8 轮对话引导用户建立初始画像
- 对话结束后展示画像摘要卡片，用户确认后跳转至学习首页
- 登录后在对话页面发送消息，收到流式 Mock 回复（逐字出现）
- JWT 鉴权工作正常（过期跳转登录、Refresh Token 刷新）
- 用户画像通过 API 可查看和修改

**涉及模块**：前端 / 后端 / AI 层（Mock + ProfileAgent 初版）

---

### 阶段 2：5 资源 Agent + 路径规划（第 4-6 周）

**目标**：实现 OrchestratorAgent 意图识别、DocAgent / MindmapAgent / QuizAgent / CodeAgent 四个资源生成 Agent、PathPlannerAgent 路径规划。用户可通过对话获得多类型个性化学习资源和学习路径。VideoAgent 启动脚本生成部分（Remotion 渲染在阶段 4 完成）。

**阶段结束可验证**：
- 发送"帮我讲讲快速排序"，系统返回个性化知识讲解文档（DocAgent 流式输出）
- 发送"画个思维导图"，系统返回结构化思维导图数据，前端渲染为可交互图
- 发送"给我出几道题"，系统返回多类型练习题（选择/填空/编程）
- 发送"给我看个代码示例"，系统返回可运行代码 + 注释讲解
- 发送"我要学数据结构"，系统生成完整学习路径
- 不同画像的用户对同一知识点获得的资源存在明显差异
- 意图识别能正确区分学习请求 / 路径查询 / 评估请求 / 视频请求 / 闲聊

**涉及模块**：AI 层（核心）/ 后端 / 前端

---

### 阶段 3：评估系统 + 推送 + 多模态辅导（第 7-8 周）

**目标**：实现 EvaluatorAgent 多维度评估（掌握度/效率/趋势/薄弱点）+ 即时联动（画像更新 + 路径调整 + 推送重算），PushService 定时任务（每日提醒 + 不活跃召回），Mermaid 图表前端集成，AI 图片生成（可选）。

**阶段结束可验证**：
- 学完知识点后系统自动生成 mini quiz（3-5 题），提交答案后返回 4 维评估报告
- 评估完成后 5 秒内完成画像更新 + 路径调整 + 推送重算（Level A 即时联动）
- 每日 09:00 自动发送学习提醒通知，用户 ≥3 天未登录发送召回通知
- 登录时首页显示"今日推荐学习"卡片
- 通知铃铛显示未读数量，通知中心可查看历史通知
- 对话中涉及流程/结构时自动嵌入 Mermaid 图表
- 完整学习闭环可跑通：注册 → 引导对话 → 生成路径 → 学习 → 评估 → 路径调整

**涉及模块**：AI 层 / 后端 / 前端

---

### 阶段 4：VideoAgent 完善 + 体验打磨 + MVP 交付（第 9-10 周）

**目标**：完成 VideoAgent 全流水线（LLM 脚本 → 讯飞 TTS 语音合成 → Remotion 视频渲染 → OSS 存储），长期记忆系统完善（MD 文件读写 + ES 向量检索 + 截断策略），性能优化、异常处理、安全防护、测试，达到可交付的 MVP 质量标准。

**阶段结束可验证**：
- 用户请求视频讲解后，系统异步生成 1-5 分钟教学视频并推送完成通知
- 视频可在前端播放器中播放
- 长期记忆 memory.md 正常读写，对话中可检索历史记忆上下文
- 所有异常场景有友好提示（LLM 超时、网络断开、视频生成失败等）
- 对话首 token 延迟 < 1.5 秒
- 500 并发压测通过
- 端到端测试覆盖核心链路

**涉及模块**：AI 层 / Sidecar / 后端 / 前端 / DevOps

---

## 2. 详细任务清单

### 阶段 0：工程脚手架与基础设施

- [ ] **T0-01 — 初始化 Vue 3 前端项目**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：`npm create vite@latest` 创建项目，配置 TypeScript、ESLint、Prettier，安装 Vue Router / Pinia / Axios / Element Plus / Mermaid.js / D3.js（思维导图渲染）

- [ ] **T0-02 — 初始化 Spring Boot 后端项目**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：Spring Initializr 创建项目（Web、Security、MyBatis-Plus、Redis、Elasticsearch），配置 `application.yml` 多环境，建立包结构

- [ ] **T0-03 — 初始化 Python AI 服务项目**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：创建 FastAPI 项目，安装 LangChain / LangGraph 依赖，配置 `.env`，实现 `/health` 端点

- [ ] **T0-04 — Docker Compose 基础设施配置**
  - 所属模块：DevOps
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：无
  - 简要说明：编写 docker-compose.yml，包含 MySQL 8.0 + Redis 7 + Elasticsearch 8.x（含 IK 中文分词插件），配置数据卷持久化。开发环境可选 MinIO 作为对象存储

- [ ] **T0-05 — 数据库表结构迁移脚本**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-04
  - 简要说明：按 TDD 3.1 节编写全部 MySQL 表的 Flyway 迁移 SQL（含 `notification` 表），创建 ES 索引脚本（`zhiban-user-memory`、`zhiban-learning-log`、`zhiban-resource-cache`、`zhiban-knowledge-vector`），配置 dense_vector 字段（1536 维）

- [ ] **T0-06 — 后端公共模块搭建**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02
  - 简要说明：实现 `ApiResult` 统一响应封装、`ErrorCode` 错误码枚举、`GlobalExceptionHandler` 全局异常处理、`CorsConfig` 跨域配置、`SchedulingConfig` 定时任务配置

- [ ] **T0-07 — 前端基础布局与路由框架**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-01
  - 简要说明：实现 `AppLayout` / `Sidebar` / `TopNav`（含 `NotificationBell` 占位）布局组件，配置 Vue Router（含导航守卫 + `/welcome` 路由），搭建 `api/http.ts` Axios 封装

- [ ] **T0-08 — 后端 AIClientService 骨架 + AI 层 Mock 端点**
  - 所属模块：后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-03
  - 简要说明：后端实现 `AIClientService`（`callSync` + `callStream` + `callAsync`），AI 层实现 `/ai/v1/chat` 及 `/ai/v1/chat/welcome` Mock 端点（返回固定 SSE 流），验证双端通信链路

- [ ] **T0-09 — Remotion Node.js sidecar 服务搭建**
  - 所属模块：Sidecar
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：无
  - 简要说明：初始化 Node.js + Remotion 项目，配置 Express 服务监听 8020 端口，实现 `/health` 端点和 `/render` 占位端点（接收脚本 JSON + 音频文件路径，返回视频渲染任务 ID），编写 Dockerfile

- [ ] **T0-10 — 用户记忆文件目录结构初始化**
  - 所属模块：AI 层
  - 优先级：P1
  - 预估工作量：小（<1天）
  - 前置依赖：T0-03
  - 简要说明：创建 `profiles/` 目录结构，实现 memory.md 文件的读写工具函数（`read_memory(user_id)` / `append_memory(user_id, section, entry)`），定义 memory.md 模板格式

---

### 阶段 1：认证 + 欢迎引导对话 + 对话骨架

- [ ] **T1-01 — 后端认证模块（简化注册/登录/Token 刷新）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T0-06
  - 简要说明：实现 `JwtUtil` / `SecurityConfig` / `AuthController` / `AuthService`。注册接口仅接收 email + password（无 survey），返回 `is_new_user` + `welcome_session_id`。登录接口调用 `PushService.getLoginRecommendation()` 返回 `today_recommendation`。实现 JWT 签发、验证、Refresh Token（存 Redis）刷新逻辑

- [ ] **T1-02 — 前端简化注册页面**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：T0-07
  - 简要说明：实现 `RegisterView.vue`，仅 1 步流程（邮箱 + 密码），注册成功后根据 `is_new_user=true` 自动跳转至 `/welcome` 欢迎对话页

- [ ] **T1-03 — 前端登录页面 + Token 管理**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-07
  - 简要说明：实现 `LoginView.vue` + `useAuthStore`。Token 存 localStorage，Axios 拦截器自动附加 Bearer Token，401 时自动刷新。登录后根据 `has_profile` 判断是否跳转 `/welcome`

- [ ] **T1-04 — 前端欢迎对话页面（引导式画像构建）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-07, T1-03
  - 简要说明：实现 `WelcomeView.vue`，包含：欢迎动画（AI CS Buddy角色出场 + 渐变背景 + 微动效）、对话气泡逐步出现（打字机效果）、进度条显示对话进度（5-8 轮）、画像摘要卡片展示 + 确认/修改按钮。使用 SSE 流式接收 AI 回复，调用 `/ai/v1/chat/welcome` 端点

- [ ] **T1-05 — 后端画像模块（CRUD API + 初始画像创建）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `ProfileController` / `ProfileService` / `UserProfileMapper`。支持 `GET /profile`（Redis 缓存 + MySQL 回源）、`PATCH /profile`（更新 + 清除缓存）、`GET /profile/history`（画像变更历史）。新增初始画像创建接口，接收引导对话提取的画像数据

- [ ] **T1-06 — 后端对话模块（会话管理 + SSE 流式推送）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T0-08, T1-01
  - 简要说明：实现 `ChatController`（`POST /chat/sessions`, `GET /chat/sessions`, `POST /chat/stream`）。`/chat/stream` 使用 `SseEmitter`，内部调用 `AIClientService.callStream()` 转发 AI 层流式响应。支持 `welcome` 类型的会话（引导对话）。消息持久化到 `chat_session` + `chat_message` 表

- [ ] **T1-07 — 前端对话页面（消息列表 + 流式渲染）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-07, T1-03
  - 简要说明：实现 `ChatView.vue` + `ChatMessageList` + `ChatInput` + `MessageBubble`。实现 `useSSE` composable 接收 SSE 流，逐 token 追加渲染。集成 `MarkdownRenderer`（markdown-it + highlight.js + Mermaid.js）

- [ ] **T1-08 — AI 层 ProfileAgent 引导对话逻辑（初版）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-03, T0-10
  - 简要说明：实现 ProfileAgent 的引导对话流程：按 7 个画像维度设计对话 Prompt（专业背景、知识基础、认知风格、易错点偏好、学习风格、学习节奏、学习目标），从用户回复中提取结构化画像特征，支持"跳过"操作和默认值填充。实现 `/ai/v1/chat/welcome` 流式端点

- [ ] **T1-09 — 前端个人中心页面（画像查看/修改）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-07, T1-03, T1-05
  - 简要说明：实现 `ProfileView.vue`，展示画像各维度数据（7 维，含知识掌握度雷达图），支持手动修改标签

- [ ] **T1-10 — 阶段 1 全链路联调**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-01 ~ T1-09
  - 简要说明：端到端联调：简化注册 → 跳转欢迎对话 → 引导对话建立画像 → 确认画像 → 跳转首页 → 登录 → 对话页 Mock 流式回复。修复接口参数/格式不一致问题

---

### 阶段 2：5 资源 Agent + 路径规划

- [ ] **T2-01 — 知识图谱数据准备**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-03
  - 简要说明：为首发科目（数据结构与算法）编写知识图谱 JSON。定义知识点 ID、标题、前置依赖、难度。约 20-30 个知识点节点

> ⚠️ **假设**：知识图谱由开发团队根据主流教材自行整理。PRD A3 项待确认是否有教研团队参与。

- [ ] **T2-02 — LangGraph StateGraph 定义与工作流骨架**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-03
  - 简要说明：实现 `CS BuddyState` TypedDict（扩展支持 9 Agent 状态流转），搭建 `build_chat_graph()` 工作流骨架（9 个 Agent 节点占位 + 条件边路由），实现 `with_retry` 重试装饰器

- [ ] **T2-03 — OrchestratorAgent 实现（意图识别 + 9 Agent 路由）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02
  - 简要说明：实现 `orchestrator_node`，使用 LLM 进行意图分类（learn / path_query / evaluate / video_request / code_request / mindmap_request / profile_update / chitchat / clarify 等），输出 intent + confidence。实现 `route_by_intent` 条件路由函数，根据意图和画像中的学习风格决定调用哪些资源 Agent 及组合策略。闲聊意图由 Orchestrator 直接生成回复

- [ ] **T2-04 — ProfileAgent 完善（画像读取 + 分析更新 + 长期记忆）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02, T1-08, T0-10
  - 简要说明：在阶段 1 初版基础上完善：实现 `profile_fetch_node`（从 Spring Boot 获取画像 JSON + 从 ES 检索相关记忆上下文写入 State）和 `profile_update_node`（分析评估结果，计算新 mastery 值，回写 Spring Boot）。实现对话记忆提取（通道 A）：每次对话结束后用 LLM 提取画像相关信息，追加写入 memory.md + 生成向量嵌入存入 ES `zhiban-user-memory`

- [ ] **T2-05 — DocAgent 实现（文档资源生成）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `doc_agent_node`。根据画像中的水平、偏好风格、style_weights 动态构建 Prompt，调用 LLM 流式生成 Markdown 文档讲解。支持多种表述风格（通俗 / 学术 / 类比）。输出包括资源内容和元数据（难度、时长、关联知识点）。实现 `/ai/v1/resource/doc` 流式端点

- [ ] **T2-06 — MindmapAgent 实现（思维导图生成）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `mindmap_agent_node`。使用 LLM 生成结构化 JSON 或 Mermaid mindmap 语法，表达知识点关联结构。实现 `/ai/v1/resource/mindmap` 同步端点。输出格式需与前端 `MindmapViewer` 组件对齐

- [ ] **T2-07 — QuizAgent 实现（练习题生成）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `quiz_agent_node`。根据画像和知识点生成多类型练习题（选择题 / 填空题 / 编程题），使用结构化输出（JSON Mode）确保格式规范，附带标准答案和解析。实现 `/ai/v1/resource/quiz` 同步端点

- [ ] **T2-08 — CodeAgent 实现（代码示例生成）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `code_agent_node`。生成基于真实场景的代码实操案例，含可运行代码 + 完整注释 + 逐步讲解 + 运行结果。支持多种编程语言（Python / Java / C++）。实现 `/ai/v1/resource/code` 同步端点

- [ ] **T2-09 — VideoAgent 脚本生成（阶段 2 部分）**
  - 所属模块：AI 层
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 VideoAgent 的脚本生成部分：使用 LLM 将知识点生成视频脚本 JSON（包含场景列表、旁白文本、代码动画指令、文字覆盖等）。Remotion 渲染和 TTS 集成留到阶段 4

- [ ] **T2-10 — PathPlannerAgent 实现（路径生成 + 调整）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-01, T2-02, T2-04
  - 简要说明：实现 `path_planner_node`。加载知识图谱 JSON，结合用户画像（已掌握知识点跳过），使用 LLM 推理最优学习顺序，生成有序路径节点列表。实现 `/ai/v1/path/generate`、`/ai/v1/path/adjust`、`/ai/v1/path/recommend` 端点

- [ ] **T2-11 — AI 层 FastAPI 正式接口实现**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-03 ~ T2-10
  - 简要说明：将 Mock 端点替换为真实 Agent 调用。整合所有 Agent 端点：`/ai/v1/chat`（流式）、`/ai/v1/resource/doc`（流式）、`/ai/v1/resource/mindmap`、`/ai/v1/resource/quiz`、`/ai/v1/resource/code`、`/ai/v1/path/*`、`/ai/v1/profile/*`

- [ ] **T2-12 — 后端学习路径模块**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `PathController` / `PathService`。`POST /paths` 调用 AI 层生成路径并持久化到 `learning_path` + `path_node` 表。`PATCH /paths/{id}/nodes/{id}` 更新节点状态。`GET /paths` 支持分页查询

- [ ] **T2-13 — 后端资源管理模块**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `ResourceController` / `ResourceService`。支持资源缓存写入 ES（语义检索），`GET /resources/{resourceId}` 获取已缓存资源，`POST /resources/feedback` 提交反馈。支持 5 种资源类型的统一管理

- [ ] **T2-14 — 前端学习路径页面**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-03, T1-07
  - 简要说明：实现 `PathView.vue` + `PathTimeline` + `PathNodeCard`。时间线展示路径节点，标记已完成/进行中/待学习状态，点击节点可跳转到对话页面发起该知识点的学习

- [ ] **T2-15 — 前端 MindmapViewer 组件**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-01
  - 简要说明：实现 `MindmapViewer.vue`，将 MindmapAgent 返回的结构化 JSON 渲染为可交互思维导图。基于 D3.js 或类似库，支持节点展开/折叠、缩放、拖拽

- [ ] **T2-16 — 前端 CodeBlock 增强组件**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-07
  - 简要说明：增强 `CodeBlock.vue`，支持 CodeAgent 返回的代码示例展示：语法高亮、运行结果展示区域、逐步讲解折叠面板、一键复制

- [ ] **T2-17 — 前端对话页增强（多资源卡片 + 路径引导）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T1-07, T2-15, T2-16
  - 简要说明：解析 SSE 中的 `resource_card`（doc / mindmap / quiz / code / video 五种类型）、`metadata`、`mermaid` 类型事件。在对话中嵌入对应 `ResourceCard` / `MindmapViewer` / `CodeBlock` / `VideoCard`（占位）组件。添加 `FeedbackButtons`（有用/没用）

- [ ] **T2-18 — 阶段 2 全链路联调**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-11 ~ T2-17
  - 简要说明：端到端联调核心对话场景。发送学习请求 → 意图识别 → 画像获取 → DocAgent/MindmapAgent/QuizAgent/CodeAgent 资源生成 → 前端多类型展示。发送路径请求 → 路径生成 → 前端时间线展示。全链路流式跑通

---

### 阶段 3：评估系统 + 推送 + 多模态辅导

- [ ] **T3-01 — EvaluatorAgent 实现（多维度评估）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02, T2-04, T2-07
  - 简要说明：实现 `evaluator_node`。题目生成委托给 QuizAgent，EvaluatorAgent 专注于答案分析和多维度评估：①知识掌握度（正确率 + 遗忘曲线模型）②学习效率（单位时间知识点完成数 + 正确率）③进步趋势（多次评估得分变化）④薄弱点分析（错题聚类）。评估完成后触发 Level A 即时联动：调用 ProfileAgent 更新画像 + PathPlannerAgent 调整路径

- [ ] **T3-02 — AI 层评估接口实现**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-01
  - 简要说明：实现 `/ai/v1/evaluate/generate`（调用 QuizAgent）和 `/ai/v1/evaluate/analyze`（调用 EvaluatorAgent，返回 4 维评估报告 + 画像更新 + 路径调整建议）

- [ ] **T3-03 — AI 层自适应路径调整逻辑**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-10, T3-01
  - 简要说明：在工作流中实现 `route_after_eval` 条件边。评估后根据 mastery 阈值（<0.4 回退 / 0.4-0.7 补强 / ≥0.7 推进），调用 PathPlannerAgent 执行路径插入/调整。同时触发推送内容重算

- [ ] **T3-04 — 后端评估模块**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `EvalController` / `EvalService`。`POST /evaluations` 调用 AI 层生成题目并持久化。`POST /evaluations/{id}/submit` 调用 AI 层分析，更新 `evaluation` + `eval_question` 表。联动更新 `user_profile.knowledge_mastery` 并清除 Redis 画像缓存。`GET /evaluations/{id}` 返回含 4 维分析的评估报告

- [ ] **T3-05 — 后端推送服务（PushService + NotificationService）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T1-01, T2-12
  - 简要说明：实现 `PushService`（定时任务）：①`dailyStudyReminder()`（每日 09:00，调用 PathPlannerAgent 获取推荐节点，创建 STUDY_REMINDER 通知）②`inactiveUserReminder()`（每日 10:00，查询 ≥3 天未登录用户，创建 INACTIVE_REMINDER 通知，每日最多 1 条，连续不超过 3 天）③`getLoginRecommendation()`（登录时调用，生成"今日推荐学习"数据）。实现 `NotificationService`（CRUD + 未读计数 + 标记已读）+ `NotificationController`

- [ ] **T3-06 — 前端通知系统（铃铛 + 通知中心 + 推荐卡片）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-07, T1-03
  - 简要说明：实现 `NotificationBell.vue`（顶栏铃铛 + 未读角标，轮询 `/notifications/unread-count`）、`NotificationView.vue`（通知中心页面，展示历史通知列表，支持标记已读/全部已读）、`RecommendCard.vue`（登录后首页展示"今日推荐学习"卡片，含推荐知识点 + 预计时长 + 快速开始按钮）

- [ ] **T3-07 — 前端评估答题面板（含多维度报告）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T1-07
  - 简要说明：实现 `QuizPanel` + `QuizQuestion`（支持选择题/填空题/代码题渲染和作答）+ `EvalReport`（展示 4 维评估报告：知识掌握度进度条、学习效率评分、进步趋势折线图/雷达图、薄弱点分析列表）。提交后展示完整评估报告

- [ ] **T3-08 — 前端评估中心页面**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-07
  - 简要说明：实现 `EvalView.vue`，展示历史评估列表（时间、知识点、得分、趋势标识），点击可查看含 4 维分析的详细评估报告

- [ ] **T3-09 — 前端 MermaidDiagram 组件集成**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-07
  - 简要说明：实现 `MermaidDiagram.vue` 组件，在 `MarkdownRenderer` 中集成 Mermaid.js 渲染逻辑。检测 LLM 回复中的 Mermaid 代码块自动渲染为 SVG 图表。支持流式渲染中的 Mermaid 延迟初始化

- [ ] **T3-10 — 后端资源反馈接口**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `POST /resources/feedback`，写入 `resource_feedback` 表，反馈数据回流至画像

- [ ] **T3-11 — 阶段 3 闭环联调**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T3-01 ~ T3-10, T2-18
  - 简要说明：端到端联调完整学习闭环：简化注册 → 引导对话建立画像 → 生成路径 → 学习知识点（多资源类型）→ 触发评估 → 提交答案 → 4 维评估报告 → 画像更新 → 路径调整 → 推送重算 → 继续学习。验证推送通知：每日提醒 + 不活跃召回 + 登录推荐卡片。验证 Mermaid 图表渲染

---

### 阶段 4：VideoAgent 完善 + 体验打磨 + MVP 交付

- [ ] **T4-01 — 讯飞 TTS 集成**
  - 所属模块：AI 层 / Sidecar
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-09
  - 简要说明：集成讯飞 TTS API，实现文本转语音功能。接收 VideoAgent 生成的旁白文本，输出音频文件（WAV/MP3）。封装为 `tts_service.py` 工具函数，支持多种音色选择

- [ ] **T4-02 — Remotion 视频渲染流水线**
  - 所属模块：Sidecar
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-09, T4-01
  - 简要说明：在 Remotion sidecar 中实现完整渲染流水线：接收脚本 JSON + 音频文件 → 解析场景列表（代码动画、文字覆盖、图表场景）→ 渲染为 MP4 视频 → 上传 OSS → 返回视频 URL。实现 `/render` 正式端点，支持异步渲染 + 进度查询

- [ ] **T4-03 — VideoAgent 全流水线整合**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-09, T4-01, T4-02
  - 简要说明：整合 VideoAgent 全流水线：LLM 生成视频脚本 → 讯飞 TTS 合成语音 → 调用 Remotion sidecar 渲染视频 → 返回视频 URL。实现 `/ai/v1/resource/video` 异步端点（提交任务返回 task_id，完成后通过回调通知 Spring Boot，创建通知推送给用户）。视频时长 1-5 分钟，生成时间 < 60 秒

- [ ] **T4-04 — 前端 VideoPlayer 组件**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-07
  - 简要说明：实现 `VideoCard.vue` / 视频播放器组件。在对话页 `ResourceCard` 中嵌入视频卡片，显示缩略图 + 时长，点击展开播放器。支持"视频生成中"加载状态 + 完成通知后自动刷新

- [ ] **T4-05 — 长期记忆系统完善**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-04
  - 简要说明：完善 memory.md 读写机制：①记忆截断策略（文件超过 500 行时归档旧记录，保留摘要）②ES 向量检索优化（对话前检索 Top-5 相关记忆片段注入上下文）③记忆去重和合并（相似记忆合并为一条）④管理后台查看和导出 memory.md（运维用）

- [ ] **T4-06 — 异常处理与降级完善**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-11
  - 简要说明：补全所有异常场景的用户友好提示。LLM 超时 → "正在思考中..."重试；AI 服务不可用 → 系统提示；网络断开 → 前端检测并提示重连；SSE 中断恢复；视频生成失败 → 降级提供文字讲解；讯飞 TTS 不可用 → 降级无语音视频或纯文档

- [ ] **T4-07 — Prompt 注入防护 + 内容安全过滤**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-03
  - 简要说明：在 OrchestratorAgent 入口增加输入安全检查（正则过滤常见注入模式），敏感词过滤。实现 `check_input_safety()` 函数

- [ ] **T4-08 — 后端限流实现**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-06
  - 简要说明：基于 Redis 实现令牌桶限流。单用户对话 5 QPS，全局 AI 调用 50 QPS，视频生成限流 1 次/分钟/用户。超限返回 429 错误码

- [ ] **T4-09 — 日志与监控基础设施**
  - 所属模块：后端 + AI 层
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-03
  - 简要说明：后端配置 Logback JSON 格式日志（含 request_id / user_id / latency_ms），日志脱敏。集成 Spring Boot Actuator + Prometheus 端点。AI 层记录 9 Agent 调度链路 + LLM token 消耗 + 各 Agent 耗时

- [ ] **T4-10 — 前端响应式适配**
  - 所属模块：前端
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-07, T2-14
  - 简要说明：对话页、路径页、评估页、通知中心的移动端响应式布局适配。侧边栏在小屏下折叠为底部 Tab 导航

- [ ] **T4-11 — 性能优化**
  - 所属模块：后端 + AI 层
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-11
  - 简要说明：画像 Redis 缓存验证（命中率 >80%）；ES 行为日志异步批量写入；AI 层 Prompt 优化（减少不必要的 token 消耗）；前端路由懒加载；资源缓存命中优化（高频知识点 + 相同画像段命中缓存不调 LLM）

- [ ] **T4-12 — 端到端测试 + 回归测试**
  - 所属模块：前端 + 后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T3-11
  - 简要说明：编写核心链路的端到端测试用例（注册 → 引导对话 → 学习 → 评估 → 路径调整 → 推送通知 → 视频生成）。后端关键 Service 层单元测试。修复回归 bug

- [ ] **T4-13 — 部署脚本 + 环境配置**
  - 所属模块：DevOps
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-04
  - 简要说明：编写完整的 Docker Compose（含应用服务 + Remotion sidecar + ES + MinIO）或 Dockerfile。配置 Nginx 反向代理（静态文件 + API 转发 + Remotion 代理 + SSL）。文档化环境变量和部署步骤

---

## 3. 关键路径说明

### 主关键路径（对话 + 资源生成闭环）

```
T0-02/T0-04 → T0-05 → T1-01 → T1-06 → T1-10 → T2-03 → T2-05 → T2-11 → T2-18 → T3-01 → T3-03 → T3-11 → T4-12
  项目初始化     DB迁移    认证模块   SSE对话    联调    OrchestratorAgent  DocAgent  正式接口  联调     EvaluatorAgent  自适应   闭环联调   测试
```

### 引导对话子路径

```
T0-03 → T0-10 → T1-08 → T1-04 → T1-10
AI初始化  记忆文件  ProfileAgent引导  欢迎页面  联调
```

### VideoAgent 独立路径（可并行）

```
T0-09 → T2-09 → T4-01 → T4-02 → T4-03 → T4-04
Remotion搭建  脚本生成  讯飞TTS  Remotion渲染  全流水线  前端播放器
```

**预估关键路径总时长**：约 9-10 周（单人串行，实际可通过并行缩短至 10 周）

### 瓶颈任务（需优先投入）

| 任务 | 原因 | 建议 |
|------|------|------|
| **T2-03 OrchestratorAgent** | 所有 9 个 Agent 的路由入口，阻塞 AI 层所有后续任务 | AI 工程师最早开始，阶段 1 期间即可并行开发 |
| **T2-05 DocAgent** | 第一个证明资源生成管线的 Agent，验证成功后其余 Agent 可快速复制模式 | 优先完成，作为模板 |
| **T1-08 ProfileAgent 引导对话** | 新用户首次体验的关键环节，对话质量直接影响画像准确度 | 预留额外 1-2 天 Prompt 工程时间 |
| **T1-06 SSE 流式推送** | 技术难度较高（SseEmitter 超时管理、异常处理），阻塞前端对话页 | 后端工程师优先攻关 |
| **T3-01 EvaluatorAgent** | 闭环核心，4 维评估 + 即时联动逻辑复杂 | 需与 DocAgent 同等重视 Prompt 调优 |
| **T4-02 Remotion 渲染** | 视频渲染技术复杂度高，可能遇到 Remotion 兼容性问题 | 安排独立工程师并行攻关 |
| **T3-11 闭环联调** | 三层 + 9 Agent 协同，任何一层的 bug 都可能暴露，问题定位耗时 | 预留充足缓冲时间（3-4 天） |

---

## 4. 并行开发建议

### 4.1 并行任务分配（建议 3-4 人团队）

```
时间线    │  前端工程师              │  后端工程师              │  AI 工程师 1             │  AI/全栈工程师 2（可选）
──────────┼────────────────────────┼────────────────────────┼────────────────────────┼──────────────────────────
第 1 周   │ T0-01 前端初始化         │ T0-02 后端初始化         │ T0-03 AI 初始化          │ T0-09 Remotion sidecar
(阶段0)   │ T0-07 布局/路由框架      │ T0-04 Docker Compose    │ T0-08 Mock端点(AI侧)     │ T0-10 记忆文件工具
          │                        │ T0-05 DB迁移+ES索引     │                         │
          │                        │ T0-06 公共模块           │                         │
          │                        │ T0-08 AIClient(后端侧)  │                         │
──────────┼────────────────────────┼────────────────────────┼────────────────────────┼──────────────────────────
第 2-3 周 │ T1-02 简化注册页面       │ T1-01 认证模块           │ T1-08 ProfileAgent引导   │ T2-01 知识图谱数据
(阶段1)   │ T1-03 登录页面           │ T1-05 画像模块           │ T2-02 StateGraph骨架     │ T2-09 VideoAgent脚本
          │ T1-04 欢迎对话页面       │ T1-06 SSE对话模块        │ T2-03 OrchestratorAgent  │  (提前开始)
          │ T1-07 对话页面(流式)     │                         │  ⬅ 提前开始              │
          │ T1-09 个人中心           │                         │                         │
          │ T1-10 联调(前端侧)      │ T1-10 联调(后端侧)       │ T1-10 联调(AI侧)        │
──────────┼────────────────────────┼────────────────────────┼────────────────────────┼──────────────────────────
第 4-6 周 │ T2-14 路径页面           │ T2-12 路径模块           │ T2-04 ProfileAgent完善   │ T2-10 PathPlannerAgent
(阶段2)   │ T2-15 MindmapViewer     │ T2-13 资源管理模块       │ T2-05 DocAgent           │ T4-01 讯飞TTS集成
          │ T2-16 CodeBlock增强     │ T2-18 联调(后端侧)       │ T2-06 MindmapAgent       │  (可提前)
          │ T2-17 对话页增强         │                         │ T2-07 QuizAgent          │ T4-02 Remotion渲染
          │ T2-18 联调(前端侧)      │                         │ T2-08 CodeAgent          │  (可提前)
          │                        │                         │ T2-11 正式接口           │
          │                        │                         │ T2-18 联调(AI侧)        │
──────────┼────────────────────────┼────────────────────────┼────────────────────────┼──────────────────────────
第 7-8 周 │ T3-06 通知系统           │ T3-04 评估模块           │ T3-01 EvaluatorAgent     │ T4-03 VideoAgent整合
(阶段3)   │ T3-07 评估答题面板       │ T3-05 推送服务           │ T3-02 评估接口           │ T4-04 VideoPlayer
          │ T3-08 评估中心           │ T3-10 资源反馈接口       │ T3-03 自适应逻辑         │
          │ T3-09 Mermaid集成       │ T3-11 联调(后端侧)       │ T3-11 联调(AI侧)        │
          │ T3-11 联调(前端侧)      │                         │                         │
──────────┼────────────────────────┼────────────────────────┼────────────────────────┼──────────────────────────
第 9-10 周│ T4-04 VideoPlayer       │ T4-08 限流实现           │ T4-07 Prompt注入防护     │ T4-05 长期记忆完善
(阶段4)   │ T4-10 响应式适配         │ T4-09 日志监控           │ T4-05 长期记忆完善       │ T4-03 VideoAgent收尾
          │ T4-12 E2E测试(前端)     │ T4-11 性能优化           │ T4-11 Prompt优化         │
          │ T4-06 异常处理(前端)    │ T4-12 单元测试           │ T4-06 异常处理(AI侧)    │
          │                        │ T4-13 部署脚本           │                         │
```

> **说明**：若团队仅 3 人（无 AI/全栈工程师 2），则 VideoAgent 全部任务顺延至阶段 4，由 AI 工程师 1 在阶段 3 完成后接手。Remotion sidecar 可在阶段 0 由后端工程师兼顾搭建。

### 4.2 前后端联调时机

| 联调点 | 时机 | 范围 | 准备条件 |
|--------|------|------|---------|
| **联调 1** | 阶段 1 末（第 3 周） | 简化注册 → 引导对话 → 画像建立 → 登录 → Mock 对话流式通信 | 前后端 API 格式对齐，AI 层 ProfileAgent 引导对话 + Mock chat 就绪 |
| **联调 2** | 阶段 2 末（第 6 周） | 真实对话 + 4 类资源生成（Doc/Mindmap/Quiz/Code）+ 路径生成 | AI 层 OrchestratorAgent + 4 资源 Agent + PathPlannerAgent 就绪 |
| **联调 3** | 阶段 3 末（第 8 周） | 完整闭环（含 4 维评估 + 即时联动 + 推送 + Mermaid + 通知） | EvaluatorAgent + PushService + 通知系统就绪 |
| **联调 4** | 阶段 4 中（第 9 周） | VideoAgent 全流水线（脚本 → TTS → 渲染 → 播放） | Remotion + 讯飞 TTS + VideoAgent 整合完成 |

**联调建议**：
- 每次联调前一天，前后端开发者先用 Postman / curl 验证各自接口可用
- 联调期间三方保持在线实时沟通，快速定位问题归属层
- 联调后产出 bug 列表，按优先级在下一阶段开始前修复
- 9 Agent 联调时使用统一 `request_id` 串联追踪，快速定位是哪个 Agent 出错

### 4.3 AI 层 Mock 策略

在 AI 层真实 Agent 未完成前，提供以下 Mock 能力让前后端先行开发：

**Mock 端点覆盖**：

```python
# ai-service/mock.py — 阶段 0-1 使用
# 以下端点均提供 Mock 实现：
# /ai/v1/chat           → 回显用户消息的模拟流式输出
# /ai/v1/chat/welcome   → 模拟 5 轮引导对话（固定问答脚本）
# /ai/v1/resource/doc   → 模拟流式 Markdown 文档输出
# /ai/v1/resource/mindmap → 返回固定思维导图 JSON
# /ai/v1/resource/quiz  → 返回 3 道模拟题目
# /ai/v1/resource/code  → 返回固定代码示例
# /ai/v1/resource/video → 返回 mock task_id
# /ai/v1/path/generate  → 返回固定路径节点列表
# /ai/v1/path/recommend → 返回固定推荐节点
# /ai/v1/evaluate/generate → 返回模拟评估题目
# /ai/v1/evaluate/analyze  → 返回模拟 4 维评估报告
# /ai/v1/profile/analyze   → 返回固定画像分析结果
# /ai/v1/profile/extract   → 返回固定画像特征提取结果
```

**Mock 使用阶段**：

| 阶段 | AI 层状态 | 前后端使用方式 |
|------|----------|-------------|
| 阶段 0 | Mock 全部接口 | 前后端基于 Mock 开发和联调 |
| 阶段 1 | ProfileAgent 引导对话就绪，其余 Mock | 引导对话用真实 Agent，chat 仍 Mock |
| 阶段 2 前半 | OrchestratorAgent + 部分资源 Agent 就绪 | 逐个替换为真实 Agent，灰度切换 |
| 阶段 2 后半 | 核心 Agent（Doc/Mindmap/Quiz/Code/Path）就绪 | 切换到正式接口，关闭对应 Mock |
| 阶段 3 | EvaluatorAgent + 推送逻辑就绪 | 评估相关 Mock 关闭 |
| 阶段 4 | VideoAgent 全流水线就绪 | 全部 Mock 关闭 |

---

## 5. 风险提示

### 风险 1：LLM 输出质量不稳定

**表现**：资源讲解出现事实错误、评估题目答案有误、意图识别漂移、画像提取不准确。

**概率**：高

**规避建议**：
- Prompt 模板化 + 版本管理，每次调整记录变更原因
- 关键输出（评估题目正确答案、画像特征提取）使用结构化输出（JSON Mode / Function Calling）约束格式
- 建立人工抽检机制：MVP 阶段每周抽检 50 条生成内容，统计事实性错误率
- 5 个资源 Agent 的 Prompt 开发各预留额外 1-2 天调优时间

### 风险 2：SSE 流式通信稳定性

**表现**：长连接断开、消息丢失、浏览器兼容性问题、SSE 超时。

**概率**：中

**规避建议**：
- `SseEmitter` 设置合理超时（60 秒），前端检测到 `onerror` 后自动重连
- 每条消息携带 `message_id`，前端可根据最后收到的 ID 请求补发
- 后端增加心跳机制：每 15 秒发送 `data: {"type":"heartbeat"}\n\n`
- 早期（阶段 1）就要验证流式链路，不要等到阶段 2 才发现问题

### 风险 3：LLM API 成本超预期

**表现**：开发调试阶段频繁调用 LLM API，产生大量费用；9 个 Agent 意味着更多调用链路。

**概率**：中

**规避建议**：
- 开发环境设置 API 日调用量上限（如 1000 次/天），超限自动降级到 Mock
- 实现资源缓存（ES `zhiban-resource-cache`），高频知识点命中缓存后不调 LLM
- 监控每次调用的 token 消耗，Prompt 超过 2000 token 的要优化精简
- 非核心场景（闲聊、进度查询）使用更低成本的模型
- OrchestratorAgent 路由决策尽量用轻量模型或规则引擎辅助

> ⚠️ **假设**：PRD 未明确 LLM API 预算。建议 MVP 阶段预留 $500-1000/月 用于开发 + 测试 + 小规模用户验证。

### 风险 4：VideoAgent 复杂度（v2.0 新增）

**表现**：Remotion 渲染环境搭建困难、视频生成耗时超预期、讯飞 TTS API 稳定性不足、视频质量不达标。

**概率**：高

**规避建议**：
- VideoAgent 安排在独立并行路径上开发，不阻塞其他 Agent
- Remotion sidecar 阶段 0 即搭建好，尽早验证渲染管线可行性
- 讯飞 TTS 在阶段 2 即开始集成测试，验证 API 额度、延迟、音质
- 设定降级方案：视频生成失败 → 降级为纯文档 + 代码示例
- 预留视频模板库：高频知识点预渲染模板，减少实时渲染压力
- 若 3 人团队无法并行，VideoAgent 可延后到 MVP 后的 v2.1 迭代

### 风险 5：讯飞 TTS API 稳定性和成本（v2.0 新增）

**表现**：TTS API 调用失败、音质不稳定、API 额度耗尽、成本高于预期。

**概率**：中

**规避建议**：
- 确认讯飞 TTS API 的免费额度和付费方案，预留月度预算
- 实现 TTS 音频缓存：相同文本不重复调用 API
- 降级方案：TTS 不可用时生成无语音的纯动画视频
- 考虑备选 TTS 方案（如 Azure TTS、Edge TTS 开源方案）

### 风险 6：长期记忆 MD 文件增长（v2.0 新增）

**表现**：memory.md 文件随着用户使用持续增长，读取和解析性能下降；文件过大影响 LLM 上下文窗口。

**概率**：中

**规避建议**：
- 实现记忆截断策略：文件超过 500 行时归档旧记录到 `memory_archive/` 目录，主文件保留最近 3 个月的记忆
- 定期对记忆进行摘要压缩（用 LLM 将多条相似记忆合并为一条摘要）
- 对话时优先使用 ES 向量检索获取相关记忆（Top-5），而非全量读取 MD 文件
- 监控每个用户的 memory.md 文件大小，设置告警阈值

### 风险 7：9 Agent 协调复杂度（v2.0 新增）

**表现**：Agent 间调用链路变长、故障传播范围扩大、调试定位困难、集成测试工作量倍增。

**概率**：高

**规避建议**：
- 统一 `request_id` 贯穿整条调用链，日志中记录每个 Agent 的输入/输出/耗时
- 实现 Agent 级别的熔断和降级：单个 Agent 异常不影响整体对话
- OrchestratorAgent 路由决策要明确，避免不必要的 Agent 调用
- 每个 Agent 独立可测试：编写 Agent 级单元测试，用 Mock 画像 + Mock 知识点验证生成质量
- 联调时按 Agent 逐个替换（灰度接入），不要一次性全部切换
- 建立 Agent 调度链路可视化监控（可复用 LangSmith 或自建 trace 服务）

### 风险 8：知识图谱质量影响路径规划

**表现**：知识点划分粒度不合适、前置依赖关系错误，导致路径不合理。

**概率**：中

**规避建议**：
- 首发科目（数据结构与算法）参考 2-3 本主流教材交叉验证知识点划分
- 知识图谱 JSON 格式化存储，支持快速修改和热加载（无需重启服务）
- 邀请 3-5 名目标用户做路径体验测试，收集反馈后调整
- PathPlannerAgent 生成路径时做合法性校验（不出现循环依赖）

### 风险 9：三层 + Sidecar 联调沟通成本高

**表现**：前端/后端/AI 层/Remotion sidecar 接口格式不一致、字段命名混乱、联调时问题定位困难。

**概率**：高

**规避建议**：
- **阶段 0 就对齐接口契约**：基于 TDD 中的 API 接口清单生成 OpenAPI Spec 文档，四方以此为准
- AI 层对 Spring Boot 的响应也要遵循约定格式（TDD 2.2.4），不随意变更字段
- Remotion sidecar 的 `/render` 接口也要提前约定请求/响应格式
- 每次联调建立共享日志查看通道：统一 `request_id` 串联追踪
- 联调期间每日 15 分钟 Stand-up，快速同步阻塞问题

---

## 附录：任务工作量统计

| 阶段 | 任务数 | 小任务 | 中任务 | 大任务 | 预估总人天 |
|------|--------|--------|--------|--------|-----------|
| 阶段 0 | 10 | 3 | 7 | 0 | ~15 人天 |
| 阶段 1 | 10 | 1 | 4 | 5 | ~28 人天 |
| 阶段 2 | 18 | 0 | 12 | 6 | ~45 人天 |
| 阶段 3 | 11 | 1 | 5 | 5 | ~32 人天 |
| 阶段 4 | 13 | 0 | 8 | 5 | ~30 人天 |
| **合计** | **62** | **5** | **36** | **21** | **~150 人天** |

> ⚠️ **假设**：按 3-4 人团队并行开发，预估总历时约 10 周。  
> - **3 人团队**（前端 1 + 后端 1 + AI 1）：VideoAgent 延后，约 10-11 周  
> - **4 人团队**（前端 1 + 后端 1 + AI 1 + AI/全栈 1）：VideoAgent 并行，约 10 周  
> - 关键路径上的 AI 层任务是瓶颈（9 Agent 开发量大），增加 AI 工程师可显著缩短工期
