import { shallowRef, computed } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser, RegisterRequest } from '@/types'
import { mockUser } from '@/mock/data'

export const useAuthStore = defineStore('auth', () => {
  const user = shallowRef<AuthUser | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )

  const isLoggedIn = computed(() => !!user.value)
  const nickname = computed(() => user.value?.nickname ?? '')

  function login(_email: string, _password: string) {
    user.value = { ...mockUser }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function register(_req: RegisterRequest) {
    user.value = { ...mockUser, nickname: _req.nickname }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function logout() {
    user.value = null
    localStorage.removeItem('user')
  }

  return { user, isLoggedIn, nickname, login, register, logout }
})
