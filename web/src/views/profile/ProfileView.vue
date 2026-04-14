<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useProfileStore } from '@/stores/profile'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const profileStore = useProfileStore()
const authStore = useAuthStore()

const profile = computed(() => profileStore.profile)

const form = reactive({
  major: profile.value.major,
  current_level: profile.value.current_level,
  learning_goal: profile.value.learning_goal,
  preferred_style: profile.value.preferred_style,
  cognitive_style: profile.value.cognitive_style,
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

const cognitiveStyleOptions = [
  { value: 'THEORETICAL', label: '理论推导型', desc: '偏好从原理出发理解知识' },
  { value: 'PRACTICAL', label: '实践驱动型', desc: '偏好通过动手练习来学习' },
  { value: 'VISUAL', label: '视觉学习型', desc: '偏好图表和可视化辅助' },
  { value: 'MIXED', label: '混合型', desc: '灵活运用多种学习方式' },
]

const timeOptions = [
  { value: 15, label: '15 分钟' },
  { value: 30, label: '30 分钟' },
  { value: 60, label: '1 小时' },
  { value: 90, label: '1.5 小时' },
  { value: 120, label: '2 小时' },
]

const isDirty = computed(() => {
  const currentForm = {
    major: form.major,
    current_level: form.current_level,
    learning_goal: form.learning_goal,
    preferred_style: form.preferred_style,
    cognitive_style: form.cognitive_style,
    daily_time_minutes: form.daily_time_minutes,
  }
  const profileForm = {
    major: profile.value.major,
    current_level: profile.value.current_level,
    learning_goal: profile.value.learning_goal,
    preferred_style: profile.value.preferred_style,
    cognitive_style: profile.value.cognitive_style,
    daily_time_minutes: profile.value.daily_time_minutes,
  }
  return JSON.stringify(currentForm) !== JSON.stringify(profileForm)
})

function handleSave() {
  profileStore.updateProfile({
    major: form.major,
    current_level: form.current_level,
    learning_goal: form.learning_goal,
    preferred_style: form.preferred_style,
    cognitive_style: form.cognitive_style,
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
  if (percentage < 40) return 'var(--status-error)'
  if (percentage <= 70) return 'var(--accent-secondary)'
  return 'var(--status-success)'
}

function masteryGradient(percentage: number): string {
  if (percentage < 40) return 'linear-gradient(90deg, var(--status-error), var(--status-error))'
  if (percentage <= 70) return 'linear-gradient(90deg, var(--accent-secondary), var(--accent-secondary))'
  return 'linear-gradient(90deg, var(--status-success), var(--status-success))'
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

const root = document.documentElement
const cs = getComputedStyle(root)
const styleBarColors = [
  cs.getPropertyValue('--accent-primary').trim(),
  cs.getPropertyValue('--accent-secondary').trim(),
  cs.getPropertyValue('--accent-secondary-light').trim(),
]

function levelLabel(val: string): string {
  return levelOptions.find(o => o.value === val)?.label ?? val
}

function goalLabel(val: string): string {
  return goalOptions.find(o => o.value === val)?.label ?? val
}
</script>

<template>
  <div class="profile-view">
    <!-- Profile Incomplete Banner -->
    <div v-if="!profile.profile_complete" class="incomplete-banner">
      <div class="incomplete-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div class="incomplete-body">
        <div class="incomplete-title">学习画像尚未完成</div>
        <div class="incomplete-desc">通过与智伴对话，完成学习画像初始化，获得更精准的个性化推荐。</div>
      </div>
      <router-link to="/app/chat" class="incomplete-action">去对话</router-link>
    </div>

    <!-- Greeting Card -->
    <div class="greeting-card">
      <div class="greeting-content">
        <h1 class="greeting-text">你好，{{ authStore.nickname || '同学' }}</h1>
        <div class="greeting-pills">
          <span class="greeting-pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            {{ levelLabel(profile.current_level) }}
          </span>
          <span class="greeting-pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>
            每日 {{ profile.daily_time_minutes }} 分钟
          </span>
          <span class="greeting-pill">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            {{ goalLabel(profile.learning_goal) }}
          </span>
        </div>
      </div>
      <div class="greeting-decoration">
        <svg width="120" height="120" viewBox="0 0 120 120" fill="none" opacity="0.15">
          <circle cx="60" cy="60" r="50" stroke="var(--bg-card)" stroke-width="4"/>
          <circle cx="60" cy="60" r="35" stroke="var(--bg-card)" stroke-width="3"/>
          <circle cx="60" cy="60" r="20" stroke="var(--bg-card)" stroke-width="2"/>
        </svg>
      </div>
    </div>

    <!-- Section 1: 基本信息 -->
    <div class="section-grid">
      <div class="dashboard-card profile-card">
        <div class="card-header-custom">
          <div class="card-icon card-icon-indigo">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <span class="card-title-custom">基本信息</span>
        </div>

        <div class="profile-form">
          <div class="form-field">
            <label class="form-label">昵称</label>
            <div class="form-value-static">{{ authStore.nickname || '--' }}</div>
          </div>

          <div class="form-field">
            <label class="form-label">专业背景</label>
            <el-input
              v-model="form.major"
              placeholder="例如：计算机科学与技术"
              class="form-input"
            />
          </div>

          <div class="form-field">
            <label class="form-label">当前水平</label>
            <el-select v-model="form.current_level" class="form-select">
              <el-option
                v-for="opt in levelOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>

          <div class="form-field">
            <label class="form-label">学习目标</label>
            <el-select v-model="form.learning_goal" class="form-select">
              <el-option
                v-for="opt in goalOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>

          <div class="form-field">
            <label class="form-label">偏好学习方式</label>
            <el-select v-model="form.preferred_style" class="form-select">
              <el-option
                v-for="opt in styleOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>

          <div class="form-field">
            <label class="form-label">每日学习时长</label>
            <el-select v-model="form.daily_time_minutes" class="form-select">
              <el-option
                v-for="opt in timeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </div>

          <!-- Cognitive Style Cards -->
          <div class="form-field">
            <label class="form-label">认知风格</label>
            <div class="cognitive-cards">
              <div
                v-for="opt in cognitiveStyleOptions"
                :key="opt.value"
                class="cognitive-card"
                :class="{ 'cognitive-card--active': form.cognitive_style === opt.value }"
                @click="form.cognitive_style = opt.value as typeof form.cognitive_style"
              >
                <span class="cognitive-card-label">{{ opt.label }}</span>
                <span class="cognitive-card-desc">{{ opt.desc }}</span>
              </div>
            </div>
          </div>

          <div class="form-field">
            <label class="form-label">学习科目</label>
            <div class="subjects-tags">
              <span
                v-for="(subject, i) in profile.subjects"
                :key="subject"
                class="subject-tag"
                :style="{
                  backgroundColor: ['var(--accent-primary-light)', 'var(--accent-primary-light)', 'var(--accent-secondary-light)', 'var(--status-error-light)', 'var(--bg-hover)'][i % 5],
                  color: ['var(--accent-primary)', 'var(--status-success)', 'var(--status-error)', 'var(--status-error)', 'var(--accent-secondary)'][i % 5],
                  borderColor: ['var(--accent-primary-light)', 'var(--accent-primary-light)', 'var(--accent-secondary-light)', 'var(--status-error-light)', 'var(--accent-primary-light)'][i % 5],
                }"
              >
                {{ subject }}
              </span>
              <span v-if="!profile.subjects.length" class="empty-hint">暂无科目</span>
            </div>
          </div>

          <Transition name="fade">
            <button
              v-if="isDirty"
              class="save-btn"
              @click="handleSave"
            >
              保存修改
            </button>
          </Transition>
        </div>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Section 2: 知识掌握度 -->
        <div class="dashboard-card mastery-card">
          <div class="card-header-custom">
            <div class="card-icon card-icon-emerald">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/>
              </svg>
            </div>
            <span class="card-title-custom">知识掌握度</span>
          </div>

          <div v-if="masteryEntries.length" class="mastery-list">
            <div
              v-for="entry in masteryEntries"
              :key="entry.name"
              class="mastery-item"
            >
              <div class="mastery-header">
                <span class="mastery-name">{{ entry.name }}</span>
                <div class="mastery-right">
                  <span
                    v-if="entry.isWeak"
                    class="weak-badge"
                  >
                    &#9888; 薄弱
                  </span>
                  <span
                    class="mastery-percent"
                    :style="{ color: masteryColor(entry.percentage) }"
                  >
                    {{ entry.percentage }}%
                  </span>
                </div>
              </div>
              <div class="mastery-bar-track">
                <div
                  class="mastery-bar-fill"
                  :style="{
                    width: entry.percentage + '%',
                    background: masteryGradient(entry.percentage),
                  }"
                ></div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-icon">&#128202;</span>
            <span class="empty-text">暂无知识掌握数据</span>
          </div>
        </div>

        <!-- Section 3: 学习偏好 -->
        <div class="dashboard-card preference-card">
          <div class="card-header-custom">
            <div class="card-icon card-icon-violet">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
              </svg>
            </div>
            <span class="card-title-custom">学习偏好</span>
          </div>

          <div v-if="styleWeights.length" class="preference-content">
            <div class="stacked-bar-wrapper">
              <div class="stacked-bar">
                <div
                  v-for="(item, index) in styleWeights"
                  :key="item.key"
                  class="stacked-segment"
                  :style="{
                    width: item.percentage + '%',
                    backgroundColor: styleBarColors[index % styleBarColors.length],
                  }"
                >
                  <span v-if="item.percentage > 15" class="segment-label">{{ item.percentage }}%</span>
                </div>
              </div>
            </div>
            <div class="preference-legend">
              <div
                v-for="(item, index) in styleWeights"
                :key="item.key"
                class="legend-item"
              >
                <span
                  class="legend-dot"
                  :style="{ backgroundColor: styleBarColors[index % styleBarColors.length] }"
                ></span>
                <span class="legend-label">{{ item.label }}</span>
                <span class="legend-value">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-text">暂无风格数据</span>
          </div>
        </div>

        <!-- Section 4: 易错点分析 -->
        <div class="dashboard-card error-card">
          <div class="card-header-custom">
            <div class="card-icon card-icon-amber">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <span class="card-title-custom">易错点分析</span>
          </div>

          <div v-if="profile.error_patterns.length" class="error-list">
            <div
              v-for="(pattern, i) in profile.error_patterns"
              :key="i"
              class="error-tag"
            >
              <span class="error-tag-dot"></span>
              {{ pattern }}
            </div>
          </div>
          <div v-else class="empty-state">
            <span class="empty-text">暂无易错点数据</span>
          </div>
          <div class="error-note">系统通过评估自动识别</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Incomplete Banner */
.incomplete-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  margin-bottom: 20px;
  background: var(--accent-secondary-light);
  border: 1px solid var(--accent-secondary);
  border-radius: 12px;
}

.incomplete-icon {
  flex-shrink: 0;
  color: var(--accent-secondary);
}

.incomplete-body {
  flex: 1;
}

.incomplete-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.incomplete-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.incomplete-action {
  flex-shrink: 0;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--bg-card);
  background: var(--accent-secondary);
  border-radius: 8px;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.incomplete-action:hover {
  opacity: 0.85;
}

/* Greeting Card */
.greeting-card {
  position: relative;
  overflow: hidden;
  background: var(--accent-primary);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 28px;
  color: var(--bg-card);
}

.greeting-content {
  position: relative;
  z-index: 1;
}

.greeting-text {
  margin: 0 0 16px;
  font-size: 28px;
  font-weight: 800;
  color: var(--bg-card);
  line-height: 1.3;
}

.greeting-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.greeting-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: color-mix(in srgb, var(--bg-card) 20%, transparent);
  backdrop-filter: blur(8px);
  color: var(--bg-card);
  border: 1px solid color-mix(in srgb, var(--bg-card) 15%, transparent);
}

