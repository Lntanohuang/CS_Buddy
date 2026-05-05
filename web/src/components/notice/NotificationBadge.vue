<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Delete } from '@element-plus/icons-vue'
import { useNotificationStore } from '@/stores/notification'
import type { NotificationMessage } from '@/types'

const router = useRouter()
const notificationStore = useNotificationStore()

const isAnimating = ref(false)

let animationTimer: ReturnType<typeof setTimeout> | null = null

const unreadCount = computed(() => notificationStore.unreadCount)
const messages = computed(() => notificationStore.messageList)

function formatTime(value: string) {
  const date = new Date(value)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  if (diffHour < 24) return `${diffHour} 小时前`

  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function playAnimation() {
  isAnimating.value = true

  if (animationTimer) {
    clearTimeout(animationTimer)
  }

  animationTimer = setTimeout(() => {
    isAnimating.value = false
    animationTimer = null
  }, 2400)
}

function openMessage(message: NotificationMessage) {
  notificationStore.markAsRead(message.id)

  if (message.actionUrl) {
    void router.push(message.actionUrl)
  } else if (message.action_url) {
    void router.push(message.action_url)
  } else {
    void router.push('/app/notifications')
  }
}

function deleteMessage(messageId: string) {
  notificationStore.removeMessage(messageId)
}

watch(
  () => notificationStore.unreadCount,
  (next, previous) => {
    if (next > (previous ?? 0)) {
      playAnimation()
    }
  },
)

onBeforeUnmount(() => {
  if (animationTimer) {
    clearTimeout(animationTimer)
  }
})

onMounted(() => {
  notificationStore.loadNotifications()
})
</script>

<template>
  <el-popover
    placement="bottom-end"
    trigger="click"
    :width="360"
    popper-class="notification-popover"
  >
    <template #reference>
      <button class="notification-trigger" :class="{ 'is-animating': isAnimating }" type="button">
        <el-icon :size="18"><Bell /></el-icon>
        <span v-if="unreadCount > 0" class="notification-badge">
          {{ unreadCount > 99 ? '99+' : unreadCount }}
        </span>
      </button>
    </template>

    <div class="notification-panel">
      <div class="notification-panel__header">
        <div>
          <p class="notification-panel__eyebrow">消息提醒</p>
          <h3 class="notification-panel__title">AI 学习通知流</h3>
        </div>
        <button
          v-if="unreadCount > 0"
          class="notification-panel__action"
          type="button"
          @click="notificationStore.markAsRead()"
        >
          全部已读
        </button>
      </div>

      <div v-if="messages.length === 0" class="notification-empty">
        暂无新的学习提醒
      </div>

      <div v-else class="notification-list">
        <div
          v-for="message in messages"
          :key="message.id"
          class="notification-item"
          :class="{ 'notification-item--unread': !message.read }"
        >
          <div class="notification-item__marker" />
          <button class="notification-item__main" type="button" @click="openMessage(message)">
            <div class="notification-item__body">
              <div class="notification-item__top">
                <span class="notification-item__title">{{ message.title }}</span>
                <span class="notification-item__time">{{ formatTime(message.createdAt) }}</span>
              </div>
              <p class="notification-item__content">{{ message.content }}</p>
            </div>
          </button>
          <button
            class="notification-item__delete"
            type="button"
            aria-label="删除消息"
            @click.stop="deleteMessage(message.id)"
          >
            <el-icon :size="15"><Delete /></el-icon>
          </button>
        </div>
      </div>
    </div>
  </el-popover>
</template>

<style scoped>
.notification-trigger {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border: 1px solid rgba(var(--accent-primary-rgb), 0.14);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.notification-trigger:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
  background: rgba(255, 255, 255, 0.96);
}

.notification-trigger.is-animating {
  animation: ring 0.55s ease-in-out 4;
}

.notification-trigger.is-animating::after {
  content: '';
  position: absolute;
  inset: -6px;
  border: 1px solid rgba(var(--accent-secondary-rgb), 0.72);
  border-radius: 18px;
  animation: ripple 1.2s ease-out 2;
}

.notification-badge {
  position: absolute;
  top: -6px;
  right: -4px;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: linear-gradient(135deg, #c4554d, #e17b71);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 20px;
  text-align: center;
  box-shadow: 0 10px 18px rgba(196, 85, 77, 0.24);
}

.notification-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: min(70vh, 520px);
}

.notification-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.notification-panel__eyebrow {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.notification-panel__title {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.notification-panel__action {
  border: none;
  border-radius: 999px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.notification-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  overflow-y: auto;
  padding-right: 4px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), color-mix(in srgb, var(--bg-primary) 92%, white));
  padding: 14px;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.notification-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.notification-item--unread {
  background: linear-gradient(180deg, var(--accent-primary-light), rgba(255, 255, 255, 0.96));
}

.notification-item__marker {
  width: 10px;
  height: 10px;
  margin-top: 7px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  box-shadow: 0 0 0 4px rgba(var(--accent-primary-rgb), 0.12);
  flex-shrink: 0;
}

.notification-item__body {
  flex: 1;
  min-width: 0;
}

.notification-item__main {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  padding: 0;
  text-align: left;
  cursor: pointer;
  font: inherit;
}

.notification-item__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.notification-item__title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.notification-item__time {
  font-size: 11px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.notification-item__content {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-tertiary);
}

.notification-item__delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  margin-top: 1px;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.62);
  color: var(--text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.18s ease, color 0.18s ease;
}

.notification-item__delete:hover {
  background: rgba(196, 85, 77, 0.12);
  color: var(--status-error);
}

.notification-empty {
  border-radius: 16px;
  padding: 24px 18px;
  text-align: center;
  background: var(--bg-primary);
  color: var(--text-secondary);
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  20% { transform: rotate(-12deg); }
  40% { transform: rotate(10deg); }
  60% { transform: rotate(-8deg); }
  80% { transform: rotate(6deg); }
}

@keyframes ripple {
  0% {
    opacity: 0.8;
    transform: scale(0.85);
  }
  100% {
    opacity: 0;
    transform: scale(1.25);
  }
}
</style>
