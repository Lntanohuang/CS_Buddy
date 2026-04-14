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
    COMPLETED: 'var(--status-success)',
    IN_PROGRESS: 'var(--accent-primary)',
    PENDING: 'var(--border-strong)',
    SKIPPED: 'var(--text-secondary)',
  }
  return map[status]
}

const timelineIcon = (status: PathNode['status']) => {
  if (status === 'COMPLETED') return 'CircleCheckFilled'
  return ''
}

const dotColor = (status: PathNode['status']) => {
  const map: Record<PathNode['status'], string> = {
    COMPLETED: 'var(--status-success)',
    IN_PROGRESS: 'var(--accent-primary)',
    PENDING: 'var(--border-strong)',
    SKIPPED: 'var(--text-secondary)',
  }
  return map[status]
}

const segmentColor = (status: PathNode['status']) => {
  const map: Record<PathNode['status'], string> = {
    COMPLETED: 'var(--status-success)',
    IN_PROGRESS: 'var(--accent-primary)',
    PENDING: 'var(--border)',
    SKIPPED: 'var(--border-strong)',
  }
  return map[status]
}
</script>

<template>
  <div class="path-timeline">
    <!-- Progress Section -->
    <div class="progress-section">
      <div class="progress-header">
        <div class="progress-text-block">
          <span class="progress-label">学习进度</span>
          <span class="progress-sublabel">继续保持，你做得很好！</span>
        </div>
        <div class="progress-ring-wrapper">
          <svg class="progress-ring" viewBox="0 0 100 100">
            <circle
              class="progress-ring-bg"
              cx="50" cy="50" r="42"
              fill="none"
              stroke="var(--border)"
              stroke-width="8"
            />
            <circle
              class="progress-ring-fill"
              cx="50" cy="50" r="42"
              fill="none"
              stroke="url(#progressGradient)"
              stroke-width="8"
              stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 42"
              :stroke-dashoffset="2 * Math.PI * 42 * (1 - progressPercent / 100)"
              transform="rotate(-90 50 50)"
            />
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="var(--accent-primary)" />
                <stop offset="100%" stop-color="var(--status-success)" />
              </linearGradient>
            </defs>
          </svg>
          <span class="progress-ring-text">{{ progressPercent }}%</span>
        </div>
      </div>
      <div class="progress-stats">
        <div class="progress-stat">
          <span class="stat-number">{{ nodes.filter(n => n.status === 'COMPLETED').length }}</span>
          <span class="stat-desc">已完成</span>
        </div>
        <div class="progress-stat-divider"></div>
        <div class="progress-stat">
          <span class="stat-number">{{ nodes.filter(n => n.status === 'IN_PROGRESS').length }}</span>
          <span class="stat-desc">进行中</span>
        </div>
        <div class="progress-stat-divider"></div>
        <div class="progress-stat">
          <span class="stat-number">{{ nodes.filter(n => n.status === 'PENDING').length }}</span>
          <span class="stat-desc">待完成</span>
        </div>
        <div class="progress-stat-divider"></div>
        <div class="progress-stat">
          <span class="stat-number">{{ nodes.filter(n => n.status === 'SKIPPED').length }}</span>
          <span class="stat-desc">已跳过</span>
        </div>
      </div>
    </div>

    <!-- Custom Timeline -->
    <div class="timeline">
      <div
        v-for="(node, index) in nodes"
        :key="node.node_id"
        class="timeline-item"
      >
        <!-- Timeline line + dot -->
        <div class="timeline-track">
          <div
            v-if="index > 0"
            class="timeline-segment timeline-segment-top"
            :style="{ backgroundColor: segmentColor(nodes[index - 1].status) }"
          ></div>
          <div
            class="timeline-dot"
            :class="{ 'is-active': node.status === 'IN_PROGRESS' }"
            :style="{ backgroundColor: dotColor(node.status) }"
          >
            <svg
              v-if="node.status === 'COMPLETED'"
              width="10" height="10" viewBox="0 0 12 12" fill="none"
            >
              <path d="M2.5 6L5 8.5L9.5 4" stroke="var(--bg-card)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div
            v-if="index < nodes.length - 1"
            class="timeline-segment timeline-segment-bottom"
            :style="{ backgroundColor: segmentColor(node.status) }"
          ></div>
        </div>

        <!-- Node card -->
        <div class="timeline-card-wrapper">
          <PathNodeCard
            :node="node"
            @select="emit('select', $event)"
            @skip="emit('skip', $event)"
            @start-eval="emit('start-eval', $event)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.path-timeline {
  padding: 0;
}

/* Progress Section */
.progress-section {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.progress-text-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-label {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.progress-sublabel {
  font-size: 14px;
  color: var(--text-tertiary);
}

.progress-ring-wrapper {
  position: relative;
  width: 88px;
  height: 88px;
  flex-shrink: 0;
}

.progress-ring {
  width: 100%;
  height: 100%;
}

.progress-ring-bg {
  opacity: 1;
}

.progress-ring-fill {
  transition: stroke-dashoffset 0.6s ease;
}

.progress-ring-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.progress-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 16px 0 0;
  border-top: 1px solid var(--bg-hover);
}

.progress-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.progress-stat-divider {
  width: 1px;
  height: 28px;
  background: var(--border);
}

.stat-number {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-desc {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* Custom Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.timeline-item {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.timeline-track {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
  position: relative;
}

.timeline-segment {
  width: 2px;
  flex: 1;
  min-height: 8px;
}

.timeline-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.timeline-dot.is-active {
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-primary) 20%, transparent);
}

.timeline-card-wrapper {
  flex: 1;
  min-width: 0;
  padding: 8px 0;
}
</style>
