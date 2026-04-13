<script setup lang="ts">
import type { PathNode } from '@/types'
import PathNodeCard from './PathNodeCard.vue'

defineProps<{
  nodes: PathNode[]
  progressPercent: number
}>()

const emit = defineEmits<{
  select: [nodeId: string]
  skip: [nodeId: string]
  'start-eval': [knowledgePoint: string]
}>()

const timelineColor = (status: PathNode['status']) => {
  const map: Record<PathNode['status'], string> = {
    COMPLETED: '#67c23a',
    IN_PROGRESS: '#409eff',
    PENDING: '#c0c4cc',
    SKIPPED: '#909399',
  }
  return map[status]
}

const timelineIcon = (status: PathNode['status']) => {
  if (status === 'COMPLETED') return 'CircleCheckFilled'
  return ''
}
</script>

<template>
  <div class="path-timeline">
    <div class="progress-section">
      <div class="progress-label">
        <span>学习进度</span>
        <span class="progress-value">{{ progressPercent }}%</span>
      </div>
      <el-progress
        :percentage="progressPercent"
        :stroke-width="10"
        :color="[
          { color: '#f56c6c', percentage: 20 },
          { color: '#e6a23c', percentage: 40 },
          { color: '#409eff', percentage: 70 },
          { color: '#67c23a', percentage: 100 },
        ]"
      />
    </div>

    <el-timeline class="timeline">
      <el-timeline-item
        v-for="node in nodes"
        :key="node.node_id"
        :color="timelineColor(node.status)"
        :hollow="node.status === 'PENDING'"
        size="large"
      >
        <PathNodeCard
          :node="node"
          @select="emit('select', $event)"
          @skip="emit('skip', $event)"
          @start-eval="emit('start-eval', $event)"
        />
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<style scoped>
.path-timeline {
  padding: 0;
}

.progress-section {
  margin-bottom: 24px;
  padding: 16px 20px;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.progress-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.progress-value {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.timeline {
  padding-left: 4px;
}

.timeline :deep(.el-timeline-item__wrapper) {
  padding-left: 20px;
}

.timeline :deep(.el-timeline-item__tail) {
  border-left-width: 2px;
}
</style>
