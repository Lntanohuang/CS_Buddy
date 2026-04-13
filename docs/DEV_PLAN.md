# 智伴（ZhiBan）开发顺序计划

> **文档版本**：v1.0  
> **创建日期**：2026-04-13  
> **作者**：技术项目负责人  
> **关联文档**：[PRD](./PRD.md) · [TDD](./TDD.md)

---

## 1. 开发阶段划分

### 总览

```
阶段0          阶段1            阶段2             阶段3            阶段4
工程脚手架 ──▶ 用户系统+对话骨架 ──▶ AI Agent闭环 ──▶ 评估+自适应 ──▶ 体验增强
(1 周)         (2 周)             (2.5 周)          (2 周)          (1.5 周)
               可验证：注册登录     可验证：对话+      可验证：完整      可验证：
               + 对话收发流式文本   资源生成+路径规划   学习闭环         MVP可交付
```

---

### 阶段 0：工程脚手架与基础设施（第 1 周）

**目标**：搭建三层项目骨架、开发环境和 CI 流程，各层可独立启动并互相通信。

**阶段结束可验证**：
- 前端 `npm run dev` 可访问空白页面
- 后端 `mvn spring-boot:run` 可启动，`GET /actuator/health` 返回 200
- AI 层 `uvicorn main:app` 可启动，`GET /health` 返回 200
- 后端可成功调用 AI 层的 health 端点
- Docker Compose 一键拉起 MySQL + Redis + MongoDB
- 数据库表已通过 Flyway 迁移创建

**涉及模块**：前端 / 后端 / AI 层 / DevOps

---

### 阶段 1：用户系统 + 对话骨架（第 2-3 周）

**目标**：完成用户注册登录全流程，搭建对话页面 + SSE 流式通信链路。此阶段 AI 层使用 Mock 回复（回显用户消息或返回固定文本），重点打通前端 → Spring Boot → AI 层的完整数据链路。

**阶段结束可验证**：
- 用户可完成注册（含偏好问卷）→ 登录 → 进入主界面
- 在对话页面发送消息，收到流式 Mock 回复（逐字出现）
- JWT 鉴权工作正常（过期跳转登录、Refresh Token 刷新）
- 用户画像通过 API 可查看和修改

**涉及模块**：前端 / 后端 / AI 层（Mock）

---

### 阶段 2：AI Agent 核心能力（第 4-5 周）

**目标**：实现 OrchestratorAgent 意图识别、ProfileAgent 画像分析、ResourceGenAgent 资源生成、PathPlannerAgent 路径规划。用户可通过对话获得个性化学习资源和学习路径。

**阶段结束可验证**：
- 发送"帮我讲讲快速排序"，系统返回个性化的知识讲解（流式）
- 发送"我要学数据结构"，系统生成完整学习路径
- 不同画像的用户对同一知识点获得的资源存在明显差异
- 意图识别能正确区分学习请求 / 路径查询 / 闲聊

**涉及模块**：AI 层（核心）/ 后端 / 前端

---

### 阶段 3：评估系统 + 自适应闭环（第 6-7 周）

**目标**：实现 EvaluatorAgent，完成"学习 → 评估 → 画像更新 → 路径调整"完整闭环。这是 MVP 的核心价值验证环节。

**阶段结束可验证**：
- 学完一个知识点后，系统自动生成 mini quiz（3-5 题）
- 提交答案后，系统返回评分 + 错误分析 + 推荐复习知识点
- 评估结果自动更新画像中的知识掌握度
- 掌握度低的知识点被自动插入路径中进行补强
- 完整学习闭环可跑通：注册 → 生成路径 → 学习 → 评估 → 路径调整

**涉及模块**：AI 层 / 后端 / 前端

---

### 阶段 4：体验打磨 + MVP 交付准备（第 8-9 周）

**目标**：补全边缘场景、异常处理、性能优化，达到可交付的 MVP 质量标准。

**阶段结束可验证**：
- 所有异常场景有友好提示（LLM 超时、网络断开等）
- 对话首 token 延迟 < 1.5 秒
- 500 并发压测通过
- 资源反馈功能可用
- 前端移动端基本可用（响应式）
- 端到端测试覆盖核心链路

**涉及模块**：前端 / 后端 / AI 层 / DevOps

