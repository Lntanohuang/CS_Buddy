<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, shallowRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { upsertUserProfile } from '@/api/profile'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { welcomeQuestions } from '@/mock/data'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'
import type { UserProfile } from '@/types'
import type { WelcomeOption, WelcomeQuestion } from '@/mock/data'

type WelcomeMessage = {
  role: 'USER' | 'ASSISTANT'
  content: string
}

type DialogueProfile = {
  major: string
  learning_goal: string
  current_level: string
  preferred_style: string
  cognitive_style: UserProfile['cognitive_style']
  daily_time_minutes: number
  subjects: string[]
}

type WelcomeAnswerValue = string | number | string[]

const TYPING_DELAY_MS = 450

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const messagesContainer = ref<HTMLElement | null>(null)
const visibleMessages = ref<WelcomeMessage[]>([])
const answers = ref<Partial<Record<string, WelcomeAnswerValue>>>({})
const currentQuestionIndex = shallowRef(0)
const isTyping = shallowRef(false)
const dialogueComplete = shallowRef(false)
const showButton = shallowRef(false)
const headerVisible = shallowRef(false)
const isUnmounted = shallowRef(false)
const isSubmitting = shallowRef(false)
const textAnswer = ref('')
const multiSelectedValues = ref<string[]>([])

const isProfileRefreshFlow = computed(() => route.query.mode === 'refresh-profile')

const refreshReturnPath = computed(() => {
  const target = route.query.redirect
  if (typeof target === 'string' && target.startsWith('/app/')) {
    return target
  }
  return '/app/profile'
})

const welcomeTitle = computed(() =>
  isProfileRefreshFlow.value ? '🌿 欢迎回来，更新你的学习画像' : '🌿 欢迎加入CS Buddy',
)

const welcomeSubtitle = computed(() =>
  isProfileRefreshFlow.value
    ? '我们将通过同样的问答快速更新你的个人画像'
    : '让我们通过一段对话来了解你',
)

const totalQuestions = computed(() => welcomeQuestions.length)
const answeredCount = computed(() => Object.keys(answers.value).length)
const currentQuestion = computed<WelcomeQuestion | null>(() => {
  if (dialogueComplete.value) return null
  return welcomeQuestions[currentQuestionIndex.value] ?? null
})

const canSubmitTextAnswer = computed(() => {
  const question = currentQuestion.value
  if (!question || (question.type !== 'text' && question.type !== 'number')) return false

  // 防御:Vue 3 v-model 在 <input type="number"> 上返回 number,直接 .trim() 会炸
  const trimmed = String(textAnswer.value ?? '').trim()
  if (question.required === false && trimmed.length === 0) return true
  if (trimmed.length === 0) return false

  if (question.type === 'number') {
    const value = Number(trimmed)
    if (!Number.isFinite(value)) return false
    if (question.min !== undefined && value < question.min) return false
    if (question.max !== undefined && value > question.max) return false
  }

  return true
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

function getOptionLabel(question: WelcomeQuestion, value: string) {
  return question.options?.find((option) => option.value === value)?.label ?? value
}

function isMultiOptionSelected(value: string) {
  return multiSelectedValues.value.includes(value)
}

function toCognitiveStyle(value: WelcomeAnswerValue | undefined): UserProfile['cognitive_style'] {
  if (value === 'THEORETICAL' || value === 'PRACTICAL' || value === 'VISUAL' || value === 'MIXED') {
    return value
  }
  throw new Error('Invalid cognitive_style answer')
}

function requireStringAnswer(id: string) {
  const value = answers.value[id]
  if (typeof value !== 'string') {
    throw new Error(`Missing ${id} answer`)
  }
  return value
}

function requireNumberAnswer(id: string) {
  const value = answers.value[id]
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`Missing ${id} answer`)
  }
  return value
}

function requireStringArrayAnswer(id: string) {
  const value = answers.value[id]
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string')) {
    throw new Error(`Missing ${id} answer`)
  }
  return value
}

function buildDialogueProfile(): DialogueProfile {
  return {
    major: requireStringAnswer('major'),
    learning_goal: requireStringAnswer('learning_goal'),
    current_level: requireStringAnswer('current_level'),
    preferred_style: requireStringAnswer('preferred_style'),
    cognitive_style: toCognitiveStyle(answers.value.cognitive_style),
    daily_time_minutes: requireNumberAnswer('daily_time_minutes'),
    subjects: requireStringArrayAnswer('subjects'),
  }
}

