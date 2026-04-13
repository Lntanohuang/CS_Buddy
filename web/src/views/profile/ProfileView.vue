<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const profileStore = useProfileStore()
const authStore = useAuthStore()

const profile = computed(() => profileStore.profile)

const form = reactive({
  current_level: profile.value.current_level,
  learning_goal: profile.value.learning_goal,
  preferred_style: profile.value.preferred_style,
  daily_time_minutes: profile.value.daily_time_minutes,
})

const levelOptions = [
  { value: 'BEGINNER', label: '入门' },
  { value: 'ELEMENTARY', label: '初级' },
  { value: 'INTERMEDIATE', label: '中级' },
  { value: 'ADVANCED', label: '高级' },
]

const goalOptions = [
  { value: 'EXAM_PREP', label: '备考提分' },
  { value: 'INTEREST', label: '兴趣学习' },
  { value: 'SKILL_UP', label: '技能提升' },
]

const styleOptions = [
  { value: 'VIDEO', label: '视频讲解' },
  { value: 'TEXT', label: '文字阅读' },
  { value: 'PRACTICE', label: '练习为主' },
  { value: 'MIXED', label: '混合模式' },
]

const timeOptions = [
  { value: 15, label: '15 分钟' },
  { value: 30, label: '30 分钟' },
  { value: 60, label: '1 小时' },
  { value: 90, label: '1.5 小时' },
  { value: 120, label: '2 小时' },
]

function handleSave() {
  profileStore.updateProfile({
    current_level: form.current_level,
    learning_goal: form.learning_goal,
    preferred_style: form.preferred_style,
    daily_time_minutes: form.daily_time_minutes,
  })
  ElMessage.success('保存成功')
}

const masteryEntries = computed(() =>
  Object.entries(profile.value.knowledge_mastery).map(([name, value]) => ({
    name,
    value,
    percentage: Math.round(value * 100),
    isWeak: profile.value.weak_points.includes(name),
  }))
)

function masteryColor(percentage: number): string {
  if (percentage < 40) return '#f56c6c'
  if (percentage <= 70) return '#e6a23c'
  return '#67c23a'
}

const styleWeights = computed(() => {
  const weights = profile.value.style_weights
  const total = Object.values(weights).reduce((s, v) => s + v, 0) || 1
  return Object.entries(weights).map(([key, value]) => ({
    key,
    label: styleWeightLabel(key),
    value,
    percentage: Math.round((value / total) * 100),
  }))
})

function styleWeightLabel(key: string): string {
  const map: Record<string, string> = {
    code_example: '代码示例',
    analogy: '类比举例',
    text: '文字说明',
  }
  return map[key] ?? key
}
</script>

<template>
  <div class="profile-view">
    <el-row :gutter="24">
      <!-- Left Column: User Info -->
      <el-col :xs="24" :md="10">
        <el-card shadow="never" class="info-card">
          <template #header>
            <div class="card-title">
              <el-icon :size="20"><User /></el-icon>
              <span>个人信息</span>
            </div>
          </template>

          <el-form label-position="top" class="profile-form">
            <el-form-item label="昵称">
              <el-input :model-value="authStore.nickname" disabled />
            </el-form-item>

            <el-form-item label="当前水平">
              <el-select v-model="form.current_level" style="width: 100%">
                <el-option
                  v-for="opt in levelOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="学习目标">
              <el-select v-model="form.learning_goal" style="width: 100%">
                <el-option
                  v-for="opt in goalOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="偏好学习方式">
              <el-select v-model="form.preferred_style" style="width: 100%">
                <el-option
                  v-for="opt in styleOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="每日学习时长">
              <el-select v-model="form.daily_time_minutes" style="width: 100%">
                <el-option
                  v-for="opt in timeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="学习科目">
              <div class="subjects-tags">
                <el-tag
                  v-for="subject in profile.subjects"
                  :key="subject"
                  type="primary"
                  effect="light"
                >
                  {{ subject }}
                </el-tag>
                <span v-if="!profile.subjects.length" class="empty-hint">暂无科目</span>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleSave" style="width: 100%">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right Column: Knowledge Mastery -->
      <el-col :xs="24" :md="14">
        <el-card shadow="never" class="mastery-card">
          <template #header>
            <div class="card-title">
              <el-icon :size="20"><DataAnalysis /></el-icon>
              <span>知识掌握度</span>
            </div>
          </template>

          <div v-if="masteryEntries.length" class="mastery-list">
            <div
              v-for="entry in masteryEntries"
              :key="entry.name"
              class="mastery-item"
            >
              <div class="mastery-label">
                <span class="mastery-name">{{ entry.name }}</span>
                <el-icon
                  v-if="entry.isWeak"
                  color="#e6a23c"
                  :size="16"
                  class="weak-icon"
                >
                  <WarningFilled />
                </el-icon>
              </div>
              <el-progress
                :percentage="entry.percentage"
                :color="masteryColor(entry.percentage)"
                :stroke-width="14"
                :text-inside="true"
              />
            </div>
          </div>
          <el-empty v-else description="暂无知识掌握数据" />
        </el-card>

        <el-card shadow="never" class="style-card">
          <template #header>
            <div class="card-title">
              <el-icon :size="20"><PieChart /></el-icon>
              <span>风格偏好权重</span>
            </div>
          </template>

          <div v-if="styleWeights.length" class="style-chart">
            <div
              v-for="item in styleWeights"
              :key="item.key"
              class="style-row"
            >
              <span class="style-label">{{ item.label }}</span>
              <div class="style-bar-wrapper">
                <div
                  class="style-bar"
                  :style="{ width: item.percentage + '%' }"
                ></div>
              </div>
              <span class="style-percentage">{{ item.percentage }}%</span>
            </div>
          </div>
          <el-empty v-else description="暂无风格数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.profile-view {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.info-card {
  margin-bottom: 24px;
}

.profile-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.subjects-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-hint {
  font-size: 13px;
  color: var(--el-text-color-placeholder);
}

/* Mastery */
.mastery-card {
  margin-bottom: 24px;
}

.mastery-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mastery-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mastery-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mastery-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.weak-icon {
  flex-shrink: 0;
}

/* Style weights chart */
.style-card {
  margin-bottom: 24px;
}

.style-chart {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.style-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.style-label {
  width: 80px;
  flex-shrink: 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
  text-align: right;
}

.style-bar-wrapper {
  flex: 1;
  height: 20px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  overflow: hidden;
}

.style-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--el-color-primary-light-3), var(--el-color-primary));
  border-radius: 4px;
  transition: width 0.4s ease;
  min-width: 2px;
}

.style-percentage {
  width: 40px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  text-align: right;
}
</style>
