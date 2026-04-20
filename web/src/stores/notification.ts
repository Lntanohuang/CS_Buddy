import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Notification, NotificationMessage, NotificationType } from '@/types'

type IncomingNotification = {
  type: NotificationType
  title: string
  content: string
  actionUrl?: string
  action_url?: string
}

const DEFAULT_MESSAGES: IncomingNotification[] = [
  {
    type: 'DAILY_RECOMMEND',
    title: '今日学习建议已刷新',
    content: '建议优先完成“二叉树遍历 + 图搜索对比”专题，预计 35 分钟。',
    actionUrl: '/app/profile',
  },
  {
    type: 'EVAL_RESULT',
    title: '多模态测评结果已生成',
    content: '你的图示理解显著领先，建议补强口述分析与复杂度表达。',
    actionUrl: '/app/evaluate',
  },
  {
    type: 'STUDY_REMINDER',
    title: '晚间学习窗口即将开始',
    content: '保持 25 分钟沉浸学习，再用 10 分钟做图文复盘，效率会更高。',
    actionUrl: '/app/chat',
  },
]

const DEFAULT_RECOMMENDATION = {
  knowledge_point: 'binary_tree',
  title: '二叉树遍历联动训练',
  reason: '它能同时锻炼树结构理解、递归边界意识和图示迁移能力。',
  est_minutes: 35,
  path_node_id: 'node_binary_tree_focus',
}

function buildMessage(payload: IncomingNotification, createdAt = new Date().toISOString(), read = false): NotificationMessage {
  const actionUrl = payload.actionUrl ?? payload.action_url

  return {
    id: `noti_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    type: payload.type,
    title: payload.title,
    content: payload.content,
    time: createdAt,
    read,
    createdAt,
    is_read: read,
    created_at: createdAt,
    actionUrl,
    action_url: actionUrl,
  }
}

function syncReadState(message: NotificationMessage, read: boolean) {
  message.read = read
  message.is_read = read
}

export const useNotificationStore = defineStore('notification', () => {
  const messageList = ref<NotificationMessage[]>(
    DEFAULT_MESSAGES.map((message, index) =>
      buildMessage(
        message,
        new Date(Date.now() - index * 1000 * 60 * 45).toISOString(),
        index === DEFAULT_MESSAGES.length - 1,
      ),
    ),
  )
  const notifications = messageList
  const todayRecommendation = ref(DEFAULT_RECOMMENDATION)

  const unreadCount = computed(() => messageList.value.filter((message) => !message.read).length)

  function markRead(id: string) {
    markAsRead(id)
  }

  function markAllRead() {
    markAsRead()
  }

  function markAsRead(id?: string) {
    if (id) {
      const message = messageList.value.find((item) => item.id === id)
      if (message) syncReadState(message, true)
      return
    }

    messageList.value.forEach((message) => syncReadState(message, true))
  }

  function receiveNewMessage(payload?: Partial<IncomingNotification>) {
    const message = buildMessage({
      type: payload?.type ?? 'STUDY_REMINDER',
      title: payload?.title ?? '新的学习提醒',
      content: payload?.content ?? 'AI 导师刚刚为你生成了一条新的学习建议。',
      actionUrl: payload?.actionUrl,
      action_url: payload?.action_url,
    })
    messageList.value.unshift(message)
  }

  function addNotification(notification: Omit<Notification, 'id' | 'created_at' | 'is_read'>) {
    receiveNewMessage({
      type: notification.type,
      title: notification.title,
      content: notification.content,
      actionUrl: notification.actionUrl,
      action_url: notification.action_url,
    })
  }

  return {
    messageList,
    notifications,
    todayRecommendation,
    unreadCount,
    receiveNewMessage,
    markAsRead,
    markRead,
    markAllRead,
    addNotification,
  }
})
