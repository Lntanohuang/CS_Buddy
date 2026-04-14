<script setup lang="ts">
import { computed } from 'vue'

defineOptions({
  name: 'MindmapViewer',
})

interface MindmapNode {
  name: string
  children?: MindmapNode[]
}

const props = withDefaults(defineProps<{
  data: MindmapNode
  depth?: number
  isRoot?: boolean
}>(), {
  depth: 0,
  isRoot: true,
})

const pillClass = computed(() => {
  if (props.depth === 0) return 'mindmap-pill--root'
  if (props.depth === 1) return 'mindmap-pill--l1'
  return 'mindmap-pill--l2'
})
</script>

<template>
  <div :class="isRoot ? 'mindmap-viewer' : 'mindmap-viewer--nested'">
    <div class="mindmap-node" :class="{ 'mindmap-node--root': depth === 0 }">
      <span class="mindmap-pill" :class="pillClass">{{ data.name }}</span>
      <div
        v-if="data.children?.length"
        class="mindmap-children"
        :class="{ 'mindmap-children--nested': depth > 0 }"
      >
        <div
          v-for="(child, i) in data.children"
          :key="i"
          class="mindmap-branch"
        >
          <div class="mindmap-connector">
            <span class="mindmap-connector__vline" />
            <span class="mindmap-connector__hline" />
          </div>
          <div class="mindmap-subtree">
            <MindmapViewer :data="child" :depth="depth + 1" :is-root="false" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mindmap-viewer {
  padding: 16px 0;
  overflow-x: auto;
}

.mindmap-viewer--nested {
  width: max-content;
}

.mindmap-node--root {
  display: flex;
  flex-direction: column;
}

.mindmap-pill {
  display: inline-block;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  white-space: nowrap;
}

.mindmap-pill--root {
  background: var(--accent-primary);
  color: #fff;
  font-weight: 600;
}

.mindmap-pill--l1 {
  background: var(--bg-card);
  border: 1px solid var(--accent-primary);
  color: var(--accent-primary);
}

.mindmap-pill--l2 {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
}

.mindmap-children {
  margin-left: 16px;
  padding-top: 4px;
}

.mindmap-children--nested {
  margin-left: 12px;
}

.mindmap-branch {
  display: flex;
  align-items: flex-start;
  position: relative;
}

.mindmap-connector {
  display: flex;
  align-items: flex-start;
  flex-shrink: 0;
  width: 20px;
  position: relative;
  height: 100%;
  min-height: 32px;
}

.mindmap-connector__vline {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--border);
}

.mindmap-connector__hline {
  position: absolute;
  left: 0;
  top: 16px;
  width: 20px;
  height: 1px;
  background: var(--border);
}

.mindmap-branch:last-child > .mindmap-connector > .mindmap-connector__vline {
  height: 16px;
}

.mindmap-subtree {
  display: flex;
  flex-direction: column;
  padding: 6px 0;
}

.mindmap-subtree :deep(.mindmap-node > .mindmap-pill) {
  margin-top: 6px;
  margin-bottom: 6px;
}
</style>
