import type { Notification } from '@/types'

export async function listNotifications(userId: string, limit = 50): Promise<Notification[]> {
  const params = new URLSearchParams({ user_id: userId, limit: String(limit) })
  const res = await fetch(`/api/v1/notifications?${params.toString()}`)

  if (!res.ok) {
    throw new Error(`通知加载失败: ${res.status}`)
  }

  return await res.json() as Notification[]
}

export async function markNotificationRead(notificationId: string): Promise<Notification> {
  const res = await fetch(`/api/v1/notifications/${encodeURIComponent(notificationId)}/read`, {
    method: 'PATCH',
  })

  if (!res.ok) {
    throw new Error(`通知已读失败: ${res.status}`)
  }

  return await res.json() as Notification
}

export async function markAllNotificationsRead(userId: string): Promise<{ updated_count: number }> {
  const params = new URLSearchParams({ user_id: userId })
  const res = await fetch(`/api/v1/notifications/read-all?${params.toString()}`, {
    method: 'PATCH',
  })

  if (!res.ok) {
    throw new Error(`通知全部已读失败: ${res.status}`)
  }

  return await res.json() as { updated_count: number }
}
