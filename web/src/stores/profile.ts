import { computed } from 'vue'
import { defineStore } from 'pinia'
import type { UserProfile } from '@/types'
import { useUserStore } from './user'

export const useProfileStore = defineStore('profile', () => {
  const userStore = useUserStore()
  userStore.fetchMockUserData()

  const profile = computed<UserProfile>(() => ({
    user_id: userStore.userInfo.id,
    major: userStore.major,
    knowledge_mastery: { ...userStore.knowledgeMastery },
    cognitive_style: userStore.cognitiveStyle,
    error_patterns: [...userStore.errorPatterns],
    preferred_style: userStore.preferredStyle,
    daily_time_minutes: userStore.dailyTimeMinutes,
    learning_goal: userStore.learningGoal,
    current_level: userStore.currentLevel,
    weak_points: [...userStore.weakPoints],
    style_weights: { ...userStore.styleWeights },
    subjects: [...userStore.subjects],
    profile_complete: userStore.profileComplete,
    updated_at: userStore.updatedAt,
  }))

  function updateProfile(updates: Partial<UserProfile>) {
    userStore.updateProfile(updates)
  }

  function updateMastery(kp: string, value: number) {
    userStore.updateMastery(kp, value)
  }

  function initFromDialogue(data: {
    major: string
    learning_goal: string
    current_level: string
    preferred_style: string
    cognitive_style: UserProfile['cognitive_style']
    daily_time_minutes: number
    subjects: string[]
  }) {
    userStore.initFromDialogue(data)
  }

  return { profile, updateProfile, updateMastery, initFromDialogue }
})
