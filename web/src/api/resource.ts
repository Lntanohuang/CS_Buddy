import type { ResourceFeedback } from '@/types'

export async function submitResourceFeedback(
  payload: ResourceFeedback & { user_id?: string },
): Promise<Record<string, unknown>> {
  const res = await fetch('/api/v1/resources/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    throw new Error(`资源反馈提交失败: ${res.status}`)
  }

  return await res.json() as Record<string, unknown>
}
