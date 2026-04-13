<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()

const sessions = computed(() => chatStore.sessions)
const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
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
  const isToday = date.toDateString() === now.toDateString()
  if (isToday) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<template>
  <div class="chat-view">
    <!-- Left panel: session list -->
    <aside class="chat-view__sidebar">
      <div class="chat-view__sidebar-header">
        <el-button type="primary" @click="handleCreateSession" class="new-session-btn">
          + 新对话
        </el-button>
      </div>

      <el-menu
        :default-active="activeSessionId"
        class="chat-view__session-menu"
        @select="handleSelectSession"
      >
        <el-menu-item
          v-for="session in sessions"
          :key="session.session_id"
          :index="session.session_id"
        >
          <div class="session-item">
            <span class="session-item__title">{{ session.title }}</span>
            <span class="session-item__time">{{ formatSessionTime(session.updated_at) }}</span>
          </div>
        </el-menu-item>
      </el-menu>
    </aside>

    <!-- Right panel: messages + input -->
    <main class="chat-view__main">
      <ChatMessageList
        :messages="activeMessages"
        :is-streaming="isStreaming"
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
}

.chat-view__sidebar {
  width: 260px;
  flex-shrink: 0;
  border-right: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  background: #fff;
}

.chat-view__sidebar-header {
  padding: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.new-session-btn {
  width: 100%;
}

.chat-view__session-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none;
}

.chat-view__session-menu .el-menu-item {
  height: auto;
  line-height: normal;
  padding: 12px 16px !important;
}

.session-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  overflow: hidden;
}

.session-item__title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-item__time {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
}

.chat-view__main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}
</style>
