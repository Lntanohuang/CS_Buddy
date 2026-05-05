import type { LearningPath, EvalRecommendation } from '@/types'

export async function getActiveLearningPath(userId: string): Promise<LearningPath> {
  const params = new URLSearchParams({ user_id: userId })
  const res = await fetch(`/api/v1/learning-paths/active?${params.toString()}`)

  if (!res.ok) {
    throw new Error(`学习路径加载失败: ${res.status}`)
  }

  return await res.json() as LearningPath
}

export async function adjustLearningPath(
  userId: string,
  knowledgePoint: string,
  action: EvalRecommendation['action'],
): Promise<LearningPath> {
  const res = await fetch('/api/v1/learning-paths/adjust', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      knowledge_point: knowledgePoint,
      action,
    }),
  })

  if (!res.ok) {
    throw new Error(`学习路径调整失败: ${res.status}`)
  }

  return await res.json() as LearningPath
}
