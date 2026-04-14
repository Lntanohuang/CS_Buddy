import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Notification } from '@/types'
import { mockNotifications, mockTodayRecommendation } from '@/mock/data'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([...mockNotifications])
  const todayRecommendation = ref(mockTodayRecommendation)

  const unreadCount = computed(() => notifications.value.filter((n) => !n.is_read).length)

  function markRead(id: string) {
    const n = notifications.value.find((n) => n.id === id)
    if (n) n.is_read = true
  }

  function markAllRead() {
    notifications.value.forEach((n) => (n.is_read = true))
  }

  return { notifications, todayRecommendation, unreadCount, markRead, markAllRead }
})
