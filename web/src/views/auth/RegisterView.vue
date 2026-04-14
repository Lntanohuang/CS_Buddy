<script setup lang="ts">
import { reactive, shallowRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { SurveyData } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const activeStep = shallowRef(0)
const loading = shallowRef(false)

const basicForm = reactive({ nickname: '', email: '', password: '' })

const surveyForm: SurveyData = reactive({
  learning_goal: 'INTEREST',
  current_level: 'BEGINNER',
  daily_time_minutes: 30,
  preferred_style: 'MIXED',
  subjects: [],
})

const goalOptions = [
  { value: 'EXAM_PREP', label: '备考', icon: '📝' },
  { value: 'INTEREST', label: '兴趣学习', icon: '💡' },
  { value: 'SKILL_UP', label: '技能提升', icon: '🚀' },
]

const levelOptions = [
  { value: 'BEGINNER', label: '入门', icon: '🌱' },
  { value: 'ELEMENTARY', label: '初级', icon: '🌿' },
  { value: 'INTERMEDIATE', label: '中级', icon: '🌳' },
  { value: 'ADVANCED', label: '高级', icon: '🏔' },
]

const styleOptions = [
  { value: 'VIDEO', label: '视频', icon: '🎬' },
  { value: 'TEXT', label: '文字', icon: '📖' },
  { value: 'PRACTICE', label: '实践', icon: '🔧' },
  { value: 'MIXED', label: '混合', icon: '🎯' },
]

const subjectOptions = [
  { value: '数据结构', icon: '🧩' },
  { value: '算法', icon: '⚙️' },
  { value: 'Python', icon: '🐍' },
  { value: '英语', icon: '🌍' },
]

function goToStep2() {
  if (!basicForm.nickname || !basicForm.email || !basicForm.password) {
    ElMessage.warning('请填写所有必填项')
    return
  }
  activeStep.value = 1
}

function toggleSubject(subject: string) {
  const idx = surveyForm.subjects.indexOf(subject)
  if (idx >= 0) surveyForm.subjects.splice(idx, 1)
  else surveyForm.subjects.push(subject)
}

function completeWithSurvey() { activeStep.value = 2 }
function skipSurvey() { activeStep.value = 2 }

async function handleFinish() {
  loading.value = true
  try {
    authStore.register({
      nickname: basicForm.nickname,
      email: basicForm.email,
      password: basicForm.password,
      survey: surveyForm.subjects.length > 0 ? { ...surveyForm } : null,
    })
    ElMessage.success('注册成功，欢迎使用智伴！')
    router.push('/app/chat')
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

      <!-- Step indicator -->
      <div class="steps">
        <div v-for="(s, i) in ['基础信息', '学习偏好', '完成']" :key="i" class="step" :class="{ active: activeStep === i, done: activeStep > i }">
          <div class="step-dot">{{ activeStep > i ? '✓' : i + 1 }}</div>
          <span class="step-label">{{ s }}</span>
        </div>
      </div>

      <!-- Step 1: Basic info -->
      <div v-if="activeStep === 0" class="step-content">
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input v-model="basicForm.nickname" class="form-input" placeholder="你的名字" />
        </div>
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input v-model="basicForm.email" type="email" class="form-input" placeholder="name@example.com" />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input v-model="basicForm.password" type="password" class="form-input" placeholder="至少 6 位" />
        </div>
        <button class="submit-btn" @click="goToStep2">下一步</button>
      </div>

      <!-- Step 2: Survey -->
      <div v-if="activeStep === 1" class="step-content">
        <div class="survey-section">
          <p class="survey-label">学习目标</p>
          <div class="option-grid cols-3">
            <button v-for="opt in goalOptions" :key="opt.value" class="option-card" :class="{ selected: surveyForm.learning_goal === opt.value }" @click="surveyForm.learning_goal = opt.value as SurveyData['learning_goal']">
              <span class="option-icon">{{ opt.icon }}</span>
              <span class="option-text">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <div class="survey-section">
          <p class="survey-label">当前水平</p>
          <div class="option-grid cols-4">
            <button v-for="opt in levelOptions" :key="opt.value" class="option-card" :class="{ selected: surveyForm.current_level === opt.value }" @click="surveyForm.current_level = opt.value as SurveyData['current_level']">
              <span class="option-icon">{{ opt.icon }}</span>
              <span class="option-text">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <div class="survey-section">
          <p class="survey-label">偏好方式</p>
          <div class="option-grid cols-4">
            <button v-for="opt in styleOptions" :key="opt.value" class="option-card" :class="{ selected: surveyForm.preferred_style === opt.value }" @click="surveyForm.preferred_style = opt.value as SurveyData['preferred_style']">
              <span class="option-icon">{{ opt.icon }}</span>
              <span class="option-text">{{ opt.label }}</span>
            </button>
          </div>
        </div>

        <div class="survey-section">
          <p class="survey-label">感兴趣的科目</p>
          <div class="option-grid cols-4">
            <button v-for="opt in subjectOptions" :key="opt.value" class="option-card" :class="{ selected: surveyForm.subjects.includes(opt.value) }" @click="toggleSubject(opt.value)">
              <span class="option-icon">{{ opt.icon }}</span>
              <span class="option-text">{{ opt.value }}</span>
            </button>
          </div>
        </div>

        <div class="step-actions">
          <button class="submit-btn" @click="completeWithSurvey">完成注册</button>
          <button class="text-btn" @click="skipSurvey">跳过，稍后设置</button>
        </div>
      </div>

      <!-- Step 3: Done -->
      <div v-if="activeStep === 2" class="step-content done-content">
        <div class="done-icon">🎉</div>
        <h2 class="done-title">注册成功！</h2>
        <p class="done-desc">一切就绪，开始你的学习之旅吧</p>
        <button class="submit-btn" :disabled="loading" @click="handleFinish">
          <span v-if="loading" class="spinner"></span>
          <span v-else>进入智伴</span>
        </button>
      </div>

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
  max-width: 480px;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-leaf { font-size: 28px; display: block; margin-bottom: 10px; }
.logo-name { font-size: 24px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; }
.tagline { color: var(--text-secondary); font-size: 14px; }

/* Steps */
.steps {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 32px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.step.active .step-dot {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: var(--bg-card);
}

.step.done .step-dot {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.step-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.step.active .step-label { color: var(--text-primary); font-weight: 500; }

/* Form */
.step-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 500; color: var(--text-primary); }

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
  transition: border-color 0.15s, box-shadow 0.15s;
}

.form-input::placeholder { color: var(--border-strong); }
.form-input:focus { border-color: var(--accent-primary); box-shadow: 0 0 0 3px rgba(74,124,111,0.1); }

/* Survey */
.survey-section { display: flex; flex-direction: column; gap: 8px; }
.survey-label { font-size: 13px; font-weight: 500; color: var(--text-primary); }

.option-grid {
  display: grid;
  gap: 8px;
}

.option-grid.cols-3 { grid-template-columns: repeat(3, 1fr); }
.option-grid.cols-4 { grid-template-columns: repeat(4, 1fr); }

.option-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.option-card:hover { border-color: var(--border-strong); background: var(--bg-hover); }

.option-card.selected {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.option-icon { font-size: 20px; }
.option-text { font-size: 12px; color: var(--text-primary); font-weight: 450; }

/* Buttons */
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
}

.submit-btn:hover:not(:disabled) { background: var(--accent-primary-hover); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.text-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  font-family: inherit;
  padding: 8px;
}

.text-btn:hover { color: var(--text-primary); }

.step-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

/* Done */
.done-content { align-items: center; padding: 24px 0; }
.done-icon { font-size: 48px; margin-bottom: 8px; }
.done-title { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.done-desc { color: var(--text-secondary); font-size: 14px; margin-bottom: 16px; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: var(--bg-card);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.register-footer {
  text-align: center;
  margin-top: 28px;
  font-size: 14px;
  color: var(--text-secondary);
}

.link { color: var(--accent-primary); font-weight: 500; margin-left: 2px; }
.link:hover { text-decoration: underline; }

@media (max-width: 480px) {
  .option-grid.cols-4 { grid-template-columns: repeat(2, 1fr); }
}
</style>
