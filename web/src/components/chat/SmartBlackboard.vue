<script setup lang="ts">
import { computed, defineAsyncComponent, defineComponent, h } from 'vue'
import type { AgentStep, ChatMessage } from '@/types'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import FeedbackButtons from '@/components/common/FeedbackButtons.vue'
import ResourceCard from './ResourceCard.vue'
import MindmapViewer from '@/components/resource/MindmapViewer.vue'
import CodeViewer from '@/components/resource/CodeViewer.vue'
import VideoCard from '@/components/resource/VideoCard.vue'

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
  props: {
    code: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return () => h('pre', { class: 'blackboard-mermaid-fallback' }, props.code)
  },
})

const MermaidRenderer = defineAsyncComponent({
  loader: () => import('@/components/common/MermaidRenderer.vue'),
  errorComponent: MermaidFallback,
  suspensible: false,
  timeout: 10000,
})

const resourceType = computed(() => props.currentMessage?.resource_type)

const hasResourceCard = computed(() => {
  return props.currentMessage?.metadata?.type === 'resource_card'
})

const contentParts = computed(() => {
  const content = props.currentMessage?.content ?? ''
  if (!content) return [{ type: 'markdown' as const, content: '' }]

  const mermaidRegex = /```mermaid\s*\r?\n([\s\S]*?)```/g
  const mermaidMatches = Array.from(content.matchAll(mermaidRegex))
  if (mermaidMatches.length === 0) {
    return [{ type: 'markdown' as const, content }]
  }

  const parts: Array<{ type: 'markdown' | 'mermaid'; content: string }> = []
  let lastIndex = 0

  for (const match of mermaidMatches) {
    const matchIndex = match.index ?? 0
    if (matchIndex > lastIndex) {
      parts.push({ type: 'markdown', content: content.slice(lastIndex, matchIndex) })
    }
    parts.push({ type: 'mermaid', content: match[1].trim() })
    lastIndex = matchIndex + match[0].length
  }

  if (lastIndex < content.length) {
    parts.push({ type: 'markdown', content: content.slice(lastIndex) })
  }

  return parts.length ? parts : [{ type: 'markdown' as const, content }]
})

const hasMermaidBlocks = computed(() => contentParts.value.some((part) => part.type === 'mermaid'))
const hasActiveContent = computed(() => Boolean(props.currentMessage?.content))
const visibleQuestion = computed(() => props.currentQuestion.trim())
</script>

