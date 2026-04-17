<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useNotificationStore } from '@/stores/notification'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import RecommendCard from '@/components/notification/RecommendCard.vue'

const chatStore = useChatStore()
const notificationStore = useNotificationStore()

const showRecommend = shallowRef(true)
const recommendation = computed(() => notificationStore.todayRecommendation)

function handleStartRecommend() {
  if (recommendation.value) {
    chatStore.sendMessage(`帮我学习${recommendation.value.title}`)
    showRecommend.value = false
  }
}

function handleDismissRecommend() {
  showRecommend.value = false
}

const sessions = computed(() => chatStore.sessions)
const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)
const activeSessionId = computed(() => chatStore.activeSessionId)

function handleSelectSession(id: string) {
  chatStore.selectSession(id)
}

function handleCreateSession() {
  chatStore.createSession()
}

function handleSend(text: string) {
  chatStore.sendMessage(text)
}

function formatSessionTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHr < 24) return `${diffHr}小时前`
  if (diffDay < 7) return `${diffDay}天前`

  const isToday = date.toDateString() === now.toDateString()
  if (isToday) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div class="chat-view">
    <!-- Left sidebar -->
    <aside class="chat-sidebar">
      <div class="chat-sidebar__header">
        <button class="new-session-btn" @click="handleCreateSession">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>新对话</span>
        </button>
      </div>

      <div class="chat-sidebar__section-label">对话记录</div>

      <div class="chat-sidebar__list">
        <button
          v-for="session in sessions"
          :key="session.session_id"
          class="session-card"
          :class="{ 'session-card--active': session.session_id === activeSessionId }"
          @click="handleSelectSession(session.session_id)"
        >
          <span class="session-card__title">{{ session.title }}</span>
          <span class="session-card__time">{{ formatSessionTime(session.updated_at) }}</span>
        </button>
      </div>
    </aside>

    <!-- Right main area -->
    <main class="chat-main">
      <RecommendCard
        v-if="showRecommend && recommendation"
        :title="recommendation.title"
        :reason="recommendation.reason"
        :est-minutes="recommendation.est_minutes"
        class="chat-recommend"
        @start="handleStartRecommend"
        @dismiss="handleDismissRecommend"
      />
      <ChatMessageList
        :messages="activeMessages"
        :is-streaming="isStreaming"
        :agent-steps="agentSteps"
        :is-agent-working="isAgentWorking"
      />
      <ChatInput
        :disabled="isStreaming"
        @send="handleSend"
      />
    </main>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  height: 100%;
  overflow: hidden;
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg-primary);
}

/* Sidebar */
.chat-sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--bg-hover);
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
}

.chat-sidebar__header {
  padding: 16px;
}

.new-session-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--accent-primary);
  color: var(--bg-card);
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  font-family: system-ui, -apple-system, sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

.new-session-btn:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.new-session-btn:active {
  transform: translateY(0);
}

.chat-sidebar__section-label {
  padding: 8px 20px 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.chat-sidebar__list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Session cards */
.session-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 10px;
  background: transparent;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
  border-left: 3px solid transparent;
  font-family: system-ui, -apple-system, sans-serif;
}

.session-card:hover {
  background: var(--bg-primary);
}

.session-card--active {
  background: var(--accent-primary-light);
  border-left-color: var(--accent-primary);
}

.session-card--active:hover {
  background: var(--accent-primary-light);
}

.session-card__title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.session-card--active .session-card__title {
  color: var(--accent-primary);
  font-weight: 600;
}

.session-card__time {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.3;
}

/* Main content */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.chat-recommend {
  margin: 16px 16px 0;
  flex-shrink: 0;
}
</style>
