<script setup lang="ts">
import { computed } from 'vue'

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
  <el-card shadow="hover" class="resource-card">
    <div class="resource-card__header">
      <span class="resource-card__title">{{ title }}</span>
      <el-tag :type="difficultyColor" size="small">{{ difficultyLabel }}</el-tag>
    </div>
    <div class="resource-card__meta">
      <span class="resource-card__time">⏱ 预计 {{ estMinutes }} 分钟</span>
      <span class="resource-card__point">📖 {{ knowledgePoint }}</span>
    </div>
  </el-card>
</template>

<style scoped>
.resource-card {
  margin-top: 8px;
  max-width: 360px;
}

.resource-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.resource-card__title {
  font-weight: 600;
  font-size: 14px;
}

.resource-card__meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
