<script setup lang="ts">
import { computed } from 'vue'
import TreeDiagramNode, { type TreeNode } from './TreeDiagramNode.vue'

const props = defineProps<{
  code: string
}>()

const tree = computed(() => parseMermaidTree(props.code))

function parseMermaidTree(code: string): TreeNode | null {
  const labels = new Map<string, string>()
  const children = new Map<string, string[]>()
  const childIds = new Set<string>()
  const lines = code.split(/\r?\n/)

  for (const line of lines) {
    const edgeMatch = line.match(
      /^\s*([A-Za-z][\w-]*)(?:\["?([^"\]]+)"?\])?\s*-->\s*([A-Za-z][\w-]*)(?:\["?([^"\]]+)"?\])?/,
    )

    if (!edgeMatch) continue

    const [, parentId, parentLabel, childId, childLabel] = edgeMatch
    labels.set(parentId, parentLabel ?? labels.get(parentId) ?? parentId)
    labels.set(childId, childLabel ?? labels.get(childId) ?? childId)

    if (!children.has(parentId)) {
      children.set(parentId, [])
    }

    children.get(parentId)?.push(childId)
    childIds.add(childId)
  }

  if (labels.size === 0 || children.size === 0) {
    return null
  }

  const rootId = [...labels.keys()].find((id) => !childIds.has(id))
  if (!rootId) return null

  function buildNode(id: string, seen = new Set<string>()): TreeNode {
    if (seen.has(id)) {
      return { id, label: labels.get(id) ?? id, children: [] }
    }

    const nextSeen = new Set(seen)
    nextSeen.add(id)

    return {
      id,
      label: labels.get(id) ?? id,
      children: (children.get(id) ?? []).map((childId) => buildNode(childId, nextSeen)),
    }
  }

  return buildNode(rootId)
}
</script>

<template>
  <div class="tree-diagram">
    <TreeDiagramNode v-if="tree" :node="tree" />
    <p v-else class="tree-diagram__empty">图示暂不可用</p>
  </div>
</template>

<style scoped>
.tree-diagram {
  width: 100%;
  overflow: auto;
  padding: 18px 0 8px;
}

.tree-diagram :deep(.tree-node) {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 54px;
}

.tree-diagram :deep(.tree-node__label) {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 42px;
  padding: 0 12px;
  border: 1px solid rgba(var(--accent-primary-rgb), 0.26);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 750;
  box-shadow: var(--shadow-sm);
}

.tree-diagram :deep(.tree-node__children) {
  position: relative;
  display: flex;
  justify-content: center;
  gap: clamp(18px, 3vw, 44px);
  padding-top: 32px;
}

.tree-diagram :deep(.tree-node__children::before) {
  content: "";
  position: absolute;
  top: 13px;
  left: 24px;
  right: 24px;
  height: 1px;
  background: rgba(var(--accent-primary-rgb), 0.28);
}

.tree-diagram :deep(.tree-node__children > .tree-node::before) {
  content: "";
  position: absolute;
  top: -19px;
  left: 50%;
  width: 1px;
  height: 19px;
  background: rgba(var(--accent-primary-rgb), 0.28);
}

.tree-diagram__empty {
  margin: 0;
  color: var(--text-secondary);
  font-size: 13px;
}
</style>