---

## 2. 详细任务清单

### 阶段 0：工程脚手架与基础设施

- [ ] **T0-01 — 初始化 Vue 3 前端项目**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：`npm create vite@latest` 创建项目，配置 TypeScript、ESLint、Prettier，安装 Vue Router / Pinia / Axios / Element Plus

- [ ] **T0-02 — 初始化 Spring Boot 后端项目**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：Spring Initializr 创建项目（Web、Security、MyBatis-Plus、Redis、MongoDB），配置 `application.yml` 多环境，建立包结构

- [ ] **T0-03 — 初始化 Python AI 服务项目**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：创建 FastAPI 项目，安装 LangChain / LangGraph 依赖，配置 `.env`，实现 `/health` 端点

- [ ] **T0-04 — Docker Compose 基础设施配置**
  - 所属模块：DevOps
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：无
  - 简要说明：编写 docker-compose.yml，包含 MySQL 8.0 + Redis 7 + MongoDB 7，配置数据卷持久化

- [ ] **T0-05 — 数据库表结构迁移脚本**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-04
  - 简要说明：按 TDD 3.1 节编写全部 9 张 MySQL 表的 Flyway 迁移 SQL，创建 MongoDB 的索引脚本

- [ ] **T0-06 — 后端公共模块搭建**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02
  - 简要说明：实现 `ApiResult` 统一响应封装、`ErrorCode` 错误码枚举、`GlobalExceptionHandler` 全局异常处理、`CorsConfig` 跨域配置

- [ ] **T0-07 — 前端基础布局与路由框架**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-01
  - 简要说明：实现 `AppLayout` / `Sidebar` / `TopNav` 布局组件，配置 Vue Router（含导航守卫），搭建 `api/http.ts` Axios 封装

- [ ] **T0-08 — 后端 AIClientService 骨架 + AI 层 Mock 端点**
  - 所属模块：后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-03
  - 简要说明：后端实现 `AIClientService`（`callSync` + `callStream`），AI 层实现 `/ai/v1/chat` Mock 端点（接收请求，返回固定 SSE 流），验证双端通信链路

---

### 阶段 1：用户系统 + 对话骨架

- [ ] **T1-01 — 后端认证模块（注册/登录/Token 刷新）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T0-06
  - 简要说明：实现 `JwtUtil` / `SecurityConfig` / `AuthController` / `AuthService`。注册接口接收 survey 字段并写入 `user_profile` 表。实现 JWT 签发、验证、Refresh Token（存 Redis）刷新逻辑

- [ ] **T1-02 — 前端注册页面（含偏好问卷）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-07
  - 简要说明：实现 `RegisterView.vue`，3 步流程（基础信息 → 偏好问卷 → 完成）。问卷支持跳过。调用 `POST /api/v1/auth/register`

- [ ] **T1-03 — 前端登录页面 + Token 管理**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-07
  - 简要说明：实现 `LoginView.vue` + `useAuthStore`。Token 存 localStorage，Axios 拦截器自动附加 Bearer Token，401 时自动刷新

- [ ] **T1-04 — 后端画像模块（CRUD API）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `ProfileController` / `ProfileService` / `UserProfileMapper`。支持 `GET /profile`（Redis 缓存 + MySQL 回源）和 `PATCH /profile`（更新 + 清除缓存）

- [ ] **T1-05 — 后端对话模块（会话管理 + SSE 流式推送）**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T0-08, T1-01
  - 简要说明：实现 `ChatController`（`POST /chat/sessions`, `GET /chat/sessions`, `POST /chat/stream`）。`/chat/stream` 使用 `SseEmitter`，内部调用 `AIClientService.callStream()` 转发 AI 层流式响应。消息持久化到 `chat_session` + `chat_message` 表

- [ ] **T1-06 — 前端对话页面（消息列表 + 流式渲染）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-07, T1-03
  - 简要说明：实现 `ChatView.vue` + `ChatMessageList` + `ChatInput` + `MessageBubble`。实现 `useSSE` composable 接收 SSE 流，逐 token 追加渲染。集成 `MarkdownRenderer`（markdown-it + highlight.js）

