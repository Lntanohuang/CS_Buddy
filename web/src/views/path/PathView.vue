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
    <div class="path-header">
      <div class="header-top">
        <h2 class="path-title">{{ path.subject }}</h2>
        <el-tag effect="dark" size="large">{{ path.subject }}</el-tag>
      </div>
      <p class="path-goal">{{ path.goal }}</p>
    </div>

    <div class="stats-row">
      <el-card shadow="never" class="stat-card">
        <div class="stat-value">{{ totalCount }}</div>
        <div class="stat-label">总节点</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value completed">{{ completedCount }}</div>
        <div class="stat-label">已完成</div>
      </el-card>
      <el-card shadow="never" class="stat-card">
        <div class="stat-value hours">{{ remainingHours }}</div>
        <div class="stat-label">预计剩余 (小时)</div>
      </el-card>
    </div>

    <PathTimeline
      :nodes="nodes"
      :progress-percent="progressPercent"
      @select="handleSelect"
      @skip="handleSkip"
      @start-eval="handleStartEval"
    />
  </div>
</template>

<style scoped>
.path-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.path-header {
  margin-bottom: 24px;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.path-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.path-goal {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}

.stat-value.completed {
  color: var(--el-color-success);
}

.stat-value.hours {
  color: var(--el-color-warning);
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style>
