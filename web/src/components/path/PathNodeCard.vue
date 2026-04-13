<script setup lang="ts">
import type { PathNode } from '@/types'

const props = defineProps<{
  node: PathNode
}>()

const emit = defineEmits<{
  select: [nodeId: string]
  skip: [nodeId: string]
  'start-eval': [knowledgePoint: string]
}>()

const difficultyColor = (difficulty: string) => {
  const map: Record<string, string> = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger',
  }
  return map[difficulty.toLowerCase()] ?? 'info'
}

const difficultyLabel = (difficulty: string) => {
  const map: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难',
  }
  return map[difficulty.toLowerCase()] ?? difficulty
}

const statusConfig = {
  COMPLETED: { color: 'var(--el-color-success)', icon: 'CircleCheckFilled', label: '已完成' },
  IN_PROGRESS: { color: 'var(--el-color-primary)', icon: '', label: '学习中' },
  PENDING: { color: 'var(--el-color-info-light-5)', icon: '', label: '待学习' },
  SKIPPED: { color: 'var(--el-color-info)', icon: '', label: '已跳过' },
} as const
</script>

<template>
  <div
    class="path-node-card"
    :class="[`status-${node.status.toLowerCase()}`]"
    @click="emit('select', node.node_id)"
  >
    <div class="card-header">
      <div class="title-row">
        <span
          class="title"
          :class="{ 'is-skipped': node.status === 'SKIPPED' }"
        >
          {{ node.title }}
        </span>
        <el-tag
          v-if="node.is_supplement"
          size="small"
          type="warning"
          effect="light"
          class="supplement-tag"
        >
          补强
        </el-tag>
      </div>
      <div class="status-badge">
        <template v-if="node.status === 'COMPLETED'">
          <el-icon color="var(--el-color-success)" :size="16">
            <CircleCheckFilled />
          </el-icon>
        </template>
        <template v-else-if="node.status === 'IN_PROGRESS'">
          <span class="pulse-dot"></span>
        </template>
        <template v-else>
          <span
            class="status-dot"
            :style="{ backgroundColor: statusConfig[node.status].color }"
          ></span>
        </template>
        <span class="status-label">{{ statusConfig[node.status].label }}</span>
      </div>
    </div>

    <div class="card-meta">
      <el-tag :type="difficultyColor(node.difficulty)" size="small" effect="plain">
        {{ difficultyLabel(node.difficulty) }}
      </el-tag>
      <span class="est-time">
        <el-icon :size="14"><Timer /></el-icon>
        {{ node.est_minutes }} 分钟
      </span>
    </div>

    <div class="card-actions" v-if="node.status === 'IN_PROGRESS'">
      <el-button
        type="primary"
        size="small"
        @click.stop="emit('start-eval', node.knowledge_point)"
      >
        开始评估
      </el-button>
      <el-link
        type="info"
        :underline="false"
        @click.stop="emit('skip', node.node_id)"
      >
        跳过
      </el-link>
    </div>
    <div class="card-actions" v-else-if="node.status === 'COMPLETED'">
      <el-button type="success" size="small" disabled plain>
        已完成
      </el-button>
    </div>
    <div class="card-actions" v-else-if="node.status === 'PENDING'">
      <el-button size="small" disabled>
        待解锁
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.path-node-card {
  padding: 16px;
  border-radius: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.path-node-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.path-node-card.status-in_progress {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.path-node-card.status-completed {
  border-color: var(--el-color-success-light-5);
}

.path-node-card.status-skipped {
  opacity: 0.6;
}

.path-node-card.status-pending {
  opacity: 0.7;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.title {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.title.is-skipped {
  text-decoration: line-through;
  color: var(--el-text-color-secondary);
}

.supplement-tag {
  flex-shrink: 0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 12px;
}

.status-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.3); }
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.est-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
