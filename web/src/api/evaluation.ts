import type { Evaluation, EvalQuestion } from '@/types'

export async function createEvaluation(
  userId: string,
  knowledgePoint: string,
  type: Evaluation['type'] = 'MINI_QUIZ',
): Promise<Evaluation> {
  const res = await fetch('/api/v1/evaluations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      type,
      knowledge_point: knowledgePoint,
    }),
  })

  if (!res.ok) {
    throw new Error(`评估创建失败: ${res.status}`)
  }

  return await res.json() as Evaluation
}

export async function listEvaluations(userId: string, limit = 20): Promise<Evaluation[]> {
  const params = new URLSearchParams({
    user_id: userId,
    limit: String(limit),
  })
  const res = await fetch(`/api/v1/evaluations?${params.toString()}`)

  if (!res.ok) {
    throw new Error(`评估历史加载失败: ${res.status}`)
  }

  return await res.json() as Evaluation[]
}

export async function submitEvaluation(
  evalId: string,
  questions: EvalQuestion[],
  timeSpentSeconds?: number,
): Promise<Evaluation> {
  const res = await fetch(`/api/v1/evaluations/${encodeURIComponent(evalId)}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      answers: questions.map((question) => ({
        question_id: question.question_id,
        answer: question.user_answer ?? '',
      })),
      time_spent_seconds: timeSpentSeconds,
    }),
  })

  if (!res.ok) {
    throw new Error(`评估提交失败: ${res.status}`)
  }

  return await res.json() as Evaluation
}
