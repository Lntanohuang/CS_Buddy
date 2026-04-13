import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { UserProfile } from '@/types'
import { mockProfile } from '@/mock/data'

export const useProfileStore = defineStore('profile', () => {
  const profile = ref<UserProfile>({ ...mockProfile })

  function updateProfile(updates: Partial<UserProfile>) {
    Object.assign(profile.value, updates)
    profile.value.updated_at = new Date().toISOString()
  }

  function updateMastery(kp: string, value: number) {
    profile.value.knowledge_mastery[kp] = value
    profile.value.weak_points = Object.entries(profile.value.knowledge_mastery)
      .filter(([, v]) => v < 0.4)
      .map(([k]) => k)
    profile.value.updated_at = new Date().toISOString()
  }

  return { profile, updateProfile, updateMastery }
})