- [ ] **T1-07 — 前端个人中心页面（画像查看/修改）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-07, T1-03, T1-04
  - 简要说明：实现 `ProfileView.vue`，展示画像各维度数据（表格/标签形式），支持手动修改水平等级和学习偏好

- [ ] **T1-08 — 前后端联调：注册 → 登录 → 对话流式通信**
  - 所属模块：前端 + 后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-01 ~ T1-06
  - 简要说明：端到端联调，修复接口参数/格式不一致问题，确保注册 → 登录 → 进入对话页 → 发送消息 → 收到 Mock 流式回复全链路跑通

---

### 阶段 2：AI Agent 核心能力

- [ ] **T2-01 — 知识图谱数据准备**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-03
  - 简要说明：按 TDD 约定，为首发科目（数据结构与算法）编写知识图谱 JSON。定义知识点 ID、标题、前置依赖、难度。约 20-30 个知识点节点

> ⚠️ **假设**：知识图谱由开发团队根据主流教材自行整理。PRD A3 项待确认是否有教研团队参与。

- [ ] **T2-02 — LangGraph StateGraph 定义与工作流骨架**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-03
  - 简要说明：按 TDD 2.3.1 实现 `ZhiBanState` TypedDict，按 2.3.4 搭建 `build_chat_graph()` 工作流骨架（节点占位 + 条件边路由），实现 `with_retry` 重试装饰器

- [ ] **T2-03 — OrchestratorAgent 实现（意图识别 + 路由）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02
  - 简要说明：实现 `orchestrator_node`，使用 LLM 进行意图分类（learn / path_query / evaluate / chitchat / clarify 等），输出 intent + confidence。实现 `route_by_intent` 条件路由函数。闲聊意图由 Orchestrator 直接生成回复

- [ ] **T2-04 — ProfileAgent 实现（画像读取 + 分析更新）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-02
  - 简要说明：实现 `profile_fetch_node`（从 Spring Boot 获取画像 JSON 写入 State）和 `profile_update_node`（分析评估结果，计算新的 mastery 值，回写 Spring Boot）

- [ ] **T2-05 — ResourceGenAgent 实现（个性化资源生成）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `resource_gen_node`。根据画像中的水平、偏好风格、style_weights 动态构建 Prompt，调用 LLM 流式生成 Markdown 资源。输出包括资源内容和元数据（难度、时长、关联知识点）

- [ ] **T2-06 — PathPlannerAgent 实现（路径生成 + 调整）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-01, T2-02, T2-04
  - 简要说明：实现 `path_planner_node`。加载知识图谱 JSON，结合用户画像（已掌握知识点跳过），使用 LLM 推理最优学习顺序，生成有序路径节点列表

- [ ] **T2-07 — AI 层 FastAPI 正式接口实现**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-03 ~ T2-06
  - 简要说明：将 Mock 端点替换为真实 Agent 调用。实现 `/ai/v1/chat`（流式）、`/ai/v1/path/generate`、`/ai/v1/resource/generate`（流式）、`/ai/v1/profile/analyze` 等正式接口

- [ ] **T2-08 — 后端学习路径模块**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `PathController` / `PathService`。`POST /paths` 调用 AI 层生成路径并持久化到 `learning_path` + `path_node` 表。`PATCH /paths/{id}/nodes/{id}` 更新节点状态

- [ ] **T2-09 — 前端学习路径页面**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-03, T1-06
  - 简要说明：实现 `PathView.vue` + `PathTimeline` + `PathNodeCard`。时间线展示路径节点，标记已完成/进行中/待学习状态，点击节点可跳转到对话页面发起该知识点的学习

- [ ] **T2-10 — 前端对话页增强（资源卡片 + 路径引导）**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-06
  - 简要说明：解析 SSE 中的 `resource_card` / `metadata` 类型事件，在对话中嵌入 `ResourceCard` 组件展示资源元数据（难度、时长），添加 `FeedbackButtons`（有用/没用）

- [ ] **T2-11 — 阶段 2 全链路联调**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-07 ~ T2-10
  - 简要说明：端到端联调核心对话场景。发送学习请求 → 意图识别 → 画像获取 → 路径生成 → 资源生成，全链路流式跑通。修复数据格式、超时、异常处理问题

---

### 阶段 3：评估系统 + 自适应闭环

