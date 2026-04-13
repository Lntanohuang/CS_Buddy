import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { LearningPath, PathNode } from '@/types'
import { mockPath } from '@/mock/data'

export const usePathStore = defineStore('path', () => {
  const path = ref<LearningPath>({ ...mockPath, nodes: mockPath.nodes.map((n) => ({ ...n })) })

  const progressPercent = computed(() =>
    path.value.total_nodes > 0
      ? Math.round((path.value.completed_nodes / path.value.total_nodes) * 100)
      : 0
  )

  const currentNode = computed<PathNode | undefined>(() =>
    path.value.nodes.find((n) => n.status === 'IN_PROGRESS')
  )

  function completeNode(nodeId: string) {
    const node = path.value.nodes.find((n) => n.node_id === nodeId)
    if (node) {
      node.status = 'COMPLETED'
      node.completed_at = new Date().toISOString()
      path.value.completed_nodes += 1

      // Advance next pending node
      const nextNode = path.value.nodes.find((n) => n.status === 'PENDING')
      if (nextNode) {
        nextNode.status = 'IN_PROGRESS'
      }
    }
  }

  function skipNode(nodeId: string) {
    const node = path.value.nodes.find((n) => n.node_id === nodeId)
    if (node) {
      node.status = 'SKIPPED'
    }
  }

  return { path, progressPercent, currentNode, completeNode, skipNode }
})
