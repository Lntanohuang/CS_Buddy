<script setup lang="ts">
import { computed } from 'vue'
import { useMarkdown } from '@/composables/useMarkdown'

const props = defineProps<{
  content: string
}>()

const { render } = useMarkdown()

const renderedHtml = computed(() => render(props.content))

function onRendererClick(event: MouseEvent) {
  const target = event.target as HTMLElement | null
  const btn = target?.closest('.code-block-copy') as HTMLButtonElement | null
  if (!btn) return
  const block = btn.closest('.code-block')
  const code = block?.querySelector('pre code')?.textContent ?? ''
  if (!code) return
  const finish = () => {
    btn.classList.add('is-copied')
    window.setTimeout(() => btn.classList.remove('is-copied'), 1500)
  }
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(code).then(finish).catch(() => finish())
  } else {
    const ta = document.createElement('textarea')
    ta.value = code
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    try { document.execCommand('copy') } catch { /* ignore */ }
    document.body.removeChild(ta)
    finish()
  }
}
</script>

<template>
  <div class="markdown-renderer" v-html="renderedHtml" @click="onRendererClick" />
</template>

<style scoped>
.markdown-renderer {
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 14px;
  line-height: 1.75;
  color: var(--text-primary);
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.markdown-renderer :deep(h1),
.markdown-renderer :deep(h2),
.markdown-renderer :deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
  color: var(--text-primary);
}

.markdown-renderer :deep(p) {
  margin: 0.5em 0;
}

.markdown-renderer :deep(code) {
  background: var(--bg-hover);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: var(--accent-primary);
}

.markdown-renderer :deep(pre) {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 14px 18px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.75em 0;
  font-size: 13px;
  line-height: 1.6;
}

.markdown-renderer :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
  font-size: inherit;
}

/* ===== Code block with header + copy button ===== */
.markdown-renderer :deep(.code-block) {
  position: relative;
  margin: 0.75em 0;
  background: var(--code-bg);
  border-radius: 8px;
  overflow: hidden;
}

.markdown-renderer :deep(.code-block-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 18px 0;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}

.markdown-renderer :deep(.code-block-lang) {
  font-family: var(--font-mono);
  text-transform: lowercase;
  letter-spacing: 0.02em;
}

.markdown-renderer :deep(.code-block-copy) {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 4px;
  opacity: 0;
  transition: opacity 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.markdown-renderer :deep(.code-block:hover .code-block-copy),
.markdown-renderer :deep(.code-block-copy:focus-visible) {
  opacity: 1;
}

.markdown-renderer :deep(.code-block-copy:hover) {
  background: rgba(0, 0, 0, 0.06);
  color: var(--text-primary);
}

.markdown-renderer :deep(.code-block-copy-icon) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s ease;
}

.markdown-renderer :deep(.code-block-copy-icon--check) {
  position: absolute;
  inset: 0;
  opacity: 0;
  color: var(--status-success);
}

.markdown-renderer :deep(.code-block-copy.is-copied) {
  opacity: 1;
  color: var(--status-success);
}

.markdown-renderer :deep(.code-block-copy.is-copied .code-block-copy-icon--copy) {
  opacity: 0;
}

.markdown-renderer :deep(.code-block-copy.is-copied .code-block-copy-icon--check) {
  opacity: 1;
}

/* Pre inside code-block: drop its own bg/radius so the wrapper takes over */
.markdown-renderer :deep(.code-block pre) {
  background: transparent;
  margin: 0;
  padding: 0 18px 14px;
  border-radius: 0;
}

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.markdown-renderer :deep(li) {
  margin: 0.25em 0;
}

.markdown-renderer :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  margin: 0.75em 0;
  padding: 0.5em 1em;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  border-radius: 0 8px 8px 0;
}

.markdown-renderer :deep(a) {
  color: var(--accent-primary);
  text-decoration: none;
}

.markdown-renderer :deep(a:hover) {
  text-decoration: underline;
}

.markdown-renderer :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.75em 0;
  font-size: 13px;
}

.markdown-renderer :deep(th),
.markdown-renderer :deep(td) {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
}

.markdown-renderer :deep(th) {
  background: var(--bg-primary);
  font-weight: 600;
}

.markdown-renderer :deep(hr) {
  border: none;
  border-top: 1px solid var(--border);
  margin: 1em 0;
}
</style>
