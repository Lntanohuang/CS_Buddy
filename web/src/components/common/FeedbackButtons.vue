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
    <template v-if="!submitted">
      <el-button
        size="small"
        text
        :icon="/* thumb up */ undefined"
        @click="handleFeedback('USEFUL')"
      >
        <el-icon><i class="el-icon-thumb-up" /></el-icon>
        👍 有用
      </el-button>
      <el-button
        size="small"
        text
        @click="handleFeedback('NOT_USEFUL')"
      >
        👎 没用
      </el-button>
    </template>
    <span v-else class="feedback-thanks">感谢反馈</span>
  </div>
</template>

<style scoped>
.feedback-buttons {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
}

.feedback-thanks {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
