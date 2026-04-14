<script setup lang="ts">
defineProps<{
  count: number
}>()

defineEmits<{
  click: []
}>()
</script>

<template>
  <button class="bell-btn" @click="$emit('click')" title="通知">
    <span class="bell-icon">🔔</span>
    <span v-if="count > 0" class="bell-badge">{{ count > 99 ? '99+' : count }}</span>
  </button>
</template>

<style scoped>
.bell-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  transition: background 0.15s ease;
}

.bell-btn:hover {
  background: var(--bg-hover);
}

.bell-icon {
  font-size: 16px;
  line-height: 1;
}

.bell-badge {
  position: absolute;
  top: 2px;
  right: 0;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background: var(--status-error);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  line-height: 16px;
  text-align: center;
  pointer-events: none;
}
</style>
