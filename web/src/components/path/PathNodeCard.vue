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

const difficultyPillColor = (difficulty: string) => {
  const map: Record<string, { bg: string; text: string }> = {
    easy: { bg: 'var(--accent-primary-light)', text: 'var(--accent-primary-hover)' },
    medium: { bg: 'var(--accent-secondary-light)', text: 'var(--accent-secondary)' },
    hard: { bg: 'var(--status-error-light)', text: 'var(--status-error)' },
  }
  return map[difficulty.toLowerCase()] ?? { bg: 'var(--bg-hover)', text: 'var(--text-tertiary)' }
}
</script>

<template>
  <div
    class="path-node-card"
    :class="[
      `status-${node.status.toLowerCase()}`,
      { 'is-supplement': node.is_supplement }
    ]"
    @click="emit('select', node.node_id)"
  >
    <!-- Left: Status Indicator -->
    <div class="card-status-indicator">
      <template v-if="node.status === 'COMPLETED'">
        <span class="status-circle status-completed">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2.5 6L5 8.5L9.5 4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
      </template>
      <template v-else-if="node.status === 'IN_PROGRESS'">
        <span class="status-circle status-in-progress">
          <span class="pulse-ring"></span>
        </span>
      </template>
      <template v-else-if="node.status === 'SKIPPED'">
        <span class="status-circle status-skipped">
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 5H8" stroke="var(--text-secondary)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
      </template>
      <template v-else>
        <span class="status-circle status-pending"></span>
      </template>
    </div>

    <!-- Center: Content -->
    <div class="card-content">
      <div class="card-title-row">
        <span
          class="card-title"
          :class="{ 'is-skipped': node.status === 'SKIPPED' }"
        >
          {{ node.title }}
        </span>
        <span v-if="node.is_supplement" class="supplement-badge">补强</span>
      </div>
      <div class="card-subtitle-row">
        <span
          class="difficulty-pill"
          :style="{
            backgroundColor: difficultyPillColor(node.difficulty).bg,
            color: difficultyPillColor(node.difficulty).text,
          }"
        >
          {{ difficultyLabel(node.difficulty) }}
        </span>
        <span class="time-estimate">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/>
          </svg>
          {{ node.est_minutes }} 分钟
        </span>
        <span class="status-text">{{ statusConfig[node.status].label }}</span>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="card-actions">
      <template v-if="node.status === 'IN_PROGRESS'">
        <button
          class="btn btn-primary"
          @click.stop="emit('start-eval', node.knowledge_point)"
        >
          开始评估
        </button>
        <button
          class="btn btn-ghost"
          @click.stop="emit('skip', node.node_id)"
        >
          跳过
        </button>
      </template>
      <template v-else-if="node.status === 'COMPLETED'">
        <span class="completed-label">
          <svg width="14" height="14" viewBox="0 0 12 12" fill="none">
            <path d="M2.5 6L5 8.5L9.5 4" stroke="var(--status-success)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          已完成
        </span>
      </template>
      <template v-else-if="node.status === 'PENDING'">
        <span class="pending-label">待解锁</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.path-node-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.path-node-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--border-strong);
  transform: translateY(-1px);
}

/* Status backgrounds */
.path-node-card.status-completed {
  background: var(--accent-primary-light);
  border-color: var(--accent-primary-light);
}

.path-node-card.status-in_progress {
  background: var(--accent-primary-light);
  border-color: var(--accent-primary-light);
  border-left: 3px solid #4A7C6F;
  animation: border-pulse 2s ease-in-out infinite;
}

@keyframes border-pulse {
  0%, 100% { border-left-color: var(--accent-primary); }
  50% { border-left-color: var(--accent-primary); }
}

.path-node-card.status-pending {
  background: var(--bg-card);
}

.path-node-card.status-pending .card-title,
.path-node-card.status-pending .card-subtitle-row {
  opacity: 0.6;
}

.path-node-card.status-skipped {
  background: var(--bg-primary);
  border-color: var(--border);
}

/* Supplement node */
.path-node-card.is-supplement {
  border-style: dashed;
  border-color: var(--accent-secondary-light);
}

.path-node-card.is-supplement:hover {
  border-color: var(--accent-secondary);
}

/* Status Indicator */
.card-status-indicator {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.status-circle.status-completed {
  background: var(--status-success);
}

.status-circle.status-in-progress {
  background: var(--accent-primary);
}

.status-circle.status-in-progress .pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #4A7C6F;
  animation: pulse-ring 2s ease-out infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.8); opacity: 0; }
}

.status-circle.status-skipped {
  background: var(--bg-hover);
  border: 2px solid var(--border-strong);
}

.status-circle.status-pending {
  background: var(--bg-hover);
  border: 2px solid var(--border);
  width: 28px;
  height: 28px;
}

/* Content */
.card-content {
  flex: 1;
  min-width: 0;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.card-title.is-skipped {
  text-decoration: line-through;
  color: var(--text-secondary);
}

.supplement-badge {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  background: var(--accent-secondary-light);
  color: var(--status-error);
  border: 1px solid var(--accent-secondary-light);
}

.card-subtitle-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.difficulty-pill {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.6;
}

.time-estimate {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-tertiary);
}

.status-text {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Actions */
.card-actions {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn {
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 8px 16px;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-primary {
  background: var(--accent-primary);
  color: var(--bg-card)fff;
}

.btn-primary:hover {
  background: var(--accent-primary-hover);
  box-shadow: 0 2px 8px rgba(74, 124, 111, 0.4);
}

.btn-ghost {
  background: transparent;
  color: var(--text-tertiary);
  padding: 8px 12px;
}

.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-tertiary);
}

.completed-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--status-success);
  font-weight: 500;
}

.pending-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Responsive: stack on small screens */
@media (max-width: 540px) {
  .path-node-card {
    flex-wrap: wrap;
  }
  .card-actions {
    width: 100%;
    padding-top: 8px;
    padding-left: 44px;
  }
}
</style>