- [ ] **T3-01 — EvaluatorAgent 实现（题目生成 + 答案分析）**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T2-02, T2-04
  - 简要说明：实现 `evaluator_gen_node`（根据画像和知识点生成 3-5 道评估题目，支持选择题/填空题）和 `evaluator_analyze_node`（对比答案、生成错误分析、计算 mastery、输出路径调整建议）

- [ ] **T3-02 — AI 层评估接口实现**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-01
  - 简要说明：实现 `/ai/v1/evaluate/generate` 和 `/ai/v1/evaluate/analyze` 正式接口。评估分析接口需调用 ProfileAgent 更新画像并返回路径调整建议

- [ ] **T3-03 — AI 层自适应路径调整逻辑**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-06, T3-01
  - 简要说明：在工作流中实现 `route_after_eval` 条件边。评估后根据 mastery 阈值（<0.4 回退 / 0.4-0.7 补强 / ≥0.7 推进），调用 PathPlannerAgent 执行路径插入/调整

- [ ] **T3-04 — 后端评估模块**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `EvalController` / `EvalService`。`POST /evaluations` 调用 AI 层生成题目并持久化。`POST /evaluations/{id}/submit` 调用 AI 层分析，更新 `evaluation` + `eval_question` 表，联动更新 `user_profile.knowledge_mastery` 并清除 Redis 画像缓存

- [ ] **T3-05 — 后端资源反馈接口**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：小（<1天）
  - 前置依赖：T0-05, T1-01
  - 简要说明：实现 `POST /resources/feedback`，写入 `resource_feedback` 表

- [ ] **T3-06 — 前端评估答题面板**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T1-06
  - 简要说明：实现 `QuizPanel` + `QuizQuestion` + `EvalReport` 组件。支持选择题（单选）和填空题的渲染和作答。提交后展示评估报告（得分、错题分析、推荐复习点）

- [ ] **T3-07 — 前端评估中心页面**
  - 所属模块：前端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-06
  - 简要说明：实现 `EvalView.vue`，展示历史评估列表（时间、知识点、得分），点击可查看详细评估报告

- [ ] **T3-08 — 阶段 3 闭环联调**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T3-01 ~ T3-07, T2-11
  - 简要说明：端到端联调完整学习闭环：注册 → 生成路径 → 学习知识点 → 触发评估 → 提交答案 → 画像更新 → 路径调整 → 继续学习。重点验证自适应调整逻辑的正确性

---

### 阶段 4：体验打磨 + MVP 交付准备

- [ ] **T4-01 — 异常处理与降级完善**
  - 所属模块：前端 + 后端 + AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-08
  - 简要说明：补全所有异常场景的用户友好提示。LLM 超时 → "正在思考中..."重试；AI 服务不可用 → 系统提示；网络断开 → 前端检测并提示重连；SSE 中断恢复

- [ ] **T4-02 — Prompt 注入防护 + 内容安全过滤**
  - 所属模块：AI 层
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T2-03
  - 简要说明：在 OrchestratorAgent 入口增加输入安全检查（正则过滤常见注入模式），敏感词过滤。按 TDD 6.3 节实现 `check_input_safety()`

- [ ] **T4-03 — 后端限流实现**
  - 所属模块：后端
  - 优先级：P0
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-06
  - 简要说明：基于 Redis 实现令牌桶限流。单用户对话 5 QPS，全局 AI 调用 50 QPS。超限返回 429 错误码

- [ ] **T4-04 — 日志与监控基础设施**
  - 所属模块：后端 + AI 层
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-02, T0-03
  - 简要说明：后端配置 Logback JSON 格式日志（含 request_id / user_id / latency_ms），日志脱敏（不记录用户原始消息）。集成 Spring Boot Actuator + Prometheus 端点。AI 层记录 Agent 调度链 + LLM token 消耗

- [ ] **T4-05 — 前端响应式适配**
  - 所属模块：前端
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T1-06, T2-09
  - 简要说明：对话页、路径页、评估页的移动端响应式布局适配。侧边栏在小屏下折叠为底部 Tab 导航

- [ ] **T4-06 — 性能优化**
  - 所属模块：后端 + AI 层
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T3-08
  - 简要说明：画像 Redis 缓存验证（命中率 >80%）；MongoDB 行为日志异步批量写入；AI 层 Prompt 优化（减少不必要的 token 消耗）；前端路由懒加载

