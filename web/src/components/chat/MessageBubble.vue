<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '@/types'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import FeedbackButtons from '@/components/common/FeedbackButtons.vue'
import ResourceCard from './ResourceCard.vue'

const props = defineProps<{
  message: ChatMessage
}>()

const isUser = computed(() => props.message.role === 'USER')

const hasResourceCard = computed(() => {
  return props.message.metadata?.type === 'resource_card'
})

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})
</script>

<template>
  <div class="message-row" :class="{ 'message-row--user': isUser, 'message-row--assistant': !isUser }">
    <!-- Avatar -->
    <div class="message-avatar" :class="{ 'message-avatar--user': isUser, 'message-avatar--assistant': !isUser }">
      <span v-if="isUser">你</span>
      <span v-else>✦</span>
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
          <MarkdownRenderer :content="message.content" />

          <ResourceCard
            v-if="hasResourceCard"
            :title="(message.metadata!.title as string)"
            :difficulty="(message.metadata!.difficulty as string)"
            :est-minutes="(message.metadata!.est_minutes as number)"
            :knowledge-point="(message.metadata!.knowledge_point as string)"
          />

          <FeedbackButtons :message-id="message.message_id" />
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
  max-width: 80%;
}

.message-row--user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-row--assistant {
  align-self: flex-start;
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
  margin-top: 2px;
}

.message-avatar--user {
  background: var(--accent-primary);
  color: var(--bg-card)fff;
}

.message-avatar--assistant {
  background: var(--accent-secondary);
  color: var(--bg-card)fff;
}

/* Body */
.message-body {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.message-row--user .message-body {
  align-items: flex-end;
}

.message-row--assistant .message-body {
  align-items: flex-start;
}

/* Bubble */
.message-bubble {
  word-break: break-word;
}

.message-bubble--user {
  background: var(--accent-primary);
  color: var(--bg-card)fff;
  padding: 12px 18px;
  border-radius: 16px;
  border-top-right-radius: 2px;
  box-shadow: 0 1px 3px rgba(74, 124, 111, 0.2);
}

.message-bubble--assistant {
  background: var(--bg-card);
  border: 1px solid var(--border);
  padding: 14px 18px;
  border-radius: 16px;
  border-top-left-radius: 2px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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
}

/* Timestamp */
.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 5px;
  padding: 0 4px;
}
</style>