.greeting-decoration {
  position: absolute;
  top: -10px;
  right: -10px;
  pointer-events: none;
}

/* Section Grid (replaces dashboard-grid) */
.section-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-card {
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
  padding: 24px;
}

.card-header-custom {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-indigo {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.card-icon-emerald {
  background: var(--accent-primary-light);
  color: var(--status-success);
}

.card-icon-violet {
  background: var(--bg-hover);
  color: var(--accent-secondary);
}

.card-icon-amber {
  background: var(--accent-secondary-light);
  color: var(--accent-secondary);
}

.card-title-custom {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

/* Profile Form */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.form-value-static {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  border: 1px solid var(--bg-hover);
}

.form-select {
  width: 100%;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px var(--border);
  padding: 4px 12px;
  transition: all 0.15s ease;
}

.form-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary-light);
}

.form-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--accent-primary);
}

.form-select :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px var(--border);
  padding: 4px 12px;
  transition: all 0.15s ease;
}

.form-select :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--accent-primary-light);
}

.form-select :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--accent-primary);
}

/* Cognitive Style Cards */
.cognitive-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.cognitive-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1.5px solid var(--border);
  background: var(--bg-primary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.cognitive-card:hover {
  border-color: var(--accent-primary-light);
  background: var(--bg-hover);
}

.cognitive-card--active {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.cognitive-card-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.cognitive-card-desc {
  font-size: 11px;
  color: var(--text-tertiary);
  line-height: 1.4;
}

.cognitive-card--active .cognitive-card-label {
  color: var(--accent-primary);
}

.subjects-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-tag {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid;
}

.empty-hint {
  font-size: 13px;
  color: var(--text-secondary);
}

.save-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-card);
  background: var(--accent-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 4px;
}

.save-btn:hover {
  box-shadow: 0 4px 16px color-mix(in srgb, var(--accent-primary) 40%, transparent);
  transform: translateY(-1px);
}

.save-btn:active {
  transform: translateY(0);
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* Mastery Card */
.mastery-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mastery-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mastery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mastery-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.mastery-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weak-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-secondary);
  background: var(--accent-secondary-light);
  border: 1px solid var(--accent-secondary);
  padding: 1px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.mastery-percent {
  font-size: 14px;
  font-weight: 700;
  min-width: 38px;
  text-align: right;
}

.mastery-bar-track {
  width: 100%;
  height: 8px;
  background: var(--bg-hover);
  border-radius: 20px;
  overflow: hidden;
}

.mastery-bar-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 0;
}

.empty-icon {
  font-size: 28px;
}

.empty-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Preference Card */
.preference-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stacked-bar-wrapper {
  width: 100%;
}

.stacked-bar {
  display: flex;
  height: 28px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-hover);
}

.stacked-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.4s ease;
  min-width: 2px;
}

.segment-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--bg-card);
}

.preference-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.legend-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Error Patterns Card */
.error-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.error-tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-secondary);
  flex-shrink: 0;
}

.error-note {
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-tertiary);
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .profile-view {
    padding: 20px 16px;
  }
  .section-grid {
    grid-template-columns: 1fr;
  }
  .greeting-text {
    font-size: 22px;
  }
  .greeting-card {
    padding: 24px 20px;
  }
  .cognitive-cards {
    grid-template-columns: 1fr;
  }
}
</style>
