<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePathStore } from '@/stores/path'
import { useEvalStore } from '@/stores/eval'
import PathTimeline from '@/components/path/PathTimeline.vue'

const router = useRouter()
const pathStore = usePathStore()
const evalStore = useEvalStore()

const path = computed(() => pathStore.path)
const nodes = computed(() => path.value.nodes)
const progressPercent = computed(() => pathStore.progressPercent)

const completedCount = computed(() => path.value.completed_nodes)
const totalCount = computed(() => path.value.total_nodes)

const remainingHours = computed(() => {
  const remainingMinutes = path.value.nodes
    .filter((n) => n.status === 'PENDING' || n.status === 'IN_PROGRESS')
    .reduce((sum, n) => sum + n.est_minutes, 0)
  return (remainingMinutes / 60).toFixed(1)
})

function handleSkip(nodeId: string) {
  pathStore.skipNode(nodeId)
}

function handleStartEval(knowledgePoint: string) {
  evalStore.startEval(knowledgePoint)
  router.push('/app/evaluate')
}

function handleSelect(_nodeId: string) {
  // Could navigate to node detail in the future
}
</script>

<template>
  <div class="path-view">
    <!-- Header Section -->
    <div class="path-header">
      <div class="header-title-row">
        <h1 class="path-title">{{ path.subject }}学习路径</h1>
        <span class="subject-pill">{{ path.subject }}</span>
      </div>
      <p class="path-goal">{{ path.goal }}</p>
    </div>

    <!-- Stats Row -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon stat-icon-total">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ totalCount }}</span>
          <span class="stat-label">总节点</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-completed">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value stat-value-success">{{ completedCount }}</span>
          <span class="stat-label">已完成</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-remaining">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value stat-value-warning">{{ remainingHours }}h</span>
          <span class="stat-label">预计剩余</span>
        </div>
      </div>
    </div>

    <!-- Timeline -->
    <div class="timeline-wrapper">
      <PathTimeline
        :nodes="nodes"
        :progress-percent="progressPercent"
        @select="handleSelect"
        @skip="handleSkip"
        @start-eval="handleStartEval"
      />
    </div>
  </div>
</template>

<style scoped>
.path-view {
  max-width: 720px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* Header */
.path-header {
  margin-bottom: 28px;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.path-title {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  background: var(--accent-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.3;
}

.subject-pill {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary-light);
  white-space: nowrap;
}

.path-goal {
  margin: 0;
  font-size: 15px;
  color: var(--text-tertiary);
  line-height: 1.6;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-total {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.stat-icon-completed {
  background: var(--accent-primary-light);
  color: var(--status-success);
}

.stat-icon-remaining {
  background: var(--accent-secondary-light);
  color: var(--accent-secondary);
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-value-success {
  color: var(--status-success);
}

.stat-value-warning {
  color: var(--accent-secondary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Timeline wrapper */
.timeline-wrapper {
  /* No extra styling needed, just a container */
}

/* Responsive */
@media (max-width: 540px) {
  .path-view {
    padding: 20px 16px;
  }
  .stats-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  .path-title {
    font-size: 22px;
  }
}
</style>
