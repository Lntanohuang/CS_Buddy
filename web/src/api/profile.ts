import type { UserProfile } from '@/types'

export async function upsertUserProfile(
  userId: string,
  updates: Partial<UserProfile>,
): Promise<UserProfile> {
  const res = await fetch(`/api/v1/profile/${encodeURIComponent(userId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  })

  if (!res.ok) {
    throw new Error(`画像保存失败: ${res.status}`)
  }

  return await res.json() as UserProfile
}