function formatAnswerForBubble(question: WelcomeQuestion, value: WelcomeAnswerValue) {
  if (question.type === 'number') return `${value} 分钟`
  if (question.type === 'single' && typeof value === 'string') return getOptionLabel(question, value)
  if (question.type === 'multi' && Array.isArray(value)) {
    return value.map((item) => getOptionLabel(question, item)).join(', ')
  }
  return String(value)
}

function resetInputForQuestion(question: WelcomeQuestion | null) {
  textAnswer.value = ''
  multiSelectedValues.value = question?.type === 'multi' ? [] : []
}

async function showQuestion(question: WelcomeQuestion) {
  if (isUnmounted.value) return
  isTyping.value = true
  scrollToBottom()
  await wait(TYPING_DELAY_MS)
  if (isUnmounted.value) return
  isTyping.value = false
  visibleMessages.value = [...visibleMessages.value, { role: 'ASSISTANT', content: question.prompt }]
  resetInputForQuestion(question)
  scrollToBottom()
}

async function moveToNextQuestion() {
  if (isUnmounted.value) return

  const nextIndex = currentQuestionIndex.value + 1
  if (nextIndex >= welcomeQuestions.length) {
    dialogueComplete.value = true
    showButton.value = true
    scrollToBottom()
    return
  }

  currentQuestionIndex.value = nextIndex
  await showQuestion(welcomeQuestions[nextIndex])
}

async function submitAnswer(question: WelcomeQuestion, value: WelcomeAnswerValue) {
  if (isTyping.value || dialogueComplete.value || isUnmounted.value) return

  answers.value = { ...answers.value, [question.id]: value }
  visibleMessages.value = [
    ...visibleMessages.value,
    { role: 'USER', content: formatAnswerForBubble(question, value) },
  ]
  scrollToBottom()
  await moveToNextQuestion()
}

async function submitTextAnswer() {
  const question = currentQuestion.value
  if (!question || !canSubmitTextAnswer.value) return

  const trimmed = String(textAnswer.value ?? '').trim()
  const value = question.type === 'number' ? Number(trimmed) : trimmed
  await submitAnswer(question, value)
}

async function submitSingleOption(option: WelcomeOption) {
  const question = currentQuestion.value
  if (!question || question.type !== 'single') return
  await submitAnswer(question, option.value)
}

function toggleMultiOption(value: string) {
  const selected = multiSelectedValues.value
  multiSelectedValues.value = selected.includes(value)
    ? selected.filter((item) => item !== value)
    : [...selected, value]
}

async function submitMultiAnswer() {
  const question = currentQuestion.value
  if (!question || question.type !== 'multi' || multiSelectedValues.value.length === 0) return
  await submitAnswer(question, [...multiSelectedValues.value])
}

async function applyProfileUpdateAndRedirect(targetPath: string) {
  const profileStore = useProfileStore()
  const dialogueProfile = buildDialogueProfile()

  profileStore.initFromDialogue(dialogueProfile)
  const userId = authStore.user?.user_id
  if (userId) {
    try {
      await upsertUserProfile(userId, {
        ...dialogueProfile,
        knowledge_mastery: profileStore.profile.knowledge_mastery,
        error_patterns: profileStore.profile.error_patterns,
        weak_points: profileStore.profile.weak_points,
        style_weights: profileStore.profile.style_weights,
        profile_complete: true,
      })
    } catch (error) {
      console.warn('Profile persistence failed; continuing with local profile:', error)
    }
  }

  authStore.completeProfile()
  await router.push(targetPath)
}

async function handleStart() {
  if (isSubmitting.value || !dialogueComplete.value) return
  isSubmitting.value = true

  try {
    if (isProfileRefreshFlow.value) {
      await applyProfileUpdateAndRedirect(refreshReturnPath.value)
      return
    }

    await applyProfileUpdateAndRedirect('/app/chat')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  isUnmounted.value = false
  createTimer(() => {
    if (isUnmounted.value) return
    headerVisible.value = true
  }, 100)
  createTimer(() => {
    if (isUnmounted.value) return
    const firstQuestion = welcomeQuestions[0]
    if (firstQuestion) {
      void showQuestion(firstQuestion)
    } else {
      dialogueComplete.value = true
      showButton.value = true
    }
  }, 500)
})

onUnmounted(() => {
  isUnmounted.value = true
  timers.forEach(clearTimeout)
  timers = []
  pendingWaitResolvers.forEach((resolve) => resolve())
  pendingWaitResolvers.clear()

  messagesContainer.value = null
  visibleMessages.value = []
  answers.value = {}
  currentQuestionIndex.value = 0
  isTyping.value = false
  dialogueComplete.value = false
  showButton.value = false
  headerVisible.value = false
  isSubmitting.value = false
  textAnswer.value = ''
  multiSelectedValues.value = []
})
</script>

