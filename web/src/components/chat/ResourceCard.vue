<script setup lang="ts">
import { computed } from 'vue'
import { Timer, Reading } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  difficulty: string
  estMinutes: number
  knowledgePoint: string
  resourceType?: 'doc' | 'mindmap' | 'quiz' | 'video' | 'code'
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

const typeConfig = computed(() => {
  const map: Record<string, { icon: string; label: string }> = {
    doc: { icon: '\uD83D\uDCC4', label: '文档' },
    mindmap: { icon: '\uD83E\uDDE0', label: '思维导图' },
    quiz: { icon: '\u270F\uFE0F', label: '练习题' },
    video: { icon: '\uD83C\uDFAC', label: '教学视频' },
    code: { icon: '\uD83D\uDCBB', label: '代码案例' },
  }
  return map[props.resourceType ?? 'doc'] ?? map.doc
})
</script>

<template>
  <div class="resource-card">
    <div class="resource-card__accent" />
    <div class="resource-card__body">
      <div class="resource-card__header">
        <span class="resource-card__type">
          <span class="resource-card__type-icon">{{ typeConfig.icon }}</span>
          <span class="resource-card__type-label">{{ typeConfig.label }}</span>
        </span>
        <span class="resource-card__difficulty" :class="`resource-card__difficulty--${difficultyColor}`">
          {{ difficultyLabel }}
        </span>
      </div>
      <div class="resource-card__title">{{ title }}</div>
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
  box-shadow: var(--shadow-md);
  border-color: var(--accent-primary-light);
  transform: translateY(-1px);
}

.resource-card__accent {
  width: 4px;
  flex-shrink: 0;
  background: var(--accent-primary);
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

.resource-card__type {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.resource-card__type-icon {
  font-size: 14px;
}

.resource-card__type-label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-tertiary);
}

.resource-card__title {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-top: 6px;
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
