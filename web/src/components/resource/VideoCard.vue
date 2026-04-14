<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title: string
  duration?: number
  status?: 'generating' | 'ready' | 'error'
}>()

const formattedDuration = computed(() => {
  if (!props.duration) return ''
  const m = Math.floor(props.duration / 60)
  const s = props.duration % 60
  return `${m}:${s.toString().padStart(2, '0')}`
})

const currentStatus = computed(() => props.status ?? 'ready')
</script>

<template>
  <div class="video-card">
    <div class="video-card__thumbnail">
      <!-- Generating state -->
      <template v-if="currentStatus === 'generating'">
        <div class="video-card__spinner" />
        <span class="video-card__status-text">视频生成中...</span>
      </template>

      <!-- Error state -->
      <template v-else-if="currentStatus === 'error'">
        <span class="video-card__error-icon">!</span>
        <span class="video-card__status-text video-card__status-text--error">生成失败</span>
      </template>

      <!-- Ready state -->
      <template v-else>
        <span class="video-card__play">&#9654;</span>
        <span v-if="formattedDuration" class="video-card__duration">{{ formattedDuration }}</span>
      </template>
    </div>
    <div class="video-card__info">
      <span class="video-card__title">{{ title }}</span>
    </div>
  </div>
</template>

<style scoped>
.video-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  max-width: 320px;
  margin: 8px 0;
  background: var(--bg-card);
}

.video-card__thumbnail {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: var(--bg-hover);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.video-card__play {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  padding-left: 3px;
}

.video-card__duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: var(--overlay-dark);
  color: #fff;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-family: var(--font-mono);
}

.video-card__spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.video-card__status-text {
  font-size: 12px;
  color: var(--text-tertiary);
}

.video-card__status-text--error {
  color: var(--status-error);
}

.video-card__error-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--status-error-light);
  color: var(--status-error);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.video-card__info {
  padding: 10px 14px;
}

.video-card__title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
