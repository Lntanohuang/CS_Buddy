<script setup lang="ts">
import { reactive, shallowRef, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = shallowRef(false)

const form = reactive({
  email: '',
  password: '',
})

async function handleLogin() {
  if (!form.email || !form.password) {
    ElMessage.warning('请填写邮箱和密码')
    return
  }
  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    await nextTick()
    // Let router guard decide: /welcome (new user) or /app/chat (returning user)
    await router.push(authStore.hasProfile ? '/app/chat' : '/welcome')
    ElMessage.success('登录成功')
  } catch (error) {
    console.error('Login or navigation failed:', error)
    ElMessage.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="logo-leaf">🌿</span>
        <h1 class="logo-name">CS Buddy</h1>
        <p class="tagline">你的 AI 学习搭档，懂你的学习节奏</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="name@example.com"
          />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="输入密码"
          />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>登录</span>
        </button>
      </form>

      <p class="login-footer">
        还没有账号？<router-link to="/register" class="link">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 380px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-leaf {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
}

.logo-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.tagline {
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  height: 42px;
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  color: var(--text-primary);
  background: var(--bg-card);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.form-input::placeholder {
  color: var(--border-strong);
}

.form-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(74, 124, 111, 0.1);
}

.submit-btn {
  width: 100%;
  height: 42px;
  border: none;
  border-radius: 8px;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 15px;
  font-weight: 550;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
}

.submit-btn:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--bg-card);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  margin-top: 28px;
  font-size: 14px;
  color: var(--text-secondary);
}

.link {
  color: var(--accent-primary);
  font-weight: 500;
  margin-left: 2px;
}

.link:hover {
  text-decoration: underline;
}
</style>
