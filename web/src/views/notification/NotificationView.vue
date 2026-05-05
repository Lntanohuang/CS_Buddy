<script setup lang="ts">
import { onMounted } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import type { Notification } from '@/types'

const router = useRouter()
const notificationStore = useNotificationStore()

const typeIcons: Record<Notification['type'], string> = {
  DAILY_RECOMMEND: '📘',
  EVAL_RESULT: '📊',
  STUDY_REMINDER: '🔔',
  INACTIVE_RECALL: '⏰',
  ACHIEVEMENT: '🏆',
}

function handleClick(notification: Notification) {
  notificationStore.markRead(notification.id)

  if (notification.action_url) {
    void router.push(notification.action_url)
  }
}

function handleDelete(id: string) {
  notificationStore.removeMessage(id)
}

function formatTime(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHr = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  if (diffHr < 24) return `${diffHr} 小时前`
  if (diffDay < 7) return `${diffDay} 天前`

  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  notificationStore.loadNotifications()
})
</script>

<template>
  <div class="notification-view">
    <div class="notification-header">
      <h2 class="notification-title">通知中心</h2>
      <button
        v-if="notificationStore.unreadCount > 0"
        class="mark-all-btn"
        @click="notificationStore.markAllRead()"
      >
        全部已读
      </button>
    </div>

    <div v-if="notificationStore.notifications.length === 0" class="empty-state">
      <span class="empty-icon">🔕</span>
      <p class="empty-text">暂无通知</p>
    </div>

    <div v-else class="notification-list">
      <div
        v-for="n in notificationStore.notifications"
        :key="n.id"
        class="notification-item"
        :class="{ 'notification-item--unread': !n.is_read }"
      >
        <span class="item-icon">{{ typeIcons[n.type] || '🔔' }}</span>
        <button class="item-main" type="button" @click="handleClick(n)">
          <div class="item-body">
            <span class="item-title">{{ n.title }}</span>
            <span class="item-content">{{ n.content }}</span>
            <span class="item-time">{{ formatTime(n.created_at) }}</span>
          </div>
        </button>
        <button
          class="item-delete"
          type="button"
          aria-label="删除消息"
          @click.stop="handleDelete(n.id)"
        >
          <el-icon :size="15"><Delete /></el-icon>
        </button>
        <span v-if="!n.is_read" class="unread-dot" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.notification-view {
  max-width: 680px;
  margin: 0 auto;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.notification-title {
  margin: 0;
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.mark-all-btn {
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: none;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease;
}

.mark-all-btn:hover {
  background: var(--accent-primary-light);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 12px;
}

.empty-icon {
  font-size: 32px;
  opacity: 0.4;
}

.empty-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.notification-list {
  display: flex;
  flex-direction: column;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
  background: none;
  transition: background 0.15s ease;
  width: 100%;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: var(--bg-hover);
}

.notification-item--unread {
  background: var(--accent-primary-light);
}

.notification-item--unread:hover {
  background: var(--accent-primary-light);
}

.item-icon {
  font-size: 18px;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 2px;
}

.item-main {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  padding: 0;
  text-align: left;
  cursor: pointer;
  font: inherit;
}

.item-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.4;
}

.notification-item--unread .item-title {
  font-weight: 600;
}

.item-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-time {
  margin-top: 2px;
  font-size: 11px;
  color: var(--text-secondary);
}

.item-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s ease, color 0.15s ease;
}

.item-delete:hover {
  background: rgba(196, 85, 77, 0.12);
  color: var(--status-error);
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-primary);
  flex-shrink: 0;
  margin-top: 6px;
}
</style>
