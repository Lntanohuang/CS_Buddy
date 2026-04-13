<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { ChatMessage } from '@/types'
import MessageBubble from './MessageBubble.vue'

const props = defineProps<{
  messages: ChatMessage[]
  isStreaming: boolean
}>()

const scrollContainer = ref<HTMLDivElement>()

function scrollToBottom() {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

// Watch messages length and streaming state to auto-scroll
watch(
  () => [props.messages.length, props.isStreaming] as const,
  () => {
    scrollToBottom()
  },
)

// Also watch last message content changes during streaming
watch(
  () => props.messages[props.messages.length - 1]?.content,
  () => {
    if (props.isStreaming) {
      scrollToBottom()
    }
  },
)

const showTypingIndicator = computed(() => {
  if (!props.isStreaming) return false
  const last = props.messages[props.messages.length - 1]
  return last?.role === 'USER'
})
</script>

<template>
  <div ref="scrollContainer" class="chat-message-list">
    <div class="chat-message-list__inner">
      <MessageBubble
        v-for="msg in messages"
        :key="msg.message_id"
        :message="msg"
      />

      <div v-if="showTypingIndicator" class="typing-indicator">
        <span class="typing-indicator__dot" />
        <span class="typing-indicator__dot" />
        <span class="typing-indicator__dot" />
        <span class="typing-indicator__text">智伴正在思考...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: var(--el-fill-color-lighter, #f5f7fa);
}

.chat-message-list__inner {
  display: flex;
  flex-direction: column;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.typing-indicator__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--el-text-color-placeholder);
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-indicator__dot:nth-child(1) { animation-delay: 0s; }
.typing-indicator__dot:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator__dot:nth-child(3) { animation-delay: 0.4s; }

.typing-indicator__text {
  margin-left: 4px;
}

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