- [ ] **T4-07 — 端到端测试 + 回归测试**
  - 所属模块：前端 + 后端
  - 优先级：P0
  - 预估工作量：大（>3天）
  - 前置依赖：T3-08
  - 简要说明：编写核心链路的端到端测试用例（注册 → 学习 → 评估 → 路径调整）。后端关键 Service 层单元测试。修复回归 bug

- [ ] **T4-08 — 部署脚本 + 环境配置**
  - 所属模块：DevOps
  - 优先级：P1
  - 预估工作量：中（1~3天）
  - 前置依赖：T0-04
  - 简要说明：编写完整的 Docker Compose（含应用服务）或 Dockerfile。配置 Nginx 反向代理（静态文件 + API 转发 + SSL）。文档化环境变量和部署步骤

---

## 3. 关键路径说明

### 最长依赖链（关键路径）

```
T0-02/T0-04 → T0-05 → T1-01 → T1-05 → T1-08 → T2-03 → T2-05 → T2-07 → T2-11 → T3-01 → T3-03 → T3-08 → T4-07
  项目初始化     DB迁移    认证模块    SSE对话    联调    意图识别  资源生成  正式接口  联调     评估Agent  自适应   闭环联调   测试
```

**预估关键路径总时长**：约 8-9 周（单人串行，实际可通过并行缩短）

### 瓶颈任务（需优先投入）

| 任务 | 原因 | 建议 |
|------|------|------|
| **T2-03 OrchestratorAgent** | 所有 Agent 的路由入口，阻塞 AI 层所有后续任务 | AI 工程师最早开始，阶段 1 期间即可并行开发 |
| **T2-05 ResourceGenAgent** | 核心用户体验（资源生成质量 = 产品价值），需反复调优 Prompt | 预留额外 1-2 天 Prompt 工程时间 |
| **T1-05 SSE 流式推送** | 技术难度较高（SseEmitter 超时管理、异常处理），阻塞前端对话页 | 后端工程师优先攻关 |
| **T3-01 EvaluatorAgent** | 闭环核心，题目质量和分析准确性直接影响自适应效果 | 需与 T2-05 同等重视 Prompt 调优 |
| **T3-08 闭环联调** | 三层协同，任何一层的 bug 都可能暴露，问题定位耗时 | 预留充足缓冲时间（2-3 天） |

---

## 4. 并行开发建议

### 4.1 并行任务分配

```
时间线    │  前端工程师              │  后端工程师            │  AI 工程师
──────────┼────────────────────────┼──────────────────────┼────────────────────────
第 1 周   │ T0-01 前端初始化         │ T0-02 后端初始化       │ T0-03 AI 初始化
(阶段0)   │ T0-07 布局/路由框架      │ T0-04 Docker Compose  │ T0-08 Mock端点(AI侧)
          │                        │ T0-05 DB迁移脚本      │
          │                        │ T0-06 公共模块        │
          │                        │ T0-08 AIClient(后端侧)│
──────────┼────────────────────────┼──────────────────────┼────────────────────────
第 2-3 周 │ T1-02 注册页面           │ T1-01 认证模块        │ T2-01 知识图谱数据
(阶段1)   │ T1-03 登录页面           │ T1-04 画像模块        │ T2-02 StateGraph骨架
          │ T1-06 对话页面(流式)     │ T1-05 SSE对话模块     │ T2-03 OrchestratorAgent ⬅ 提前开始
          │ T1-07 个人中心           │                      │
          │ T1-08 联调(前端侧)      │ T1-08 联调(后端侧)    │
──────────┼────────────────────────┼──────────────────────┼────────────────────────
第 4-5 周 │ T2-09 路径页面           │ T2-08 路径模块        │ T2-04 ProfileAgent
(阶段2)   │ T2-10 对话页增强         │ T2-11 联调(后端侧)    │ T2-05 ResourceGenAgent
          │ T2-11 联调(前端侧)      │                      │ T2-06 PathPlannerAgent
          │                        │                      │ T2-07 正式接口
          │                        │                      │ T2-11 联调(AI侧)
──────────┼────────────────────────┼──────────────────────┼────────────────────────
第 6-7 周 │ T3-06 答题面板           │ T3-04 评估模块        │ T3-01 EvaluatorAgent
(阶段3)   │ T3-07 评估中心           │ T3-05 资源反馈接口    │ T3-02 评估接口
          │ T3-08 联调(前端侧)      │ T3-08 联调(后端侧)    │ T3-03 自适应逻辑
          │                        │                      │ T3-08 联调(AI侧)
──────────┼────────────────────────┼──────────────────────┼────────────────────────
第 8-9 周 │ T4-05 响应式适配         │ T4-03 限流实现        │ T4-02 Prompt注入防护
(阶段4)   │ T4-07 E2E测试(前端)     │ T4-04 日志监控        │ T4-04 日志(AI侧)
          │ T4-01 异常处理(前端)    │ T4-06 性能优化        │ T4-06 Prompt优化
          │                        │ T4-07 单元测试        │ T4-01 异常处理(AI侧)
          │                        │ T4-08 部署脚本        │
```

