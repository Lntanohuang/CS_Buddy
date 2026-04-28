<script setup lang="ts">
import { computed, defineAsyncComponent, defineComponent, h } from 'vue'
import type { ChatMessage } from '@/types'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import FeedbackButtons from '@/components/common/FeedbackButtons.vue'
import ResourceCard from './ResourceCard.vue'
import MindmapViewer from '@/components/resource/MindmapViewer.vue'
import CodeViewer from '@/components/resource/CodeViewer.vue'
import VideoCard from '@/components/resource/VideoCard.vue'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  message: ChatMessage
}>()

const emit = defineEmits<{
  feedback: [payload: { messageId: string; feedback: 'USEFUL' | 'NOT_USEFUL' }]
}>()

const MermaidFallback = defineComponent({
  name: 'MermaidFallback',
  props: {
    code: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return () => h('pre', { class: 'message-mermaid-fallback' }, props.code)
  },
})

const MermaidRenderer = defineAsyncComponent({
  loader: () => import('@/components/common/MermaidRenderer.vue'),
  errorComponent: MermaidFallback,
  suspensible: false,
  timeout: 10000,
})

const userStore = useUserStore()

const isUser = computed(() => props.message.role === 'USER')

const hasResourceCard = computed(() => {
  return props.message.metadata?.type === 'resource_card'
})

const resourceType = computed(() => props.message.resource_type)

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

/** Extract mermaid code blocks from markdown content */
const contentParts = computed(() => {
  const content = props.message.content
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

  if (parts.length === 0) {
    parts.push({ type: 'markdown', content })
  }

  return parts
})

const hasMermaidBlocks = computed(() => contentParts.value.some(p => p.type === 'mermaid'))
const userAvatar = computed(() => userStore.userInfo.avatar)
const userName = computed(() => userStore.userInfo.name || '你')
</script>

<template>
  <div class="message-row" :class="{ 'message-row--user': isUser, 'message-row--assistant': !isUser }">
    <!-- Avatar -->
    <div v-if="isUser" class="message-avatar message-avatar--user">
      <img v-if="userAvatar" :src="userAvatar" :alt="userName" />
      <span v-else>你</span>
    </div>

    <!-- Bubble + timestamp -->
    <div class="message-body">
      <div class="message-bubble" :class="{ 'message-bubble--user': isUser, 'message-bubble--assistant': !isUser }">
        <!-- User message: plain text -->
        <div v-if="isUser" class="message-text message-text--user">
          {{ message.content }}
        </div>

        <!-- Assistant message: markdown rendered -->
        <div v-else class="message-text message-text--assistant">
          <!-- Content with mermaid block detection -->
          <template v-if="hasMermaidBlocks">
            <template v-for="(part, idx) in contentParts" :key="idx">
              <MarkdownRenderer v-if="part.type === 'markdown' && part.content.trim()" :content="part.content" />
              <MermaidRenderer v-else-if="part.type === 'mermaid'" :code="part.content" />
            </template>
          </template>
          <MarkdownRenderer v-else :content="message.content" />

          <!-- Resource-type specific viewers -->
          <MindmapViewer
            v-if="resourceType === 'mindmap' && message.metadata?.mindmap_data"
            :data="(message.metadata.mindmap_data as any)"
          />

          <CodeViewer
            v-if="resourceType === 'code' && message.metadata?.code"
            :code="(message.metadata.code as string)"
            :language="(message.metadata.language as string) ?? 'text'"
            :expected-output="(message.metadata.expected_output as string)"
          />

          <VideoCard
            v-if="resourceType === 'video' && message.metadata?.title"
            :title="(message.metadata.title as string)"
            :duration="(message.metadata.duration as number)"
            :status="(message.metadata.status as 'generating' | 'ready' | 'error')"
          />

          <MermaidRenderer
            v-if="resourceType === 'mermaid' && message.metadata?.mermaid_code"
            :code="(message.metadata.mermaid_code as string)"
          />

          <ResourceCard
            v-if="hasResourceCard"
            :title="(message.metadata!.title as string)"
            :difficulty="(message.metadata!.difficulty as string)"
            :est-minutes="(message.metadata!.est_minutes as number)"
            :knowledge-point="(message.metadata!.knowledge_point as string)"
            :resource-type="(message.metadata!.resource_type as any)"
          />

          <FeedbackButtons
            :message-id="message.message_id"
            @feedback="emit('feedback', $event)"
          />
        </div>
      </div>

      <div class="message-time">{{ formattedTime }}</div>
    </div>
  </div>
</template>

<style scoped>
.message-row {
  display: flex;
  gap: 10px;
  width: 100%;
}

.message-row--user {
  align-self: flex-end;
  flex-direction: row-reverse;
  max-width: 80%;
}

.message-row--assistant {
  align-self: stretch;
}

/* Avatar */
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  margin-top: 0;
}

.message-avatar--user {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-primary);
}

.message-avatar img {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 50%;
  object-fit: cover;
}

/* Body */
.message-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
  margin-top: 0;
}

.message-row--user .message-body {
  align-items: flex-end;
  margin-top: 6px;
}

.message-row--assistant .message-body {
  align-items: stretch;
  width: 100%;
}


/* Bubble */
.message-bubble {
  word-break: break-word;
}

.message-bubble--user {
  background: var(--accent-primary);
  color: var(--bg-card);
  padding: 12px 18px;
  border-radius: 16px;
  border-top-right-radius: 2px;
  box-shadow: var(--shadow-sm);
}

.message-bubble--assistant {
  background: transparent;
  border: 0;
  padding: 0;
  border-radius: 0;
  box-shadow: none;
  width: 100%;
}

/* Text */
.message-text--user {
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.6;
}

.message-text--assistant {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  width: 100%;
}

/* Timestamp */
.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 5px;
  padding: 0 4px;
}

.message-mermaid-fallback {
  margin: 8px 0;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-hover);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  overflow-x: auto;
}
</style>