<template>
  <section class="smart-blackboard" aria-live="polite">
    <div class="smart-blackboard__surface">
      <Transition name="blackboard-fade" mode="out-in">
        <div v-if="isThinking && !hasActiveContent" key="thinking" class="blackboard-state blackboard-state--thinking">
          <div class="blackboard-state__pulse" />
          <p class="blackboard-state__title">正在思考</p>
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
          <header v-if="visibleQuestion" class="blackboard-question">
            <span class="blackboard-question__label">问题</span>
            <p>{{ visibleQuestion }}</p>
          </header>

          <div class="blackboard-writing" :class="{ 'is-generating': isGenerating }">
            <template v-if="hasMermaidBlocks">
              <template v-for="(part, idx) in contentParts" :key="idx">
                <MarkdownRenderer
                  v-if="part.type === 'markdown' && part.content.trim()"
                  :content="part.content"
                />
                <MermaidRenderer v-else-if="part.type === 'mermaid'" :code="part.content" />
              </template>
            </template>
            <MarkdownRenderer v-else :content="currentMessage.content" />

            <MindmapViewer
              v-if="resourceType === 'mindmap' && currentMessage.metadata?.mindmap_data"
              :data="(currentMessage.metadata.mindmap_data as any)"
            />

            <CodeViewer
              v-if="resourceType === 'code' && currentMessage.metadata?.code"
              :code="(currentMessage.metadata.code as string)"
              :language="(currentMessage.metadata.language as string) ?? 'text'"
              :expected-output="(currentMessage.metadata.expected_output as string)"
            />

            <VideoCard
              v-if="resourceType === 'video' && currentMessage.metadata?.title"
              :title="(currentMessage.metadata.title as string)"
              :duration="(currentMessage.metadata.duration as number)"
              :status="(currentMessage.metadata.status as 'generating' | 'ready' | 'error')"
            />

            <MermaidRenderer
              v-if="resourceType === 'mermaid' && currentMessage.metadata?.mermaid_code"
              :code="(currentMessage.metadata.mermaid_code as string)"
            />

            <ResourceCard
              v-if="hasResourceCard"
              :title="(currentMessage.metadata!.title as string)"
              :difficulty="(currentMessage.metadata!.difficulty as string)"
              :est-minutes="(currentMessage.metadata!.est_minutes as number)"
              :knowledge-point="(currentMessage.metadata!.knowledge_point as string)"
              :resource-type="(currentMessage.metadata!.resource_type as any)"
            />
          </div>

          <footer v-if="!isGenerating" class="blackboard-feedback">
            <FeedbackButtons
              :message-id="currentMessage.message_id"
              @feedback="emit('feedback', $event)"
            />
          </footer>
        </article>

        <div v-else key="empty" class="blackboard-state blackboard-state--empty">
          <p class="blackboard-state__eyebrow">CS Buddy</p>
          <h1>今天想学点什么？</h1>
        </div>
      </Transition>
    </div>
  </section>
</template>

<style scoped>
.smart-blackboard {
  min-width: 0;
  min-height: 0;
  height: 100%;
}

.smart-blackboard__surface {
  position: relative;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 28px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.56)),
    color-mix(in srgb, var(--bg-card) 72%, transparent);
  box-shadow: 0 22px 70px rgba(55, 77, 96, 0.14);
  backdrop-filter: blur(24px);
}

.blackboard-content {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: clamp(22px, 3vw, 38px);
}

.blackboard-question {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(var(--accent-primary-rgb), 0.12);
}

.blackboard-question__label {
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 600;
}

.blackboard-question p {
  min-width: 0;
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(16px, 1.8vw, 21px);
  font-weight: 650;
  line-height: 1.5;
  word-break: break-word;
}

.blackboard-writing {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-right: 6px;
}

.blackboard-writing :deep(.markdown-renderer) {
  font-size: 15px;
  line-height: 1.85;
}

.blackboard-writing :deep(.markdown-renderer h1),
.blackboard-writing :deep(.markdown-renderer h2),
.blackboard-writing :deep(.markdown-renderer h3) {
  margin-top: 0.85em;
}

.blackboard-writing :deep(.code-viewer),
.blackboard-writing :deep(.mindmap-viewer),
.blackboard-writing :deep(.resource-card) {
  max-width: 100%;
}

.blackboard-writing.is-generating::after {
  content: "";
  display: inline-block;
  width: 8px;
  height: 18px;
  margin-left: 4px;
  border-radius: 999px;
  background: var(--accent-primary);
  animation: caret-blink 0.9s ease-in-out infinite;
  vertical-align: text-bottom;
}

.blackboard-feedback {
  flex-shrink: 0;
  padding-top: 8px;
}

.blackboard-state {
  height: 100%;
  min-height: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  text-align: center;
}

.blackboard-state--empty h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: clamp(28px, 4vw, 48px);
  font-weight: 760;
  line-height: 1.12;
}

.blackboard-state__eyebrow {
  margin: 0 0 12px;
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
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
  padding: 8px 12px;
  border: 1px solid rgba(var(--accent-primary-rgb), 0.1);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.56);
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

.blackboard-mermaid-fallback {
  margin: 12px 0;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-hover);
  color: var(--text-primary);
  overflow-x: auto;
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
    padding: 18px;
  }

  .blackboard-question {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
