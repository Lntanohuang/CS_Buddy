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
  <div class="message-bubble" :class="{ 'message-bubble--user': isUser, 'message-bubble--assistant': !isUser }">
    <div class="message-bubble__content">
      <!-- User message: plain text -->
      <div v-if="isUser" class="message-bubble__text message-bubble__text--user">
        {{ message.content }}
      </div>

      <!-- Assistant message: markdown rendered -->
      <div v-else class="message-bubble__text message-bubble__text--assistant">
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

    <div class="message-bubble__time">{{ formattedTime }}</div>
  </div>
</template>

<style scoped>
.message-bubble {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
  max-width: 80%;
}

.message-bubble--user {
  align-self: flex-end;
  align-items: flex-end;
}

.message-bubble--assistant {
  align-self: flex-start;
  align-items: flex-start;
}

.message-bubble__text {
  padding: 12px 16px;
  border-radius: 12px;
  word-break: break-word;
}

.message-bubble__text--user {
  background-color: var(--el-color-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
  white-space: pre-wrap;
}

.message-bubble__text--assistant {
  background-color: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-bottom-left-radius: 4px;
}

.message-bubble__time {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  margin-top: 4px;
}
</style>
