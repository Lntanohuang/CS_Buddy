<script setup lang="ts">
export type TreeNode = {
  id: string
  label: string
  children: TreeNode[]
}

defineOptions({
  name: 'TreeDiagramNode',
})

defineProps<{
  node: TreeNode
}>()
</script>

<template>
  <div class="tree-node">
    <div class="tree-node__label">{{ node.label }}</div>
    <div v-if="node.children.length" class="tree-node__children">
      <TreeDiagramNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
      />
    </div>
  </div>
</template>
