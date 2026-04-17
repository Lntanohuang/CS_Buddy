import { ref, shallowRef, computed } from 'vue'
import { defineStore } from 'pinia'
import type { LearningPath, PathNode } from '@/types'
import { mockPath } from '@/mock/data'

export const usePathStore = defineStore('path', () => {
  const path = ref<LearningPath>({ ...mockPath, nodes: mockPath.nodes.map((n) => ({ ...n })) })
  const updateHint = shallowRef('')

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

  function addNodes(newNodes: PathNode[]) {
    for (const node of newNodes) {
      if (!path.value.nodes.find((n) => n.node_id === node.node_id)) {
        path.value.nodes.push(node)
        path.value.total_nodes += 1
      }
    }
    updateHint.value = `🔄 根据最新对话，已新增 ${newNodes.length} 个学习节点`
    setTimeout(() => { updateHint.value = '' }, 5000)
  }

  function reorderAfterEval(knowledgePoint: string, action: 'ADVANCE' | 'SUPPLEMENT' | 'RETREAT') {
    if (action === 'ADVANCE') {
      // Complete the current node for this knowledge point
      const node = path.value.nodes.find(
        (n) => n.knowledge_point === knowledgePoint && n.status === 'IN_PROGRESS'
      )
      if (node) completeNode(node.node_id)
      updateHint.value = '🔄 根据测评结果，已推进学习路径'
    } else if (action === 'SUPPLEMENT') {
      // Add a supplement node after the current one
      const idx = path.value.nodes.findIndex(
        (n) => n.knowledge_point === knowledgePoint
      )
      if (idx >= 0) {
        const supplementNode: PathNode = {
          node_id: `node_sup_${Date.now()}`,
          title: `${knowledgePoint} 补充练习`,
          knowledge_point: knowledgePoint,
          order: path.value.nodes[idx].order + 0.5,
          status: 'PENDING',
          difficulty: 'INTERMEDIATE',
          est_minutes: 45,
          prerequisites: [path.value.nodes[idx].node_id],
          is_supplement: true,
        }
        path.value.nodes.splice(idx + 1, 0, supplementNode)
        path.value.total_nodes += 1
        updateHint.value = '🔄 根据测评结果，已添加补充练习节点'
      }
    } else {
      updateHint.value = '🔄 根据测评结果，建议回顾前置知识'
    }
    setTimeout(() => { updateHint.value = '' }, 5000)
  }

  function dismissHint() {
    updateHint.value = ''
  }

  return { path, progressPercent, currentNode, updateHint, completeNode, skipNode, addNodes, reorderAfterEval, dismissHint }
})
