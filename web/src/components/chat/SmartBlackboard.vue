<script setup lang="ts">
import { computed, defineAsyncComponent, defineComponent, h } from 'vue'
import type { AgentStep, ChatMessage } from '@/types'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import FeedbackButtons from '@/components/common/FeedbackButtons.vue'
import ResourceCard from './ResourceCard.vue'
import MindmapViewer from '@/components/resource/MindmapViewer.vue'
import CodeViewer from '@/components/resource/CodeViewer.vue'
import TreeDiagram from '@/components/resource/TreeDiagram.vue'
import VideoCard from '@/components/resource/VideoCard.vue'

type TeachingSection =
  | { id: string; type: 'text'; title: string; content: string }
  | { id: string; type: 'tip'; title: string; content: string }
  | { id: string; type: 'code'; title: string; code: string; language: string }
  | { id: string; type: 'diagram'; title: string; code: string; renderAsTree: boolean }
  | { id: string; type: 'resource'; title: string }

const props = defineProps<{
  currentMessage: ChatMessage | null
  currentQuestion: string
  isThinking: boolean
  isGenerating: boolean
  agentSteps?: AgentStep[]
}>()

const emit = defineEmits<{
  feedback: [payload: { messageId: string; feedback: 'USEFUL' | 'NOT_USEFUL' }]
}>()

const MermaidFallback = defineComponent({
  name: 'BlackboardMermaidFallback',
  setup() {
    return () => h('p', { class: 'blackboard-diagram-fallback' }, '图示暂不可用')
  },
})

const MermaidRenderer = defineAsyncComponent({
  loader: () => import('@/components/common/MermaidRenderer.vue'),
  errorComponent: MermaidFallback,
  suspensible: false,
  timeout: 10000,
})

const resourceType = computed(() => props.currentMessage?.resource_type)
const metadata = computed(() => props.currentMessage?.metadata)
const visibleQuestion = computed(() => props.currentQuestion.trim())

const hasResourceCard = computed(() => {
  return metadata.value?.type === 'resource_card'
})

const lectureTitle = computed(() => {
  const title = metadata.value?.title
  if (typeof title === 'string' && title.trim()) return title.trim()
  if (visibleQuestion.value) return visibleQuestion.value.slice(0, 28)
  return '本节学习内容'
})

const teachingSections = computed<TeachingSection[]>(() => {
  const message = props.currentMessage
  if (!message?.content) return []

  return buildTeachingSections(message.content, hasResourceCard.value)
})

const hasActiveContent = computed(() => teachingSections.value.length > 0)
const hasSpecialViewer = computed(() =>
  Boolean(
    (resourceType.value === 'mindmap' && metadata.value?.mindmap_data)
      || (resourceType.value === 'code' && metadata.value?.code)
      || (resourceType.value === 'video' && metadata.value?.title)
      || (resourceType.value === 'mermaid' && metadata.value?.mermaid_code),
  ),
)

function buildTeachingSections(content: string, includeResourceCard: boolean): TeachingSection[] {
  const sections: TeachingSection[] = []
  const fencedBlockRegex = /```(\w+)?\s*\r?\n([\s\S]*?)```/g
  let lastIndex = 0
  let blockIndex = 0

  for (const match of content.matchAll(fencedBlockRegex)) {
    const matchIndex = match.index ?? 0
    pushTextSections(sections, content.slice(lastIndex, matchIndex))

    const language = match[1]?.trim() || 'text'
    const code = match[2].trim()

    if (language.toLowerCase() === 'mermaid') {
      sections.push({
        id: `diagram-${blockIndex}`,
        type: 'diagram',
        title: '图示讲解',
        code,
        renderAsTree: isTreeDiagram(code),
      })
    } else {
      sections.push({
        id: `code-${blockIndex}`,
        type: 'code',
        title: '代码演示',
        code,
        language,
      })
    }

    blockIndex += 1
    lastIndex = matchIndex + match[0].length
  }

  pushTextSections(sections, content.slice(lastIndex))

  if (includeResourceCard) {
    sections.push({
      id: 'resource-card',
      type: 'resource',
      title: '随堂练习',
    })
  }

  return sections.length
    ? sections
    : [{ id: 'empty-text', type: 'text' as const, title: '思路拆解', content }]
}

