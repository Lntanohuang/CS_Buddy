import { ref, shallowRef } from 'vue'
import { defineStore } from 'pinia'
import type { Evaluation } from '@/types'
import { mockEvaluation, mockEvalHistory } from '@/mock/data'
import { useProfileStore } from './profile'
import { usePathStore } from './path'
import { useNotificationStore } from './notification'

export const useEvalStore = defineStore('eval', () => {
  const history = ref<Evaluation[]>([...mockEvalHistory])
  const activeEval = ref<Evaluation | null>(null)
  const isSubmitting = shallowRef(false)

  function startEval(knowledgePoint: string) {
    activeEval.value = {
      ...mockEvaluation,
      eval_id: `eval_${Date.now()}`,
      knowledge_point: knowledgePoint,
      questions: mockEvaluation.questions.map((q) => ({ ...q })),
      created_at: new Date().toISOString(),
    }
  }

  function submitAnswer(questionId: string, answer: string) {
    if (!activeEval.value) return
    const q = activeEval.value.questions.find((q) => q.question_id === questionId)
    if (q) {
      q.user_answer = answer
    }
  }

  async function submitEval() {
    if (!activeEval.value) return

    isSubmitting.value = true
    // Simulate AI analysis delay
    await new Promise((r) => setTimeout(r, 1000))

    let correct = 0
    for (const q of activeEval.value.questions) {
      q.is_correct =
        (q.user_answer ?? '').trim().toLowerCase() ===
        q.correct_answer.trim().toLowerCase()
      if (q.is_correct) correct++
    }

    const score = Math.round((correct / activeEval.value.question_count) * 100)
    const mastery = Number((correct / activeEval.value.question_count).toFixed(2))

    activeEval.value.score = score
    activeEval.value.correct_count = correct
    activeEval.value.mastery_level = mastery
    activeEval.value.status = 'ANALYZED'

    // Calculate learning_efficiency: correct_rate * speed_factor, capped at 1.0
    const timeSpent = activeEval.value.time_spent_seconds ?? 180
    const speedFactor = 180 / timeSpent
    const correctRate = correct / activeEval.value.question_count
    activeEval.value.learning_efficiency = Math.min(1.0, Number((correctRate * speedFactor).toFixed(2)))

    // Calculate progress_trend by comparing with last eval of the same knowledge_point
    const kp = activeEval.value.knowledge_point
    const prevEval = history.value.find((e) => e.knowledge_point === kp && e.status === 'ANALYZED')
    if (prevEval && prevEval.mastery_level != null) {
      if (mastery > prevEval.mastery_level) {
        activeEval.value.progress_trend = 'UP'
      } else if (mastery < prevEval.mastery_level) {
        activeEval.value.progress_trend = 'DOWN'
      } else {
        activeEval.value.progress_trend = 'STABLE'
      }
    } else {
      // First eval for this knowledge point — treat as stable baseline
      activeEval.value.progress_trend = 'STABLE'
    }

    // Build weak_point_analysis from wrong answers
    const weakPoints: string[] = []
    activeEval.value.questions.forEach((q, idx) => {
      if (!q.is_correct) {
        const brief = q.content.length > 30 ? q.content.slice(0, 30) + '...' : q.content
        weakPoints.push(`第${idx + 1}题: ${brief}`)
      }
    })
    activeEval.value.weak_point_analysis = weakPoints

    if (mastery >= 0.7) {
      activeEval.value.recommendation = {
        action: 'ADVANCE',
        message: '掌握良好！建议继续学习下一个知识点。',
        next_node_id: 'node_006',
      }
    } else if (mastery >= 0.4) {
      activeEval.value.recommendation = {
        action: 'SUPPLEMENT',
        message: '部分掌握，建议进行补充练习。',
      }
    } else {
      activeEval.value.recommendation = {
        action: 'RETREAT',
        message: '掌握不足，建议回顾前置知识点。',
      }
    }

    // Update profile mastery + error_patterns
    const profileStore = useProfileStore()
    profileStore.updateMastery(activeEval.value.knowledge_point, mastery)
    if (weakPoints.length > 0) {
      const existingPatterns = new Set(profileStore.profile.error_patterns)
      for (const wp of weakPoints) {
        existingPatterns.add(wp)
      }
      profileStore.updateProfile({ error_patterns: Array.from(existingPatterns) })
    }

    // Update learning path based on recommendation
    const pathStore = usePathStore()
    const action = activeEval.value.recommendation?.action
    if (action) {
      pathStore.reorderAfterEval(activeEval.value.knowledge_point, action)
    }

    // Send notifications
    const notificationStore = useNotificationStore()
    notificationStore.addNotification({
      type: 'EVAL_RESULT',
      title: `${activeEval.value.knowledge_point} 测评已完成`,
      content: `得分 ${score} 分，掌握度 ${Math.round(mastery * 100)}%`,
      action_url: '/app/evaluate',
    })
    notificationStore.addNotification({
      type: 'STUDY_REMINDER',
      title: '学习路径已调整',
      content: `根据「${activeEval.value.knowledge_point}」测评结果，已优化你的学习路径`,
      action_url: '/app/path',
    })

    history.value.unshift({ ...activeEval.value })
    isSubmitting.value = false
  }

  function clearActiveEval() {
    activeEval.value = null
  }

  return {
    history,
    activeEval,
    isSubmitting,
    startEval,
    submitAnswer,
    submitEval,
    clearActiveEval,
  }
})
