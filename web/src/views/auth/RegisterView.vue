<script setup lang="ts">
import { reactive, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = shallowRef(false)

const form = reactive({
  nickname: '',
  email: '',
  password: '',
})

async function handleRegister() {
  if (!form.nickname || !form.email || !form.password) {
    ElMessage.warning('请填写昵称、邮箱和密码')
    return
  }
  loading.value = true
  try {
    await authStore.register(form.nickname, form.email, form.password)
    await router.push('/welcome')
    ElMessage.success('注册成功')
  } catch (error) {
    console.error('Register or navigation failed:', error)
    ElMessage.error('注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <div class="register-header">
        <span class="logo-leaf">🌿</span>
        <h1 class="logo-name">创建账号</h1>
        <p class="tagline">开始你的个性化学习之旅</p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input
            v-model="form.nickname"
            class="form-input"
            placeholder="你的名字"
          />
        </div>
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
            placeholder="至少 6 位"
          />
        </div>
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>注册</span>
        </button>
      </form>

      <p class="register-footer">
        已有账号？<router-link to="/login" class="link">返回登录</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 24px;
}

.register-card {
  width: 100%;
  max-width: 380px;
}

.register-header {
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

.register-form {
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

.register-footer {
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
