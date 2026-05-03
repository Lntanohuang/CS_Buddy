<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { ChatMessage, AgentStep } from '@/types'
import MessageBubble from './MessageBubble.vue'

const props = defineProps<{
  messages: ChatMessage[]
  isStreaming: boolean
  agentSteps?: AgentStep[]
  isAgentWorking?: boolean
}>()

const emit = defineEmits<{
  feedback: [payload: { messageId: string; feedback: 'USEFUL' | 'NOT_USEFUL' }]
}>()

const scrollContainer = ref<HTMLDivElement>()
const isPinnedToBottom = ref(true)
const bottomThreshold = 96

function getDistanceFromBottom() {
  const el = scrollContainer.value
  if (!el) return 0
  return el.scrollHeight - el.clientHeight - el.scrollTop
}

function updatePinnedState() {
  isPinnedToBottom.value = getDistanceFromBottom() <= bottomThreshold
}

function scrollToBottom(behavior: ScrollBehavior = 'smooth') {
  nextTick(() => {
    const el = scrollContainer.value
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior })
    isPinnedToBottom.value = true
  })
}

function handleScroll() {
  updatePinnedState()
}

function handleJumpToBottom() {
  scrollToBottom('smooth')
}

// New user messages reveal the latest turn. Streamed assistant text only follows
// while the reader is still near the bottom.
watch(
  () => props.messages.length,
  (count, previousCount) => {
    if (count === 0) {
      isPinnedToBottom.value = true
      return
    }

    const latestMessage = props.messages[count - 1]
    const addedMessage = previousCount === undefined || count > previousCount

    if (addedMessage && latestMessage?.role === 'USER') {
      scrollToBottom('auto')
      return
    }

    if (isPinnedToBottom.value) {
      scrollToBottom()
    }
  },
)

watch(
  () => props.messages[props.messages.length - 1]?.content,
  () => {
    if (props.isStreaming && isPinnedToBottom.value) {
      scrollToBottom()
    }
  },
)

watch(
  () => props.agentSteps?.map((step) => `${step.agent}:${step.status}`).join('|'),
  () => {
    if (props.isAgentWorking && isPinnedToBottom.value) {
      scrollToBottom()
    }
  },
)

const showTypingIndicator = computed(() => {
  if (!props.isStreaming) return false
  const last = props.messages[props.messages.length - 1]
  return last?.role === 'USER'
})

const showJumpToBottom = computed(() => {
  return (props.isStreaming || props.isAgentWorking) && !isPinnedToBottom.value
})

const isEmpty = computed(() => props.messages.length === 0)
</script>

<template>
  <div class="chat-message-list-shell">
    <div
      ref="scrollContainer"
      class="chat-message-list"
      @scroll="handleScroll"
    >
    <!-- Empty state -->
    <div v-if="isEmpty" class="chat-empty">
      <div class="chat-empty__icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </div>
      <h3 class="chat-empty__title">开始你的学习之旅</h3>
      <p class="chat-empty__desc">向CS Buddy提问任何学习问题，获取个性化的学习建议</p>
    </div>

    <!-- Messages -->
    <div v-else class="chat-message-list__inner">
      <MessageBubble
        v-for="msg in messages"
        :key="msg.message_id"
        :message="msg"
        @feedback="emit('feedback', $event)"
      />

      <!-- Agent working steps -->
      <div v-if="isAgentWorking && agentSteps?.length" class="agent-steps">
        <div
          v-for="step in agentSteps"
          :key="step.agent"
          class="agent-step"
          :class="`agent-step--${step.status}`"
        >
          <span class="agent-step__icon">{{ step.icon }}</span>
          <span class="agent-step__name">{{ step.agent }}</span>
          <span class="agent-step__label">{{ step.label }}</span>
          <span v-if="step.status === 'working'" class="agent-step__spinner" />
          <span v-else-if="step.status === 'done'" class="agent-step__check">✓</span>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="showTypingIndicator && !isAgentWorking" class="typing-row">
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

    <button
      v-if="showJumpToBottom"
      class="chat-message-list__jump"
      type="button"
      aria-label="回到底部"
      title="回到底部"
      @click="handleJumpToBottom"
    >
      <span class="chat-message-list__jump-dot" />
      <span class="chat-message-list__jump-dot" />
      <span class="chat-message-list__jump-dot" />
    </button>
  </div>
</template>

<style scoped>
.chat-message-list-shell {
  position: relative;
  flex: 1;
  min-height: 0;
}

.chat-message-list {
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  padding: 24px 24px calc(var(--chat-input-reserve, 112px) + 24px);
  background: transparent;
  scroll-behavior: smooth;
  scroll-padding-bottom: var(--chat-input-reserve, 112px);
}

.chat-message-list__inner {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 100%;
  margin: 0;
  width: 100%;
}

.chat-message-list__jump {
  position: absolute;
  left: 50%;
  bottom: var(--chat-jump-bottom, 92px);
  z-index: 7;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 54px;
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  color: var(--accent-primary);
  cursor: pointer;
  transform: translateX(-50%);
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.chat-message-list__jump:hover {
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14px 34px rgba(15, 23, 42, 0.15);
  transform: translateX(-50%) translateY(-1px);
}

.chat-message-list__jump-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: jump-dot-pulse 1.2s ease-in-out infinite;
}

.chat-message-list__jump-dot:nth-child(2) {
  animation-delay: 0.12s;
}

.chat-message-list__jump-dot:nth-child(3) {
  animation-delay: 0.24s;
}

@keyframes jump-dot-pulse {
  0%, 80%, 100% {
    opacity: 0.45;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
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

/* Agent steps */
.agent-steps {
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  max-width: 420px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.agent-step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  transition: opacity 0.2s ease;
}

.agent-step--pending {
  opacity: 0.35;
}

.agent-step--working {
  opacity: 1;
  color: var(--accent-primary);
  font-weight: 500;
}

.agent-step--done {
  opacity: 0.6;
}

.agent-step__icon {
  font-size: 15px;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
}

.agent-step__name {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.agent-step--pending .agent-step__name {
  color: var(--text-secondary);
}

.agent-step__label {
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-step__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
  margin-left: auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.agent-step__check {
  color: var(--status-success);
  font-weight: 700;
  font-size: 14px;
  margin-left: auto;
  flex-shrink: 0;
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