### 4.2 前后端联调时机

| 联调点 | 时机 | 范围 | 准备条件 |
|--------|------|------|---------|
| **联调 1** | 阶段 1 末（第 3 周） | 注册 → 登录 → Mock 对话流式通信 | 前后端 API 格式对齐，AI 层 Mock 就绪 |
| **联调 2** | 阶段 2 末（第 5 周） | 真实对话 + 路径生成 + 资源生成 | AI 层 4 个 Agent 就绪，正式接口上线 |
| **联调 3** | 阶段 3 末（第 7 周） | 完整闭环（含评估 + 自适应） | EvaluatorAgent 就绪，路径调整逻辑完成 |

**联调建议**：
- 每次联调前一天，前后端开发者先用 Postman / curl 验证各自接口可用
- 联调期间三方保持在线实时沟通，快速定位问题归属层
- 联调后产出 bug 列表，按优先级在下一阶段开始前修复

### 4.3 AI 层 Mock 策略

在 AI 层真实 Agent 未完成前，提供以下 Mock 能力让前后端先行开发：

**Mock 端点实现**：

```python
# ai-service/mock.py — 阶段 0-1 使用
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json, asyncio

app = FastAPI()

async def mock_stream(message: str):
    """模拟流式输出"""
    reply = f"[Mock] 收到你的消息：{message}。这是一段模拟的学习内容回复，用于前端开发调试。"
    for char in reply:
        yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"
        await asyncio.sleep(0.05)
    yield f"data: {json.dumps({'type': 'done', 'message_id': 'mock_msg_001'})}\n\n"

@app.post("/ai/v1/chat")
async def mock_chat(request: dict):
    return StreamingResponse(
        mock_stream(request.get("payload", {}).get("message", "")),
        media_type="text/event-stream"
    )

@app.post("/ai/v1/path/generate")
async def mock_path(request: dict):
    return {
        "status": "success",
        "agent": "PathPlannerAgent",
        "data": {
            "nodes": [
                {"node_id": "node_001", "title": "数组基础", "knowledge_point": "array",
                 "order": 1, "difficulty": "BEGINNER", "est_minutes": 90, "prerequisites": []},
                {"node_id": "node_002", "title": "链表", "knowledge_point": "linked_list",
                 "order": 2, "difficulty": "BEGINNER", "est_minutes": 120, "prerequisites": ["node_001"]},
            ]
        }
    }

@app.post("/ai/v1/evaluate/generate")
async def mock_eval(request: dict):
    return {
        "status": "success",
        "agent": "EvaluatorAgent",
        "data": {
            "questions": [
                {"question_id": "q_mock_001", "type": "SINGLE_CHOICE",
                 "content": "[Mock] 数组的随机访问时间复杂度是？",
                 "options": [{"key": "A", "value": "O(1)"}, {"key": "B", "value": "O(n)"}],
                 "correct_answer": "A",
                 "explanation": "数组支持通过下标直接访问元素。"}
            ]
        }
    }
```

**Mock 使用阶段**：

| 阶段 | AI 层状态 | 前后端使用方式 |
|------|----------|-------------|
| 阶段 0-1 | Mock 全部接口 | 前后端基于 Mock 开发和联调 |
| 阶段 2 前半 | OrchestratorAgent 就绪，其余 Agent 部分 Mock | 逐个替换为真实 Agent，灰度切换 |
| 阶段 2 后半 | 全部 Agent 就绪 | 切换到正式接口，关闭 Mock |

