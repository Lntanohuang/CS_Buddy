<script setup lang="ts">
import { ref, watch, onMounted, nextTick, shallowRef } from 'vue'

const props = defineProps<{
  code: string
}>()

const svgOutput = ref('')
const hasError = ref(false)
let idCounter = 0
const mermaidInstance = shallowRef<typeof import('mermaid')['default'] | null>(null)

function generateId(): string {
  return `mermaid-${Date.now()}-${idCounter++}`
}

function readCssVar(name: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return value
}

async function loadMermaid() {
  if (mermaidInstance.value) return mermaidInstance.value
  try {
    const mod = await import('mermaid')
    const m = mod.default
    m.initialize({
      startOnLoad: false,
      theme: 'neutral',
      themeVariables: {
        primaryColor: readCssVar('--accent-primary-light'),
        primaryBorderColor: readCssVar('--accent-primary'),
        primaryTextColor: readCssVar('--text-primary'),
        lineColor: readCssVar('--border-strong'),
        secondaryColor: readCssVar('--accent-secondary-light'),
        tertiaryColor: readCssVar('--bg-hover'),
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif',
        fontSize: '13px',
      },
    })
    mermaidInstance.value = m
    return m
  } catch {
    hasError.value = true
    return null
  }
}

async function renderDiagram() {
  if (!props.code.trim()) {
    svgOutput.value = ''
    hasError.value = false
    return
  }
  try {
    const m = await loadMermaid()
    if (!m) return
    const id = generateId()
    const { svg } = await m.render(id, props.code.trim())
    svgOutput.value = svg
    hasError.value = false
  } catch {
    svgOutput.value = ''
    hasError.value = true
  }
}

onMounted(() => {
  nextTick(() => renderDiagram())
})

watch(() => props.code, () => {
  nextTick(() => renderDiagram())
})
</script>

<template>
  <div class="mermaid-renderer">
    <div v-if="hasError" class="mermaid-renderer__error">
      <pre class="mermaid-renderer__raw">{{ code }}</pre>
    </div>
    <div v-else class="mermaid-renderer__svg" v-html="svgOutput" />
  </div>
</template>

<style scoped>
.mermaid-renderer {
  margin: 8px 0;
  overflow-x: auto;
}

.mermaid-renderer__svg {
  display: flex;
  justify-content: center;
}

.mermaid-renderer__svg :deep(svg) {
  max-width: 100%;
  height: auto;
}

.mermaid-renderer__error {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.mermaid-renderer__raw {
  margin: 0;
  padding: 14px 18px;
  background: var(--bg-hover);
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  overflow-x: auto;
}
</style>
