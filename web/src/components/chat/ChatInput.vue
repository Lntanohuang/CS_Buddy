<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  disabled: boolean
}>()

const emit = defineEmits<{
  send: [text: string]
}>()

const inputText = ref('')
const isFocused = ref(false)
const quickPrompts = ['解释这段代码', '出一道类似题', '我没听懂', '帮我总结']

function handleSend() {
  const text = inputText.value.trim()
  if (!text) return
  emit('send', text)
  inputText.value = ''
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}

function handleQuickPrompt(prompt: string) {
  if (props.disabled) return
  emit('send', prompt)
  inputText.value = ''
}
</script>

<template>
  <div class="chat-input-wrapper">
    <div class="chat-input-prompts" aria-label="快捷提问">
      <button
        v-for="prompt in quickPrompts"
        :key="prompt"
        class="chat-input-prompt"
        type="button"
        :disabled="disabled"
        @click="handleQuickPrompt(prompt)"
      >
        {{ prompt }}
      </button>
    </div>
    <div
      class="chat-input-container"
      :class="{ 'chat-input-container--focused': isFocused, 'chat-input-container--disabled': disabled }"
    >
      <el-input
        v-model="inputText"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 6 }"
        placeholder="问小海豹一个学习问题..."
        :disabled="disabled"
        @keydown="handleKeydown"
        @focus="isFocused = true"
        @blur="isFocused = false"
        class="chat-input-textarea"
      />
      <button
        class="chat-input-send"
        :class="{ 'chat-input-send--active': inputText.trim() && !disabled }"
        :disabled="disabled || !inputText.trim()"
        @click="handleSend"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="19" x2="12" y2="5" />
          <polyline points="5 12 12 5 19 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-input-wrapper {
  position: relative;
  z-index: 4;
  flex-shrink: 0;
  margin-top: auto;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.chat-input-prompts {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  width: 100%;
  margin: 0 0 8px;
}

.chat-input-prompt {
  min-height: 28px;
  padding: 0 10px;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 650;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.chat-input-prompt:hover:not(:disabled) {
  background: transparent;
  color: var(--accent-primary);
}

.chat-input-prompt:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.chat-input-container {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  width: 100%;
  margin: 0;
  background: transparent;
  border: 0;
  border-bottom: 1px solid rgba(29, 29, 31, 0.16);
  border-radius: 0;
  padding: 8px 0 10px;
  transition: all 0.2s ease;
  box-shadow: none;
}

.chat-input-container--focused {
  border-bottom-color: var(--accent-primary);
  box-shadow: none;
}

.chat-input-container--disabled {
  opacity: 0.6;
  background: transparent;
}

.chat-input-textarea {
  flex: 1;
}

.chat-input-textarea :deep(.el-textarea__inner) {
  background: transparent;
  border: none;
  box-shadow: none !important;
  padding: 6px 0;
  resize: none;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
}

.chat-input-textarea :deep(.el-textarea__inner)::placeholder {
  color: var(--text-secondary);
}

.chat-input-send {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--border);
  color: var(--text-secondary);
}

.chat-input-send--active {
  background: var(--accent-primary);
  color: var(--bg-card);
  box-shadow: var(--shadow-md);
}

.chat-input-send--active:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
}

.chat-input-send:disabled {
  cursor: not-allowed;
}

@media (max-width: 720px) {
  .chat-input-wrapper {
    padding: 0;
  }
}
</style>