<template>
  <div class="welcome-page">
    <div class="welcome-container">
      <div class="welcome-header" :class="{ visible: headerVisible }">
        <h1 class="welcome-title">{{ welcomeTitle }}</h1>
        <p class="welcome-subtitle">{{ welcomeSubtitle }}</p>
      </div>

      <div class="progress-indicator">
        {{ answeredCount }}/{{ totalQuestions }} 已答
      </div>

      <div ref="messagesContainer" class="messages-container">
        <div
          v-for="(msg, idx) in visibleMessages"
          :key="`${msg.role}-${idx}`"
          class="message-row"
          :class="msg.role === 'ASSISTANT' ? 'assistant' : 'user'"
        >
          <div v-if="msg.role === 'ASSISTANT'" class="avatar assistant-avatar">🌿</div>

          <div class="message-bubble" :class="msg.role === 'ASSISTANT' ? 'assistant-bubble' : 'user-bubble'">
            <MarkdownRenderer v-if="msg.role === 'ASSISTANT'" :content="msg.content" />
            <span v-else>{{ msg.content }}</span>
          </div>

          <div v-if="msg.role === 'USER'" class="avatar user-avatar">{{ userInitial }}</div>
        </div>

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

        <div v-if="currentQuestion && !isTyping" class="welcome-answer-area">
          <form
            v-if="currentQuestion.type === 'text' || currentQuestion.type === 'number'"
            class="answer-form"
            @submit.prevent="submitTextAnswer"
          >
            <input
              v-model="textAnswer"
              class="answer-input"
              :type="currentQuestion.type === 'number' ? 'number' : 'text'"
              :placeholder="currentQuestion.placeholder"
              :min="currentQuestion.min"
              :max="currentQuestion.max"
              :data-testid="`welcome-input-${currentQuestion.id}`"
              autocomplete="off"
            >
            <button
              class="answer-next-btn"
              type="submit"
              :disabled="!canSubmitTextAnswer"
              data-testid="welcome-next"
            >
              下一题
            </button>
          </form>

          <div v-else-if="currentQuestion.type === 'single'" class="option-list">
            <button
              v-for="option in currentQuestion.options"
              :key="option.value"
              class="option-chip"
              type="button"
              :data-testid="`welcome-option-${option.value}`"
              @click="submitSingleOption(option)"
            >
              {{ option.label }}
            </button>
          </div>

          <div v-else-if="currentQuestion.type === 'multi'" class="multi-answer">
            <div class="option-list">
              <button
                v-for="option in currentQuestion.options"
                :key="option.value"
                class="option-chip"
                :class="{ 'option-chip--active': isMultiOptionSelected(option.value) }"
                type="button"
                :aria-pressed="isMultiOptionSelected(option.value)"
                :data-testid="`welcome-option-${option.value}`"
                @click="toggleMultiOption(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
            <button
              class="answer-next-btn"
              type="button"
              :disabled="multiSelectedValues.length === 0"
              data-testid="welcome-next"
              @click="submitMultiAnswer"
            >
              下一题
            </button>
          </div>
        </div>

        <div v-if="showButton" class="cta-wrapper">
          <button class="cta-btn" :disabled="isSubmitting" data-testid="welcome-start" @click="handleStart">
            {{ isSubmitting ? '处理中...' : '开始学习' }}
          </button>
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

.progress-indicator {
  text-align: center;
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

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

.welcome-answer-area {
  padding: 8px 0 4px 42px;
  animation: fadeIn 0.2s ease;
}

.answer-form,
.multi-answer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-input {
  width: min(100%, 420px);
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.answer-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-light);
}

.option-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.option-chip {
  padding: 9px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.option-chip:hover,
.option-chip--active {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.answer-next-btn {
  align-self: flex-start;
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 14px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.answer-next-btn:hover {
  background: var(--accent-primary-hover);
}

.answer-next-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

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

.cta-btn:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

.messages-container::-webkit-scrollbar {
  width: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}

@media (max-width: 480px) {
  .welcome-page {
    padding: 28px 16px;
  }

  .welcome-container {
    height: calc(100vh - 56px);
  }

  .welcome-title {
    font-size: 22px;
  }

  .message-bubble {
    max-width: 90%;
  }

  .welcome-answer-area {
    padding-left: 0;
  }
}
</style>
