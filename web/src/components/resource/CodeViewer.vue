<script setup lang="ts">
import { computed, ref } from 'vue'
import hljs from 'highlight.js'

const props = defineProps<{
  code: string
  language: string
  expectedOutput?: string
}>()

const copied = ref(false)
const languageLabel = computed(() => {
  const map: Record<string, string> = {
    js: 'JavaScript',
    javascript: 'JavaScript',
    ts: 'TypeScript',
    typescript: 'TypeScript',
    py: 'Python',
    python: 'Python',
    java: 'Java',
    cpp: 'C++',
  }

  return map[props.language.toLowerCase()] ?? props.language
})

const highlightedCode = computed(() => {
  if (props.language && hljs.getLanguage(props.language)) {
    try {
      return hljs.highlight(props.code, { language: props.language }).value
    } catch {
      // fall through
    }
  }
  return props.code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
})

async function copyCode() {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // clipboard not available
  }
}
</script>

<template>
  <div class="code-viewer">
    <div class="code-viewer__header">
      <span class="code-viewer__lang">{{ languageLabel }} 示例</span>
      <button class="code-viewer__copy" type="button" @click="copyCode">
        {{ copied ? '已复制' : '复制代码' }}
      </button>
    </div>
    <pre class="code-viewer__pre"><code class="code-viewer__code" v-html="highlightedCode" /></pre>
    <div v-if="expectedOutput" class="code-viewer__output">
      <div class="code-viewer__output-label">预期输出</div>
      <pre class="code-viewer__output-pre">{{ expectedOutput }}</pre>
    </div>
  </div>
</template>

<style scoped>
.code-viewer {
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.76);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.58);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.66), 0 8px 22px rgba(15, 23, 42, 0.035);
  overflow: hidden;
  margin: 8px 0;
}

.code-viewer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(var(--accent-primary-rgb), 0.08);
  border-bottom: 0;
  border-radius: 12px 12px 0 0;
}

.code-viewer__lang {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 11px;
  font-weight: 500;
}

.code-viewer__copy {
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(var(--accent-primary-rgb), 0.14);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.code-viewer__copy:hover {
  border-color: var(--border-strong);
  color: var(--text-primary);
}

.code-viewer__pre {
  margin: 0;
  padding: 18px;
  background: var(--code-bg);
  border-radius: 0 0 12px 12px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}

.code-viewer__code {
  font-family: var(--font-mono);
  color: var(--code-text);
}

.code-viewer__output {
  margin-top: 8px;
  border: 1px solid rgba(var(--accent-primary-rgb), 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.code-viewer__output-label {
  padding: 6px 14px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-tertiary);
  background: rgba(255, 255, 255, 0.72);
  border-bottom: 1px solid rgba(var(--accent-primary-rgb), 0.08);
}

.code-viewer__output-pre {
  margin: 0;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.58);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}
</style>
