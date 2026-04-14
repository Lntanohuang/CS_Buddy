<script setup lang="ts">
defineProps<{
  title: string
  reason: string
  estMinutes: number
}>()

defineEmits<{
  start: []
  dismiss: []
}>()
</script>

<template>
  <div class="recommend-card">
    <button class="dismiss-btn" @click="$emit('dismiss')" title="关闭">&times;</button>

    <div class="card-body">
      <div class="card-label">🌿 今日推荐</div>

      <div class="card-middle">
        <span class="card-title">{{ title }}</span>
        <span class="card-reason">{{ reason }}</span>
      </div>

      <div class="card-right">
        <span class="card-time">~{{ estMinutes }} 分钟</span>
        <button class="start-btn" @click="$emit('start')">开始学习</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.recommend-card {
  position: relative;
  background: var(--accent-primary-light);
  border-left: 4px solid var(--accent-primary);
  border-radius: var(--radius-md);
  padding: 14px 16px;
}

.dismiss-btn {
  position: absolute;
  top: 6px;
  right: 8px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  border-radius: var(--radius-sm);
  background: none;
  color: var(--text-secondary);
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.15s ease;
}

.dismiss-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.card-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-label {
  font-size: 12px;
  color: var(--accent-primary);
  font-weight: 600;
  white-space: nowrap;
}

.card-middle {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-reason {
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  flex-shrink: 0;
}

.card-time {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.start-btn {
  padding: 4px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: none;
  color: var(--accent-primary);
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.15s ease;
  white-space: nowrap;
}

.start-btn:hover {
  background: rgba(74, 124, 111, 0.1);
}
</style>