function pushTextSections(sections: TeachingSection[], segment: string) {
  const normalized = segment.trim()
  if (!normalized) return

  const { body, tips } = extractTips(normalized)
  const chunks = splitMarkdownByHeading(body)

  chunks.forEach((chunk, index) => {
    if (!chunk.content.trim()) return
    sections.push({
      id: `text-${sections.length}-${index}`,
      type: 'text',
      title: normalizeSectionTitle(chunk.heading, sections.length),
      content: chunk.content.trim(),
    })
  })

  tips.forEach((tip, index) => {
    sections.push({
      id: `tip-${sections.length}-${index}`,
      type: 'tip',
      title: '易错提醒',
      content: tip,
    })
  })
}

function extractTips(content: string) {
  const tips: string[] = []
  const bodyLines: string[] = []

  content.split(/\r?\n/).forEach((line) => {
    if (line.trim().startsWith('>')) {
      tips.push(line.replace(/^>\s?/, '').trim())
      return
    }

    bodyLines.push(line)
  })

  return {
    body: bodyLines.join('\n').trim(),
    tips,
  }
}

function splitMarkdownByHeading(content: string) {
  const lines = content.split(/\r?\n/)
  const chunks: Array<{ heading: string; content: string }> = []
  let currentHeading = ''
  let currentLines: string[] = []

  lines.forEach((line) => {
    const headingMatch = line.match(/^#{1,3}\s+(.+)$/)
    if (headingMatch) {
      if (currentLines.join('\n').trim()) {
        chunks.push({ heading: currentHeading, content: currentLines.join('\n') })
      }
      currentHeading = headingMatch[1].trim()
      currentLines = []
      return
    }

    currentLines.push(line)
  })

  if (currentLines.join('\n').trim()) {
    chunks.push({ heading: currentHeading, content: currentLines.join('\n') })
  }

  return chunks
}

function normalizeSectionTitle(heading: string, index: number) {
  if (/代码|实现|示例/i.test(heading)) return '代码演示'
  if (/图|结构|mermaid/i.test(heading)) return '图示讲解'
  if (/总结|结果|输出/i.test(heading)) return '本节总结'
  if (/练习|题目|巩固/i.test(heading)) return '随堂练习'
  if (/复杂度|注意|技巧|重点|提醒/i.test(heading)) return '易错提醒'
  if (/类型|概念|思想|原理|基础|核心/i.test(heading)) return '思路拆解'
  if (heading) return heading.replace(/^#+\s*/, '')
  return index === 0 ? '思路拆解' : '补充说明'
}

function isTreeDiagram(code: string) {
  return /graph\s+(TD|TB)/i.test(code) && /-->|---/.test(code)
}

</script>

<template>
  <section class="smart-blackboard" aria-live="polite">
    <div class="smart-blackboard__surface">
      <Transition name="blackboard-fade" mode="out-in">
        <div v-if="isThinking && !hasActiveContent" key="thinking" class="blackboard-state blackboard-state--thinking">
          <div class="blackboard-state__pulse" />
          <p class="blackboard-state__title">小海豹正在拆解这个问题</p>
          <div v-if="agentSteps?.length" class="blackboard-agents">
            <div
              v-for="step in agentSteps"
              :key="step.agent"
              class="blackboard-agent"
              :class="`blackboard-agent--${step.status}`"
            >
              <span class="blackboard-agent__icon">{{ step.icon }}</span>
              <span class="blackboard-agent__label">{{ step.label }}</span>
            </div>
          </div>
        </div>

        <article v-else-if="currentMessage" :key="currentMessage.message_id" class="blackboard-content">
          <header class="blackboard-lesson">
            <div class="blackboard-lesson__main">
              <div class="blackboard-lesson__item">
                <span>课堂白板：</span>
                <h1>{{ lectureTitle }}</h1>
              </div>
            </div>
          </header>

          <div class="teaching-scroll">
            <div class="teaching-sections" :class="{ 'is-generating': isGenerating }">
              <section
                v-for="section in teachingSections"
                :key="section.id"
                class="teaching-card"
                :class="`teaching-card--${section.type}`"
              >
                <div class="teaching-card__title">{{ section.title }}</div>

                <MarkdownRenderer
                  v-if="section.type === 'text' || section.type === 'tip'"
                  :content="section.content"
                />

                <CodeViewer
                  v-else-if="section.type === 'code'"
                  :code="section.code"
                  :language="section.language"
                />

                <TreeDiagram
                  v-else-if="section.type === 'diagram' && section.renderAsTree"
                  :code="section.code"
                />

                <MermaidRenderer
                  v-else-if="section.type === 'diagram'"
                  :code="section.code"
                />

                <ResourceCard
                  v-else-if="section.type === 'resource' && currentMessage.metadata"
                  :title="(currentMessage.metadata.title as string)"
                  :difficulty="(currentMessage.metadata.difficulty as string)"
                  :est-minutes="(currentMessage.metadata.est_minutes as number)"
                  :knowledge-point="(currentMessage.metadata.knowledge_point as string)"
                  :resource-type="(currentMessage.metadata.resource_type as any)"
                />
              </section>

              <section v-if="hasSpecialViewer" class="teaching-card teaching-card--resource">
                <div class="teaching-card__title">拓展材料</div>
                <MindmapViewer
                  v-if="resourceType === 'mindmap' && metadata?.mindmap_data"
                  :data="(metadata.mindmap_data as any)"
                />

                <CodeViewer
                  v-if="resourceType === 'code' && metadata?.code"
                  :code="(metadata.code as string)"
                  :language="(metadata.language as string) ?? 'text'"
                  :expected-output="(metadata.expected_output as string)"
                />

                <VideoCard
                  v-if="resourceType === 'video' && metadata?.title"
                  :title="(metadata.title as string)"
                  :duration="(metadata.duration as number)"
                  :status="(metadata.status as 'generating' | 'ready' | 'error')"
                />

                <MermaidRenderer
                  v-if="resourceType === 'mermaid' && metadata?.mermaid_code"
                  :code="(metadata.mermaid_code as string)"
                />
              </section>

              <footer v-if="!isGenerating" class="blackboard-feedback">
                <FeedbackButtons
                  :message-id="currentMessage.message_id"
                  @feedback="emit('feedback', $event)"
                />
              </footer>
            </div>
          </div>
        </article>

        <div v-else key="empty" class="blackboard-state blackboard-state--empty">
          <p class="blackboard-state__eyebrow">小海豹导师</p>
          <h1>今天想学点什么？</h1>
        </div>
      </Transition>
    </div>
  </section>
</template>

<style scoped>
.smart-blackboard {
  --blackboard-text: #1d1d1f;
  --blackboard-muted: #5f6368;
  --blackboard-tag-bg: rgba(var(--accent-primary-rgb), 0.1);
  --blackboard-tag-text: color-mix(in srgb, var(--accent-primary) 82%, #1d1d1f);

  min-width: 0;
  min-height: 0;
  height: 100%;
}

.smart-blackboard__surface {
  position: relative;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.blackboard-content {
  position: relative;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
}

.blackboard-lesson {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 8;
  max-width: min(640px, calc(100% - 12px));
  border: 0;
  pointer-events: none;
}

.blackboard-lesson__main {
  min-width: 0;
  display: flex;
  align-items: center;
  min-height: 36px;
  padding: 0 13px;
  border: 1px solid rgba(255, 255, 255, 0.78);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.blackboard-lesson__item {
  min-width: 0;
  max-width: 100%;
  display: flex;
  align-items: center;
  flex: 1;
  gap: 2px;
}

.blackboard-lesson__item span {
  color: var(--accent-primary);
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.blackboard-lesson h1 {
  min-width: 0;
  margin: 0;
  color: var(--blackboard-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.blackboard-lesson h1 {
  font-size: 12px;
  font-weight: 650;
  line-height: 1.3;
}

.blackboard-question {
  flex-shrink: 0;
  display: grid;
  gap: 10px;
  padding: 2px 0 18px;
  border-bottom: 1px solid rgba(29, 29, 31, 0.1);
}

.blackboard-question__label {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  flex-shrink: 0;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--blackboard-tag-bg);
  color: var(--blackboard-tag-text);
  font-size: 12px;
  font-weight: 750;
}

.blackboard-question p {
  min-width: 0;
  margin: 0;
  color: var(--blackboard-text);
  font-size: 15px;
  font-weight: 500;
  line-height: 1.55;
  word-break: break-word;
}

.teaching-scroll {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-top: 46px;
  padding-right: 4px;
  padding-bottom: 112px;
}

.teaching-sections {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding-bottom: 8px;
}

.teaching-card {
  padding: 24px 0;
  border-top: 1px solid rgba(29, 29, 31, 0.08);
  background: transparent;
}

.teaching-card--code,
.teaching-card--diagram,
.teaching-card--resource {
  background: transparent;
}

.teaching-card--tip {
  border-top-color: color-mix(in srgb, var(--accent-secondary) 22%, rgba(29, 29, 31, 0.08));
  background: transparent;
}

.teaching-card:first-child {
  padding-top: 18px;
  border-top: 0;
}

.teaching-card:last-child {
  padding-bottom: 8px;
}

.teaching-card__title {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  margin-bottom: 14px;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--blackboard-tag-bg);
  color: var(--blackboard-tag-text);
  font-size: 12px;
  font-weight: 750;
}

.teaching-card :deep(.markdown-renderer) {
  color: var(--blackboard-text);
  font-size: 15px;
  font-weight: 400;
  line-height: 1.82;
}

.teaching-card :deep(.markdown-renderer p),
.teaching-card :deep(.markdown-renderer li) {
  color: var(--blackboard-text);
}

.teaching-card :deep(.markdown-renderer strong) {
  color: var(--blackboard-text);
  font-weight: 700;
}

.teaching-card :deep(.markdown-renderer h1),
.teaching-card :deep(.markdown-renderer h2),
.teaching-card :deep(.markdown-renderer h3) {
  margin-top: 0.5em;
  color: var(--blackboard-text);
  font-weight: 650;
}

.teaching-card :deep(.code-viewer),
.teaching-card :deep(.mindmap-viewer),
.teaching-card :deep(.resource-card) {
  max-width: 100%;
}

.teaching-sections.is-generating::after {
  content: "";
  display: block;
  width: 34px;
  height: 4px;
  border-radius: 999px;
  background: var(--accent-primary);
  animation: caret-blink 0.9s ease-in-out infinite;
}

.blackboard-feedback {
  padding: 18px 0 4px;
  border-top: 1px solid rgba(29, 29, 31, 0.08);
}

.blackboard-state {
  height: 100%;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  text-align: center;
}

.blackboard-state--empty h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(28px, 4vw, 44px);
  font-weight: 760;
  line-height: 1.12;
}

.blackboard-state__eyebrow {
  margin: 0 0 12px;
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
}

.blackboard-state__pulse {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background:
    radial-gradient(circle, var(--accent-primary) 0 18%, transparent 19%),
    color-mix(in srgb, var(--accent-primary) 12%, transparent);
  box-shadow: 0 0 0 0 rgba(var(--accent-primary-rgb), 0.26);
  animation: blackboard-pulse 1.6s ease-out infinite;
}

.blackboard-state__title {
  margin: 18px 0 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 650;
}

.blackboard-agents {
  width: min(420px, 100%);
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.blackboard-agent {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 0;
  border-top: 1px solid rgba(29, 29, 31, 0.08);
  border-radius: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  text-align: left;
}

.blackboard-agent--working {
  color: var(--accent-primary);
  border-color: rgba(var(--accent-primary-rgb), 0.24);
}

.blackboard-agent--done {
  opacity: 0.56;
}

.blackboard-agent__icon {
  width: 22px;
  flex-shrink: 0;
  text-align: center;
}

.blackboard-agent__label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.blackboard-diagram-fallback {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.blackboard-fade-enter-active,
.blackboard-fade-leave-active {
  transition: opacity 0.24s ease, transform 0.24s ease;
}

.blackboard-fade-enter-from,
.blackboard-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes blackboard-pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--accent-primary-rgb), 0.26);
    transform: scale(0.96);
  }

  70% {
    box-shadow: 0 0 0 20px rgba(var(--accent-primary-rgb), 0);
    transform: scale(1);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(var(--accent-primary-rgb), 0);
    transform: scale(0.96);
  }
}

@keyframes caret-blink {
  0%,
  100% {
    opacity: 0.2;
  }

  50% {
    opacity: 1;
  }
}

@media (max-width: 760px) {
  .blackboard-content {
    padding: 16px;
  }

  .blackboard-lesson {
    max-width: calc(100% - 8px);
  }

  .blackboard-lesson__item {
    min-width: 0;
  }

  .blackboard-question {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
