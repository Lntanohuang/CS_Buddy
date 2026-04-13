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

const basicForm = reactive({
  nickname: '',
  email: '',
  password: '',
})

const surveyForm: SurveyData = reactive({
  learning_goal: 'INTEREST',
  current_level: 'BEGINNER',
  daily_time_minutes: 30,
  preferred_style: 'MIXED',
  subjects: [],
})

function goToStep2() {
  if (!basicForm.nickname || !basicForm.email || !basicForm.password) {
    ElMessage.warning('请填写所有必填项')
    return
  }
  activeStep.value = 1
}

function completeWithSurvey() {
  activeStep.value = 2
}

function skipSurvey() {
  activeStep.value = 2
}

async function handleFinish() {
  loading.value = true
  try {
    const hasSurvey = surveyForm.subjects.length > 0 || activeStep.value === 2
    authStore.register({
      nickname: basicForm.nickname,
      email: basicForm.email,
      password: basicForm.password,
      survey: hasSurvey ? { ...surveyForm } : null,
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
    <el-card class="register-card" shadow="hover">
      <div class="register-header">
        <h1>智伴</h1>
        <p class="subtitle">创建你的学习账号</p>
      </div>

      <el-steps :active="activeStep" align-center class="register-steps">
        <el-step title="基础信息" />
        <el-step title="学习偏好" />
        <el-step title="完成" />
      </el-steps>

      <!-- Step 1: Basic Info -->
      <div v-if="activeStep === 0" class="step-content">
        <el-form :model="basicForm" label-position="top">
          <el-form-item label="昵称">
            <el-input v-model="basicForm.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="basicForm.email" type="email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="basicForm.password"
              type="password"
              placeholder="请输入密码"
              show-password
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="full-btn" @click="goToStep2">
              下一步
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: Survey -->
      <div v-else-if="activeStep === 1" class="step-content">
        <el-form :model="surveyForm" label-position="top">
          <el-form-item label="学习目标">
            <el-radio-group v-model="surveyForm.learning_goal">
              <el-radio value="EXAM_PREP">备考</el-radio>
              <el-radio value="INTEREST">兴趣</el-radio>
              <el-radio value="SKILL_UP">技能提升</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="当前水平">
            <el-radio-group v-model="surveyForm.current_level">
              <el-radio value="BEGINNER">入门</el-radio>
              <el-radio value="ELEMENTARY">初级</el-radio>
              <el-radio value="INTERMEDIATE">中级</el-radio>
              <el-radio value="ADVANCED">高级</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="每日学习时间">
            <el-select v-model="surveyForm.daily_time_minutes" style="width: 100%">
              <el-option :value="15" label="15 分钟" />
              <el-option :value="30" label="30 分钟" />
              <el-option :value="60" label="60 分钟" />
              <el-option :value="120" label="120 分钟" />
            </el-select>
          </el-form-item>

          <el-form-item label="偏好学习方式">
            <el-radio-group v-model="surveyForm.preferred_style">
              <el-radio value="VIDEO">视频</el-radio>
              <el-radio value="TEXT">文字</el-radio>
              <el-radio value="PRACTICE">实践</el-radio>
              <el-radio value="MIXED">混合</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="感兴趣的学科">
            <el-checkbox-group v-model="surveyForm.subjects">
              <el-checkbox value="数据结构" label="数据结构" />
              <el-checkbox value="算法" label="算法" />
              <el-checkbox value="Python" label="Python" />
              <el-checkbox value="英语" label="英语" />
            </el-checkbox-group>
          </el-form-item>

          <el-form-item>
            <div class="step2-actions">
              <el-button @click="activeStep = 0">上一步</el-button>
              <el-button text @click="skipSurvey">跳过问卷</el-button>
              <el-button type="primary" @click="completeWithSurvey">下一步</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 3: Complete -->
      <div v-else class="step-content step-complete">
        <el-icon :size="64" color="#67c23a" class="success-icon">
          <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
            <path
              fill="currentColor"
              d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm-55.808 536.384-99.52-99.584a38.4 38.4 0 1 0-54.336 54.336l126.72 126.72a38.272 38.272 0 0 0 54.336 0l262.4-262.464a38.4 38.4 0 1 0-54.336-54.272L456.192 600.384z"
            />
          </svg>
        </el-icon>
        <h2>注册成功！</h2>
        <p class="complete-desc">一切准备就绪，开始你的智能学习之旅吧</p>
        <el-button type="primary" size="large" :loading="loading" @click="handleFinish">
          开始学习
        </el-button>
      </div>

      <div class="register-footer">
        <span>已有账号？</span>
        <router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e0ecff 0%, #f5f7fa 100%);
  padding: 40px 0;
}

.register-card {
  width: 520px;
}

.register-header {
  text-align: center;
  margin-bottom: 16px;
}

.register-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 8px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.register-steps {
  margin-bottom: 24px;
}

.step-content {
  min-height: 200px;
}

.step2-actions {
  display: flex;
  width: 100%;
  gap: 8px;
  justify-content: space-between;
}

.step-complete {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px 0;
}

.step-complete h2 {
  font-size: 20px;
  color: #303133;
}

.complete-desc {
  color: #909399;
  font-size: 14px;
}

.success-icon {
  margin-bottom: 8px;
}

.full-btn {
  width: 100%;
}

.register-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #909399;
}

.register-footer a {
  color: #409eff;
  text-decoration: none;
  margin-left: 4px;
}
</style>
