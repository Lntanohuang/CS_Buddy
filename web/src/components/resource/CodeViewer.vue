<script setup lang="ts">
import { computed, ref } from 'vue'
import hljs from 'highlight.js'

const props = defineProps<{
  code: string
  language: string
  expectedOutput?: string
}>()

const copied = ref(false)

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
      <span class="code-viewer__lang">{{ language }}</span>
      <button class="code-viewer__copy" @click="copyCode">
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
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 8px 0;
}

.code-viewer__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 14px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border);
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
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 3px 10px;
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
  padding: 16px;
  background: var(--code-bg);
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
}

.code-viewer__code {
  font-family: var(--font-mono);
  color: var(--code-text);
}

.code-viewer__output {
  border-top: 1px solid var(--border);
}

.code-viewer__output-label {
  padding: 6px 14px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text-tertiary);
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border);
}

.code-viewer__output-pre {
  margin: 0;
  padding: 12px 16px;
  background: var(--bg-primary);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}
</style>
