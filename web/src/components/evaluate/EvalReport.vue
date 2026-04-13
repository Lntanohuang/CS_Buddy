<script setup lang="ts">
import { computed } from 'vue'
import type { Evaluation } from '@/types'

const props = defineProps<{
  evaluation: Evaluation
}>()

const emit = defineEmits<{
  close: []
}>()

const scoreColor = computed(() => {
  const s = props.evaluation.score ?? 0
  if (s >= 70) return '#67c23a'
  if (s >= 40) return '#e6a23c'
  return '#f56c6c'
})

const masteryPercent = computed(() => Math.round((props.evaluation.mastery_level ?? 0) * 100))

const masteryBarColor = computed(() => {
  if (masteryPercent.value >= 70) return '#67c23a'
  if (masteryPercent.value >= 40) return '#e6a23c'
  return '#f56c6c'
})

const timeDisplay = computed(() => {
  const sec = props.evaluation.time_spent_seconds ?? 0
  if (sec < 60) return `${sec} 秒`
  const min = Math.floor(sec / 60)
  const rem = sec % 60
  return rem > 0 ? `${min} 分 ${rem} 秒` : `${min} 分钟`
})

const recommendationType = computed(() => {
  const action = props.evaluation.recommendation?.action
  if (action === 'ADVANCE') return 'success'
  if (action === 'SUPPLEMENT') return 'warning'
  return 'error'
})

const recommendationTitle = computed(() => {
  const action = props.evaluation.recommendation?.action
  if (action === 'ADVANCE') return '继续前进'
  if (action === 'SUPPLEMENT') return '补充练习'
  return '回顾基础'
})
</script>

<template>
  <div class="eval-report">
    <h2 class="report-title">评估报告</h2>

    <!-- Score -->
    <div class="score-section">
      <div class="score-display" :style="{ color: scoreColor }">
        {{ evaluation.score ?? 0 }}
      </div>
      <span class="score-label">分</span>
    </div>

    <!-- Stats -->
    <div class="stats-section">
      <div class="stat-item">
        <span class="stat-label">正确率</span>
        <span class="stat-value">
          {{ evaluation.correct_count ?? 0 }} / {{ evaluation.question_count }}
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">用时</span>
        <span class="stat-value">{{ timeDisplay }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">掌握度</span>
        <div class="mastery-bar-wrapper">
          <el-progress
            :percentage="masteryPercent"
            :color="masteryBarColor"
            :stroke-width="18"
            :text-inside="true"
          />
        </div>
      </div>
    </div>

    <!-- Recommendation -->
    <div v-if="evaluation.recommendation" class="recommendation-section">
      <el-alert
        :title="recommendationTitle"
        :type="recommendationType"
        :description="evaluation.recommendation.message"
        show-icon
        :closable="false"
      />
    </div>

    <!-- Action -->
    <div class="report-footer">
      <el-button type="primary" size="large" @click="emit('close')">
        返回评估中心
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.eval-report {
  max-width: 600px;
  margin: 0 auto;
  padding: 32px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.report-title {
  text-align: center;
  margin: 0 0 28px;
  font-size: 22px;
}

.score-section {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 32px;
}

.score-display {
  font-size: 72px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 20px;
  color: var(--el-text-color-secondary);
  margin-left: 4px;
}

.stats-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 28px;
  padding: 20px;
  background: var(--el-fill-color-lighter, #f5f7fa);
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 15px;
  font-weight: 600;
}

.mastery-bar-wrapper {
  width: 200px;
}

.recommendation-section {
  margin-bottom: 28px;
}

.report-footer {
  display: flex;
  justify-content: center;
}
</style>
