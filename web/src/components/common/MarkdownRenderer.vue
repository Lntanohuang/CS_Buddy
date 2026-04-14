<script setup lang="ts">
import { computed } from 'vue'
import { useMarkdown } from '@/composables/useMarkdown'

const props = defineProps<{
  content: string
}>()

const { render } = useMarkdown()

const renderedHtml = computed(() => render(props.content))
</script>

<template>
  <div class="markdown-renderer" v-html="renderedHtml" />
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
  background: var(--text-primary);
  color: var(--border);
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

.markdown-renderer :deep(ul),
.markdown-renderer :deep(ol) {
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.markdown-renderer :deep(li) {
  margin: 0.25em 0;
}

.markdown-renderer :deep(blockquote) {
  border-left: 3px solid #4A7C6F;
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
