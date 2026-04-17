<script setup lang="ts">
import { computed } from 'vue'
import type { Evaluation } from '@/types'

const props = defineProps<{
  evaluation: Evaluation
}>()

const emit = defineEmits<{
  close: []
}>()

const score = computed(() => props.evaluation.score ?? 0)

const scoreColor = computed(() => {
  const s = props.evaluation.score ?? 0
  if (s >= 70) return 'var(--status-success)'
  if (s >= 40) return 'var(--accent-secondary)'
  return 'var(--status-error)'
})

const masteryPercent = computed(() => Math.round((props.evaluation.mastery_level ?? 0) * 100))

const masteryBarColor = computed(() => {
  if (masteryPercent.value >= 70) return 'var(--status-success)'
  if (masteryPercent.value >= 40) return 'var(--accent-secondary)'
  return 'var(--status-error)'
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

/* Progress ring math - 96px diameter, 6px stroke */
const ringRadius = 42
const ringCircumference = 2 * Math.PI * ringRadius
const ringOffset = computed(() => ringCircumference - (masteryPercent.value / 100) * ringCircumference)

const isHighScore = computed(() => score.value >= 80)

/* Enhanced evaluation dimensions */
const efficiencyPercent = computed(() => {
  const eff = props.evaluation.learning_efficiency
  if (eff == null) return null
  return Math.round(eff * 100)
})

const trendInfo = computed(() => {
  const trend = props.evaluation.progress_trend
  if (!trend) return null
  const map: Record<string, { arrow: string; label: string; color: string }> = {
    UP: { arrow: '\u2191', label: '进步中', color: 'var(--status-success)' },
    STABLE: { arrow: '\u2192', label: '保持稳定', color: 'var(--text-tertiary)' },
    DOWN: { arrow: '\u2193', label: '需要加强', color: 'var(--status-error)' },
  }
  return map[trend] ?? null
})

const weakPoints = computed(() => props.evaluation.weak_point_analysis ?? [])
</script>

<template>
  <div class="eval-report">
    <!-- Confetti (CSS-only, high scores) -->
    <div v-if="isHighScore" class="confetti-container" aria-hidden="true">
      <span v-for="i in 20" :key="i" class="confetti-piece" :style="{ '--i': i }" />
    </div>

    <h2 class="report-title">评估报告</h2>

    <!-- Score -->
    <div class="score-section">
      <div class="score-number" :style="{ color: scoreColor }">
        {{ score }}
      </div>
      <span class="score-unit">分</span>
    </div>

    <!-- Mastery ring -->
    <div class="mastery-ring-wrapper">
      <svg class="mastery-ring" width="108" height="108" viewBox="0 0 108 108">
        <circle
          cx="54" cy="54" :r="ringRadius"
          fill="none" stroke="var(--border)" stroke-width="6"
        />
        <circle
          cx="54" cy="54" :r="ringRadius"
          fill="none"
          :stroke="masteryBarColor"
          stroke-width="6"
          stroke-linecap="round"
          :stroke-dasharray="ringCircumference"
          :stroke-dashoffset="ringOffset"
          class="mastery-ring-fill"
        />
      </svg>
      <div class="mastery-ring-label">
        <span class="mastery-ring-value" :style="{ color: masteryBarColor }">{{ masteryPercent }}%</span>
        <span class="mastery-ring-text">掌握度</span>
      </div>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon stat-icon--correct">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div class="stat-number">{{ evaluation.correct_count ?? 0 }}/{{ evaluation.question_count }}</div>
        <div class="stat-label">正确数</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--time">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="stat-number">{{ timeDisplay }}</div>
        <div class="stat-label">用时</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon--mastery">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <div class="stat-number">{{ masteryPercent }}%</div>
        <div class="stat-label">掌握度</div>
      </div>
    </div>

    <!-- Multi-dimension evaluation -->
    <div
      v-if="efficiencyPercent != null || trendInfo || weakPoints.length"
      class="multi-dim-section"
    >
      <div class="multi-dim-title">多维评估</div>

      <!-- Learning Efficiency -->
      <div v-if="efficiencyPercent != null" class="dim-item">
        <div class="dim-header">
          <span class="dim-label">学习效率</span>
          <span class="dim-value">{{ efficiencyPercent }}%</span>
        </div>
        <div class="dim-bar-track">
          <div
            class="dim-bar-fill"
            :style="{
              width: efficiencyPercent + '%',
              background: efficiencyPercent >= 70 ? 'var(--status-success)' : efficiencyPercent >= 40 ? 'var(--accent-secondary)' : 'var(--status-error)',
            }"
          ></div>
        </div>
      </div>

      <!-- Progress Trend -->
      <div v-if="trendInfo" class="dim-item">
        <div class="dim-header">
          <span class="dim-label">进步趋势</span>
          <span class="trend-badge" :style="{ color: trendInfo.color, borderColor: trendInfo.color }">
            <span class="trend-arrow">{{ trendInfo.arrow }}</span>
            {{ trendInfo.label }}
          </span>
        </div>
      </div>

      <!-- Weak Point Analysis -->
      <div v-if="weakPoints.length" class="dim-item">
        <div class="dim-header">
          <span class="dim-label">薄弱点分析</span>
        </div>
        <ul class="weak-list">
          <li v-for="(point, i) in weakPoints" :key="i" class="weak-list-item">
            {{ point }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Recommendation -->
    <div
      v-if="evaluation.recommendation"
      class="recommendation-card"
      :class="`recommendation-card--${recommendationType}`"
    >
      <div class="recommendation-icon">
        <!-- Success: rocket -->
        <svg v-if="recommendationType === 'success'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/></svg>
        <!-- Warning: refresh -->
        <svg v-else-if="recommendationType === 'warning'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
        <!-- Error: arrow-left -->
        <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      </div>
      <div class="recommendation-body">
        <div class="recommendation-title">{{ recommendationTitle }}</div>
        <div class="recommendation-message">{{ evaluation.recommendation.message }}</div>
      </div>
    </div>

    <!-- Feedback hints -->
    <div class="feedback-hints">
      <div class="feedback-hint feedback-hint--profile">
        <span class="feedback-hint__icon">✅</span>
        <span>已根据本次测评更新你的学习画像</span>
      </div>
      <div class="feedback-hint feedback-hint--path">
        <span class="feedback-hint__icon">🔄</span>
        <span>已根据测评结果调整学习路径</span>
      </div>
    </div>

    <!-- Action -->
    <div class="report-footer">
      <button class="back-btn" @click="emit('close')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
        返回评估中心
      </button>
    </div>
  </div>
</template>

<style scoped>
.eval-report {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
  padding: 40px 32px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  overflow: hidden;
}

.report-title {
  text-align: center;
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Score */
.score-section {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 8px;
}

.score-number {
  font-size: 96px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -2px;
}

.score-unit {
  font-size: 22px;
  color: var(--text-secondary);
  margin-left: 4px;
  font-weight: 500;
}

/* Mastery ring */
.mastery-ring-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  margin-bottom: 32px;
}

.mastery-ring {
  transform: rotate(-90deg);
}

.mastery-ring-fill {
  transition: stroke-dashoffset 1s ease;
}

.mastery-ring-label {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mastery-ring-value {
  font-size: 20px;
  font-weight: 700;
}

.mastery-ring-text {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 1px;
}

/* Stats row */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 12px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
}

.stat-icon--correct {
  background: var(--accent-primary-light);
  color: var(--status-success);
}

.stat-icon--time {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.stat-icon--mastery {
  background: var(--accent-secondary-light);
  color: var(--accent-secondary);
}

.stat-number {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Multi-dimension evaluation */
.multi-dim-section {
  margin-bottom: 28px;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.multi-dim-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.dim-item {
  margin-bottom: 14px;
}

.dim-item:last-child {
  margin-bottom: 0;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.dim-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-tertiary);
}

.dim-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.dim-bar-track {
  width: 100%;
  height: 6px;
  background: var(--bg-hover);
  border-radius: 20px;
  overflow: hidden;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 20px;
  transition: width 0.5s ease;
  min-width: 2px;
}

.trend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  border: 1.5px solid;
  background: var(--bg-card);
}

.trend-arrow {
  font-size: 15px;
  font-weight: 700;
}

.weak-list {
  margin: 0;
  padding: 0 0 0 18px;
  list-style: disc;
}

.weak-list-item {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.7;
}

/* Recommendation */
.recommendation-card {
  display: flex;
  gap: 14px;
  padding: 16px 18px;
  border-radius: 12px;
  margin-bottom: 28px;
  border-left: 4px solid transparent;
}

.recommendation-card--success {
  background: var(--accent-primary-light);
  border-left-color: var(--status-success);
}

.recommendation-card--warning {
  background: var(--accent-secondary-light);
  border-left-color: var(--accent-secondary);
}

.recommendation-card--error {
  background: var(--status-error-light);
  border-left-color: var(--status-error);
}

.recommendation-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.recommendation-card--success .recommendation-icon {
  color: var(--status-success);
}

.recommendation-card--warning .recommendation-icon {
  color: var(--accent-secondary);
}

.recommendation-card--error .recommendation-icon {
  color: var(--status-error);
}

.recommendation-body {
  flex: 1;
}

.recommendation-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.recommendation-message {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-tertiary);
}

/* Feedback hints */
.feedback-hints {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

.feedback-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.feedback-hint--profile {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.feedback-hint--path {
  background: var(--accent-secondary-light);
  color: var(--accent-secondary);
}

.feedback-hint__icon {
  font-size: 15px;
  flex-shrink: 0;
}

/* Footer */
.report-footer {
  display: flex;
  justify-content: center;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 28px;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-primary);
  background: transparent;
  border: 1.5px solid var(--accent-primary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--accent-primary-light);
}

/* Confetti (CSS only) */
.confetti-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  opacity: 0;
  animation: confetti-fall 3s ease-in forwards;
  animation-delay: calc(var(--i) * 0.1s);
}

.confetti-piece:nth-child(5n+1) { background: var(--accent-primary); left: 10%; }
.confetti-piece:nth-child(5n+2) { background: var(--accent-secondary); left: 30%; }
.confetti-piece:nth-child(5n+3) { background: var(--status-success); left: 50%; }
.confetti-piece:nth-child(5n+4) { background: var(--accent-secondary); left: 70%; }
.confetti-piece:nth-child(5n+5) { background: var(--status-error); left: 90%; }

.confetti-piece:nth-child(odd) {
  width: 6px;
  height: 10px;
  border-radius: 50%;
}

@keyframes confetti-fall {
  0% {
    opacity: 1;
    transform: translateY(0) rotate(0deg) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(500px) rotate(720deg) scale(0.5);
  }
}

/* Vary horizontal movement for each piece */
.confetti-piece:nth-child(1) { left: 5%; animation-duration: 2.5s; }
.confetti-piece:nth-child(2) { left: 15%; animation-duration: 3.2s; }
.confetti-piece:nth-child(3) { left: 22%; animation-duration: 2.8s; }
.confetti-piece:nth-child(4) { left: 32%; animation-duration: 3.5s; }
.confetti-piece:nth-child(5) { left: 40%; animation-duration: 2.6s; }
.confetti-piece:nth-child(6) { left: 48%; animation-duration: 3.1s; }
.confetti-piece:nth-child(7) { left: 55%; animation-duration: 2.9s; }
.confetti-piece:nth-child(8) { left: 62%; animation-duration: 3.3s; }
.confetti-piece:nth-child(9) { left: 68%; animation-duration: 2.7s; }
.confetti-piece:nth-child(10) { left: 75%; animation-duration: 3.0s; }
.confetti-piece:nth-child(11) { left: 8%; animation-duration: 3.4s; }
.confetti-piece:nth-child(12) { left: 18%; animation-duration: 2.6s; }
.confetti-piece:nth-child(13) { left: 28%; animation-duration: 3.1s; }
.confetti-piece:nth-child(14) { left: 38%; animation-duration: 2.9s; }
.confetti-piece:nth-child(15) { left: 45%; animation-duration: 3.3s; }
.confetti-piece:nth-child(16) { left: 52%; animation-duration: 2.5s; }
.confetti-piece:nth-child(17) { left: 60%; animation-duration: 3.2s; }
.confetti-piece:nth-child(18) { left: 72%; animation-duration: 2.8s; }
.confetti-piece:nth-child(19) { left: 82%; animation-duration: 3.0s; }
.confetti-piece:nth-child(20) { left: 92%; animation-duration: 2.7s; }
</style>
