# 前端重构计划

> 基于 PRD v2.0 / TDD v2.0 / 完整代码审计

---

## 1. 已知问题清单

### 致命问题（导致白屏/不可用）
| 问题 | 根因 | 修复方案 |
|------|------|---------|
| Chrome 白屏 | DOMPurify ESM 导出兼容性 — Chrome/Edge 解析 default export 方式不同 | useMarkdown.ts 统一 sanitize 解析 |
| 字体过小 | style.css `html` 未显式设置 `font-size: 15px` | 在 html + body 上强制 15px |

### 功能问题
| 问题 | 修复方案 |
|------|---------|
| RegisterView register() 未 await | 加 await + 错误处理 |
| WelcomeView timer 未完全清理 | onUnmounted 清理所有 ref |
| EvalView 弹窗 overlay 硬编码颜色 | 改用 --bg-modal-overlay |
| MindmapViewer 只支持 2 层 | 改为递归组件支持任意深度 |
| ProfileView isDirty 不准确 | 用 JSON.stringify 深比较 |

### 设计系统违规（硬编码颜色）
| 文件 | 硬编码 | 应改为 |
|------|--------|--------|
| ChatView | `#fff` | `var(--bg-card)` |
| ResourceCard | `linear-gradient(#4A7C6F, #E8C07A)` | `var(--accent-primary)` 纯色（设计规范禁止渐变） |
| MarkdownRenderer | `#4A7C6F` blockquote border | `var(--accent-primary)` |
| CodeViewer | `#2F3437` 代码背景 | 新 token `--code-bg: #2F3437` |
| MermaidRenderer | 6 个硬编码色值 | 通过 getComputedStyle 读取 CSS vars |
| VideoCard | `rgba(0,0,0,0.7)` | 新 token `--overlay-dark` |
| ChatMessageList | 硬编码 rgba 渐变 | 改用 CSS vars |
| ProfileView | styleBarColors 数组硬编码 | 改用 CSS vars |

---

## 2. 重构后目录结构

```
web/src/
├── main.ts                    # 入口 — 简洁同步初始化
├── App.vue                    # 根组件 — 仅 RouterView
├── style.css                  # 设计系统 tokens + reset + markdown + EP overrides
├── router/index.ts            # 路由 + 守卫
├── types/index.ts             # 所有 TypeScript 接口
├── mock/data.ts               # Mock 数据
├── composables/
│   └── useMarkdown.ts         # Markdown 渲染
├── stores/
│   ├── auth.ts
│   ├── chat.ts
│   ├── eval.ts
│   ├── notification.ts
│   ├── path.ts
│   └── profile.ts
├── components/
│   ├── layout/
│   │   └── AppLayout.vue      # 侧边栏 + 内容区
│   ├── chat/
│   │   ├── ChatMessageList.vue
│   │   ├── ChatInput.vue
│   │   ├── MessageBubble.vue
│   │   └── ResourceCard.vue
│   ├── common/
│   │   ├── FeedbackButtons.vue
│   │   ├── MarkdownRenderer.vue
│   │   └── MermaidRenderer.vue
│   ├── evaluate/
│   │   ├── EvalReport.vue
│   │   ├── QuizPanel.vue
│   │   └── QuizQuestion.vue
│   ├── notification/
│   │   ├── NotificationBell.vue
│   │   └── RecommendCard.vue
│   ├── path/
│   │   ├── PathNodeCard.vue
│   │   └── PathTimeline.vue
│   └── resource/
│       ├── CodeViewer.vue
│       ├── MindmapViewer.vue
│       └── VideoCard.vue
└── views/
    ├── auth/
    │   ├── LoginView.vue
    │   ├── RegisterView.vue
    │   └── WelcomeView.vue
    ├── chat/ChatView.vue
    ├── evaluate/EvalView.vue
    ├── notification/NotificationView.vue
    ├── path/PathView.vue
    └── profile/ProfileView.vue
```

---

## 3. 样式规范

### 新增 CSS tokens
```css
:root {
  /* 补充 tokens */
  --code-bg: #2F3437;
  --code-text: #E8E6E3;
  --overlay-dark: rgba(55, 53, 47, 0.6);
  --overlay-light: rgba(55, 53, 47, 0.03);
}
```

### 字体基准
- html: `font-size: 15px`
- body: `font-size: 15px; line-height: 1.65`
- 标题 H1: 30px / H2: 24px / H3: 18px

### 规则
- 所有颜色必须使用 CSS 变量
- 禁止渐变按钮/背景（设计规范）
- 阴影仅用于浮层，卡片用 border
- 动画 < 0.4s，不使用 bounce/elastic

---

## 4. 任务分工

### Agent A：全局基础（style.css + main.ts + index.html）
- 补充缺失的 CSS tokens（--code-bg, --overlay-dark 等）
- 确保 html/body font-size: 15px
- main.ts 保持简洁同步初始化
- 清理遗留动画关键帧

### Agent B：路由 + 认证流程（router + auth store + Login + Register + Welcome）
- 验证路由守卫无死循环
- RegisterView 加 await + 错误处理
- WelcomeView 修复 timer 清理
- 确保 login → /app/chat 跳转可靠

### Agent C：对话功能（Chat 相关全部组件）
- ChatView 硬编码 #fff → CSS var
- ChatMessageList 硬编码渐变 → CSS vars
- ResourceCard 去掉渐变，支持 5 种资源类型
- MessageBubble 验证 Mermaid 正则无死循环
- ChatInput 无问题

### Agent D：资源查看器 + 工具组件
- CodeViewer 代码背景 → --code-bg token
- MermaidRenderer 色值 → 读取 CSS vars
- MindmapViewer 改为递归组件支持任意深度
- VideoCard overlay → --overlay-dark token
- MarkdownRenderer blockquote 硬编码 → var
- FeedbackButtons 无问题
- useMarkdown.ts DOMPurify 兼容性确认

### Agent E：路径 + 评估 + 画像 + 通知
- PathView / PathTimeline / PathNodeCard 硬编码色值清理
- EvalView 弹窗 overlay → --bg-modal-overlay
- EvalReport 确认多维评估展示
- ProfileView styleBarColors 硬编码 → CSS vars，isDirty 修复
- NotificationView / Bell / RecommendCard 无问题

---

## 5. 验证清单

- [ ] `npx vue-tsc --noEmit` 零错误
- [ ] `npx vite build` 成功
- [ ] Chrome + Edge 均可正常渲染
- [ ] 字体大小正常（15px 基准）
- [ ] 所有页面非空白
- [ ] 登录 → 跳转 /app/chat 正常
- [ ] 注册 → 跳转 /welcome 正常
- [ ] 设计系统：grep 不到硬编码色值（除 #fff 白色和 #2F3437 代码背景 token 值）
