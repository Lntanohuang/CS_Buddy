<script setup lang="ts">
import { ref, shallowRef, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { welcomeDialogueScript } from '@/mock/data'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const router = useRouter()
const authStore = useAuthStore()

const messagesContainer = ref<HTMLElement | null>(null)
const visibleMessages = ref<typeof welcomeDialogueScript>([])
const isTyping = shallowRef(false)
const dialogueComplete = shallowRef(false)
const showButton = shallowRef(false)
const headerVisible = shallowRef(false)
const isUnmounted = shallowRef(false)

// Count dialogue rounds (each ASSISTANT+USER pair = 1 round)
const totalRounds = computed(() => {
  let count = 0
  for (const msg of welcomeDialogueScript) {
    if (msg.role === 'ASSISTANT') count++
  }
  return count
})

const currentRound = computed(() => {
  let count = 0
  for (const msg of visibleMessages.value) {
    if (msg.role === 'ASSISTANT') count++
  }
  return count
})

const userInitial = computed(() => {
  const name = authStore.nickname
  return name ? name.charAt(0).toUpperCase() : '?'
})

let timers: ReturnType<typeof setTimeout>[] = []
const pendingWaitResolvers = new Set<() => void>()

function createTimer(callback: () => void, ms: number) {
  const id = setTimeout(() => {
    timers = timers.filter((timer) => timer !== id)
    callback()
  }, ms)
  timers.push(id)
  return id
}

function scrollToBottom() {
  if (isUnmounted.value) return
  nextTick(() => {
    if (isUnmounted.value) return
    if (messagesContainer.value) {
      messagesContainer.value.scrollTo({
        top: messagesContainer.value.scrollHeight,
        behavior: 'smooth',
      })
    }
  })
}

async function playDialogue() {
  if (welcomeDialogueScript.length === 0) {
    dialogueComplete.value = true
    showButton.value = true
    return
  }

  for (let i = 0; i < welcomeDialogueScript.length; i++) {
    if (isUnmounted.value) return
    const msg = welcomeDialogueScript[i]
    const delay = msg.delay || 400

    if (msg.role === 'ASSISTANT') {
      // Show typing indicator
      isTyping.value = true
      scrollToBottom()
      await wait(delay + 600)
      if (isUnmounted.value) return
      isTyping.value = false
    } else {
      // USER message — short pause
      await wait(400)
      if (isUnmounted.value) return
    }

    visibleMessages.value = [...visibleMessages.value, msg]
    scrollToBottom()
  }

  if (isUnmounted.value) return
  dialogueComplete.value = true
  await wait(500)
  if (isUnmounted.value) return
  showButton.value = true
  scrollToBottom()
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    if (isUnmounted.value) {
      resolve()
      return
    }

    const done = () => {
      pendingWaitResolvers.delete(done)
      resolve()
    }

    pendingWaitResolvers.add(done)
    createTimer(done, ms)
  })
}

async function handleStart() {
  authStore.completeProfile()
  router.push('/app/chat')
}

onMounted(() => {
  isUnmounted.value = false
  // Fade in header first, then start dialogue
  createTimer(() => {
    if (isUnmounted.value) return
    headerVisible.value = true
  }, 100)
  createTimer(() => {
    if (isUnmounted.value) return
    void playDialogue()
  }, 800)
})

onUnmounted(() => {
  isUnmounted.value = true
  timers.forEach(clearTimeout)
  timers = []
  pendingWaitResolvers.forEach((resolve) => resolve())
  pendingWaitResolvers.clear()

  messagesContainer.value = null
  visibleMessages.value = []
  isTyping.value = false
  dialogueComplete.value = false
  showButton.value = false
  headerVisible.value = false
})
</script>

<template>
  <div class="welcome-page">
    <div class="welcome-container">
      <!-- Header -->
      <div class="welcome-header" :class="{ visible: headerVisible }">
        <h1 class="welcome-title">🌿 欢迎加入智伴</h1>
        <p class="welcome-subtitle">让我们通过一段对话来了解你</p>
      </div>

      <!-- Progress -->
      <div v-if="currentRound > 0" class="progress-indicator">
        第 {{ currentRound }}/{{ totalRounds }} 轮
      </div>

      <!-- Chat area -->
      <div ref="messagesContainer" class="messages-container">
        <div
          v-for="(msg, idx) in visibleMessages"
          :key="idx"
          class="message-row"
          :class="msg.role === 'ASSISTANT' ? 'assistant' : 'user'"
        >
          <!-- Avatar -->
          <div v-if="msg.role === 'ASSISTANT'" class="avatar assistant-avatar">🌿</div>

          <!-- Bubble -->
          <div class="message-bubble" :class="msg.role === 'ASSISTANT' ? 'assistant-bubble' : 'user-bubble'">
            <MarkdownRenderer v-if="msg.role === 'ASSISTANT'" :content="msg.content" />
            <span v-else>{{ msg.content }}</span>
          </div>

          <!-- User avatar -->
          <div v-if="msg.role === 'USER'" class="avatar user-avatar">{{ userInitial }}</div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isTyping" class="message-row assistant">
          <div class="avatar assistant-avatar">🌿</div>
          <div class="message-bubble assistant-bubble typing-bubble">
            <span class="typing-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </span>
          </div>
        </div>

        <!-- CTA button -->
        <div v-if="showButton" class="cta-wrapper">
          <button class="cta-btn" @click="handleStart">开始学习</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.welcome-page {
  min-height: 100vh;
  background: var(--bg-primary);
  display: flex;
  justify-content: center;
  padding: 40px 24px;
  animation: pageFadeIn 0.4s ease;
}

@keyframes pageFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.welcome-container {
  width: 100%;
  max-width: 680px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
}

/* Header */
.welcome-header {
  text-align: center;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 20px;
  opacity: 0;
  transform: scale(0.9);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.welcome-header.visible {
  opacity: 1;
  transform: scale(1);
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
}

/* Progress */
.progress-indicator {
  text-align: center;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

/* Messages */
.messages-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 24px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-row.user {
  justify-content: flex-end;
}

/* Avatars */
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
  margin-top: 2px;
}

.assistant-avatar {
  background: var(--accent-primary-light);
  font-size: 16px;
}

.user-avatar {
  background: var(--accent-primary);
  color: var(--bg-card);
  font-weight: 600;
  font-size: 13px;
}

/* Bubbles */
.message-bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.assistant-bubble {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 2px 12px 12px 12px;
  color: var(--text-primary);
}

.user-bubble {
  background: var(--accent-primary-light);
  border-radius: 12px 2px 12px 12px;
  color: var(--text-primary);
}

/* Typing dots */
.typing-bubble {
  padding: 14px 20px;
}

.typing-dots {
  display: flex;
  gap: 5px;
  align-items: center;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: bounce 1.2s infinite;
}

.dot:nth-child(2) {
  animation-delay: 0.15s;
}

.dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

/* CTA */
.cta-wrapper {
  display: flex;
  justify-content: center;
  padding: 16px 0;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.cta-btn {
  padding: 12px 48px;
  border: none;
  border-radius: 8px;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 16px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease;
}

.cta-btn:hover {
  background: var(--accent-primary-hover);
}

/* Scrollbar */
.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 22px;
  }

  .message-bubble {
    max-width: 90%;
  }
}
</style>
