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
  <div class="markdown-body" v-html="renderedHtml" />
</template>

<style scoped>
.markdown-body {
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.7;
}
</style>
