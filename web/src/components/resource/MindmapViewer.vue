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

.mindmap-node {
  display: flex;
  flex-direction: column;
  align-items: center;
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
  display: flex;
  justify-content: center;
  gap: clamp(16px, 3vw, 40px);
  padding-top: 24px;
  position: relative;
}

.mindmap-children::before {
  content: '';
  position: absolute;
  top: 12px;
  left: 20px;
  right: 20px;
  height: 1px;
  background: var(--border);
}

.mindmap-children--nested {
  gap: clamp(14px, 2.6vw, 32px);
  padding-top: 20px;
}

.mindmap-branch {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  padding-top: 12px;
}

.mindmap-branch::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 1px;
  height: 12px;
  background: var(--border);
  transform: translateX(-50%);
}

.mindmap-connector {
  display: none;
}

.mindmap-subtree {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0;
}

.mindmap-subtree :deep(.mindmap-node > .mindmap-pill) {
  margin-top: 6px;
  margin-bottom: 6px;
}
</style>
