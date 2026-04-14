import { shallowRef, computed } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser } from '@/types'
import { mockUser } from '@/mock/data'

const STORAGE_KEY = 'user'

function getLocalStorage(): Storage | null {
  if (typeof window === 'undefined') return null

  try {
    return window.localStorage
  } catch {
    return null
  }
}

function isAuthUser(value: unknown): value is AuthUser {
  if (!value || typeof value !== 'object') return false

  const candidate = value as Partial<AuthUser>
  return (
    typeof candidate.user_id === 'string' &&
    typeof candidate.nickname === 'string' &&
    (candidate.role === 'STUDENT' || candidate.role === 'TEACHER') &&
    typeof candidate.access_token === 'string' &&
    typeof candidate.refresh_token === 'string' &&
    typeof candidate.expires_in === 'number' &&
    typeof candidate.has_profile === 'boolean'
  )
}

function readStoredUser(): AuthUser | null {
  const storage = getLocalStorage()
  if (!storage) return null

  try {
    const raw = storage.getItem(STORAGE_KEY)
    if (!raw) return null

    const parsed = JSON.parse(raw)
    if (!isAuthUser(parsed)) {
      storage.removeItem(STORAGE_KEY)
      return null
    }

    return parsed
  } catch {
    try {
      storage.removeItem(STORAGE_KEY)
    } catch {
      // Ignore storage failures to avoid crashing app startup/navigation.
    }
    return null
  }
}

function persistUser(user: AuthUser | null) {
  const storage = getLocalStorage()
  if (!storage) return

  try {
    if (user) {
      storage.setItem(STORAGE_KEY, JSON.stringify(user))
    } else {
      storage.removeItem(STORAGE_KEY)
    }
  } catch {
    // Ignore storage failures to avoid crashing app startup/navigation.
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = shallowRef<AuthUser | null>(readStoredUser())

  const isLoggedIn = computed(() => !!user.value)
  const nickname = computed(() => user.value?.nickname ?? '')
  const hasProfile = computed(() => user.value?.has_profile ?? false)

  async function login(_email: string, _password: string) {
    user.value = { ...mockUser, has_profile: true }
    persistUser(user.value)
  }

  async function register(nickname: string, _email: string, _password: string) {
    user.value = { ...mockUser, nickname, has_profile: false }
    persistUser(user.value)
  }

  function completeProfile() {
    if (user.value) {
      user.value = { ...user.value, has_profile: true }
      persistUser(user.value)
    }
  }

  function logout() {
    user.value = null
    persistUser(null)
  }

  return { user, isLoggedIn, nickname, hasProfile, login, register, completeProfile, logout }
})
