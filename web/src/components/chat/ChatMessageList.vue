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

const isEmpty = computed(() => props.messages.length === 0)
</script>

<template>
  <div ref="scrollContainer" class="chat-message-list">
    <!-- Empty state -->
    <div v-if="isEmpty" class="chat-empty">
      <div class="chat-empty__icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </div>
      <h3 class="chat-empty__title">开始你的学习之旅</h3>
      <p class="chat-empty__desc">向智伴提问任何学习问题，获取个性化的学习建议</p>
    </div>

    <!-- Messages -->
    <div v-else class="chat-message-list__inner">
      <MessageBubble
        v-for="msg in messages"
        :key="msg.message_id"
        :message="msg"
      />

      <!-- Typing indicator -->
      <div v-if="showTypingIndicator" class="typing-row">
        <div class="typing-avatar">
          <span>✦</span>
        </div>
        <div class="typing-bubble">
          <span class="typing-dot" />
          <span class="typing-dot" />
          <span class="typing-dot" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: var(--bg-primary);
  scroll-behavior: smooth;
}

.chat-message-list__inner {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

/* Empty state */
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px 20px;
}

.chat-empty__icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--accent-primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
  margin-bottom: 20px;
}

.chat-empty__title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px;
  font-family: system-ui, -apple-system, sans-serif;
}

.chat-empty__desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Typing indicator */
.typing-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  align-self: flex-start;
}

.typing-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-secondary);
  color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
}

.typing-bubble {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 12px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  border-top-left-radius: 2px;
  box-shadow: var(--shadow-sm);
}

.typing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--text-secondary);
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-dot:nth-child(1) { animation-delay: 0s; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 80%, 100% {
    transform: scale(0.5);
    opacity: 0.35;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