---

## 5. 风险提示

### 风险 1：LLM 输出质量不稳定

**表现**：资源讲解出现事实错误、评估题目答案有误、意图识别漂移。

**概率**：高

**规避建议**：
- Prompt 模板化 + 版本管理，每次调整记录变更原因
- 关键输出（评估题目正确答案）使用结构化输出（JSON Mode / Function Calling）约束格式
- 建立人工抽检机制：MVP 阶段每周抽检 50 条生成内容，统计事实性错误率
- ResourceGenAgent 和 EvaluatorAgent 的 Prompt 开发预留额外 2 天调优时间

### 风险 2：SSE 流式通信稳定性

**表现**：长连接断开、消息丢失、浏览器兼容性问题、SSE 超时。

**概率**：中

**规避建议**：
- `SseEmitter` 设置合理超时（60 秒），前端检测到 `onerror` 后自动重连
- 每条消息携带 `message_id`，前端可根据最后收到的 ID 请求补发
- 后端增加心跳机制：每 15 秒发送 `data: {"type":"heartbeat"}\n\n`
- 早期（阶段 1）就要验证流式链路，不要等到阶段 2 才发现问题

### 风险 3：LLM API 成本超预期

**表现**：开发调试阶段频繁调用 LLM API，产生大量费用；或用户增长后每用户成本过高。

**概率**：中

**规避建议**：
- 开发环境设置 API 日调用量上限（如 1000 次/天），超限自动降级到 Mock
- 按 TDD 设计实现资源缓存（MongoDB `resource_cache`），高频知识点命中缓存后不调 LLM
- 监控每次调用的 token 消耗，Prompt 超过 2000 token 的要优化精简
- 考虑非核心场景（闲聊、进度查询）使用更低成本的模型

> ⚠️ **假设**：PRD 未明确 LLM API 预算。建议 MVP 阶段预留 $500-1000/月 用于开发 + 测试 + 小规模用户验证。

### 风险 4：知识图谱质量影响路径规划

**表现**：知识点划分粒度不合适、前置依赖关系错误，导致路径不合理。

**概率**：中

**规避建议**：
- 首发科目（数据结构与算法）参考 2-3 本主流教材交叉验证知识点划分
- 知识图谱 JSON 格式化存储，支持快速修改和热加载（无需重启服务）
- 邀请 3-5 名目标用户做路径体验测试，收集反馈后调整
- PathPlannerAgent 生成路径时做合法性校验（不出现循环依赖）

### 风险 5：三层联调沟通成本高

**表现**：前端/后端/AI 层接口格式不一致、字段命名混乱、联调时问题定位困难。

**概率**：高

**规避建议**：
- **阶段 0 就对齐接口契约**：基于 TDD 中的 API 接口清单生成 OpenAPI Spec 文档，三方以此为准
- AI 层对 Spring Boot 的响应也要遵循约定格式（TDD 2.2.3），不随意变更字段
- 每次联调建立共享日志查看通道：前端看 Console、后端看 Spring Boot 日志、AI 层看 FastAPI 日志，统一 `request_id` 串联追踪
- 联调期间每日 15 分钟 Stand-up，快速同步阻塞问题

---

## 附录：任务工作量统计

| 阶段 | 任务数 | 小任务 | 中任务 | 大任务 | 预估总人天 |
|------|--------|--------|--------|--------|-----------|
| 阶段 0 | 8 | 3 | 5 | 0 | ~12 人天 |
| 阶段 1 | 8 | 0 | 5 | 3 | ~20 人天 |
| 阶段 2 | 11 | 0 | 7 | 4 | ~30 人天 |
| 阶段 3 | 8 | 1 | 3 | 4 | ~24 人天 |
| 阶段 4 | 8 | 0 | 6 | 2 | ~20 人天 |
| **合计** | **43** | **4** | **26** | **13** | **~106 人天** |

> ⚠️ **假设**：按 3 人团队（前端 1 + 后端 1 + AI 1）并行开发，预估总历时约 8-9 周。若团队规模不同，关键路径上的 AI 层任务是瓶颈，增加 AI 工程师可显著缩短工期。
