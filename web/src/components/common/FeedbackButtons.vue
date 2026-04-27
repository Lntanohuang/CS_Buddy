<script setup lang="ts">
import { shallowRef } from 'vue'

const props = defineProps<{
  messageId: string
}>()

const emit = defineEmits<{
  feedback: [payload: { messageId: string; feedback: 'USEFUL' | 'NOT_USEFUL' }]
}>()

const submitted = shallowRef(false)

function handleFeedback(feedback: 'USEFUL' | 'NOT_USEFUL') {
  if (submitted.value) return
  submitted.value = true
  emit('feedback', { messageId: props.messageId, feedback })
}
</script>

<template>
  <div class="feedback-buttons">
    <Transition name="feedback-fade" mode="out-in">
      <div v-if="!submitted" key="buttons" class="feedback-buttons__actions">
        <button
          class="feedback-btn"
          type="button"
          @click="handleFeedback('USEFUL')"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
          </svg>
          <span>有用</span>
        </button>
        <button
          class="feedback-btn"
          type="button"
          @click="handleFeedback('NOT_USEFUL')"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17" />
          </svg>
          <span>没用</span>
        </button>
      </div>
      <div v-else key="thanks" class="feedback-buttons__thanks">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        <span>感谢反馈</span>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.feedback-buttons {
  margin-top: 10px;
  min-height: 30px;
}

.feedback-buttons__actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.feedback-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border: 1px solid var(--border);
  border-radius: 100px;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 12px;
  font-family: system-ui, -apple-system, sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.4;
}

.feedback-btn:hover {
  background: var(--bg-primary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.feedback-btn:active {
  transform: scale(0.96);
}

.feedback-buttons__thanks {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 0;
  color: var(--text-secondary);
  font-size: 12px;
  font-family: system-ui, -apple-system, sans-serif;
}

/* Transition */
.feedback-fade-enter-active,
.feedback-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.feedback-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.feedback-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
