<script setup lang="ts">
import { computed } from 'vue'
import { Timer, Reading } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  difficulty: string
  estMinutes: number
  knowledgePoint: string
}>()

const difficultyColor = computed(() => {
  const map: Record<string, string> = {
    BEGINNER: 'success',
    INTERMEDIATE: '',
    ADVANCED: 'warning',
  }
  return map[props.difficulty] ?? 'info'
})

const difficultyLabel = computed(() => {
  const map: Record<string, string> = {
    BEGINNER: '入门',
    INTERMEDIATE: '中级',
    ADVANCED: '高级',
  }
  return map[props.difficulty] ?? props.difficulty
})
</script>

<template>
  <div class="resource-card">
    <div class="resource-card__accent" />
    <div class="resource-card__body">
      <div class="resource-card__header">
        <span class="resource-card__title">{{ title }}</span>
        <span class="resource-card__difficulty" :class="`resource-card__difficulty--${difficultyColor}`">
          {{ difficultyLabel }}
        </span>
      </div>
      <div class="resource-card__meta">
        <span class="resource-card__meta-item">
          <el-icon :size="13"><Timer /></el-icon>
          <span>预计 {{ estMinutes }} 分钟</span>
        </span>
        <span class="resource-card__meta-item">
          <el-icon :size="13"><Reading /></el-icon>
          <span>{{ knowledgePoint }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.resource-card {
  display: flex;
  margin-top: 12px;
  max-width: 380px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
  cursor: pointer;
}

.resource-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--accent-primary-light);
  transform: translateY(-1px);
}

.resource-card__accent {
  width: 4px;
  flex-shrink: 0;
  background: linear-gradient(to bottom, #4A7C6F, #E8C07A);
}

.resource-card__body {
  flex: 1;
  padding: 12px 16px;
  min-width: 0;
}

.resource-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.resource-card__title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resource-card__difficulty {
  flex-shrink: 0;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.6;
}

.resource-card__difficulty--success {
  background: var(--accent-primary-light);
  color: var(--accent-primary-hover);
}

.resource-card__difficulty-- {
  background: var(--accent-primary-light);
  color: var(--accent-primary);
}

.resource-card__difficulty--warning {
  background: var(--accent-secondary-light);
  color: var(--accent-secondary);
}

.resource-card__difficulty--info {
  background: var(--bg-hover);
  color: var(--text-tertiary);
}

.resource-card__meta {
  display: flex;
  gap: 18px;
  margin-top: 10px;
}

.resource-card__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.resource-card__meta-item .el-icon {
  color: var(--text-secondary);
}
</style>
