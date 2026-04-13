<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEvalStore } from '@/stores/eval'
import type { Evaluation } from '@/types'
import QuizPanel from '@/components/evaluate/QuizPanel.vue'
import EvalReport from '@/components/evaluate/EvalReport.vue'

const evalStore = useEvalStore()

// Dialog state
const dialogVisible = ref(false)
const selectedKP = ref('')

const knowledgePoints = [
  { value: 'array', label: '数组 (Array)' },
  { value: 'linked_list', label: '链表 (Linked List)' },
  { value: 'stack', label: '栈 (Stack)' },
  { value: 'hash_table', label: '哈希表 (Hash Table)' },
  { value: 'sorting', label: '排序 (Sorting)' },
  { value: 'binary_tree', label: '二叉树 (Binary Tree)' },
  { value: 'graph', label: '图 (Graph)' },
]

function openDialog() {
  selectedKP.value = ''
  dialogVisible.value = true
}

function confirmStartEval() {
  if (!selectedKP.value) return
  evalStore.startEval(selectedKP.value)
  dialogVisible.value = false
}

function onAnswer(payload: { questionId: string; answer: string }) {
  evalStore.submitAnswer(payload.questionId, payload.answer)
}

async function onSubmit() {
  await evalStore.submitEval()
}

function onReportClose() {
  evalStore.clearActiveEval()
}

function scoreColor(score?: number): string {
  const s = score ?? 0
  if (s >= 70) return '#67c23a'
  if (s >= 40) return '#e6a23c'
  return '#f56c6c'
}

function recommendationTag(eval_: Evaluation) {
  const action = eval_.recommendation?.action
  if (action === 'ADVANCE') return { label: '继续前进', type: 'success' as const }
  if (action === 'SUPPLEMENT') return { label: '补充练习', type: 'warning' as const }
  if (action === 'RETREAT') return { label: '回顾基础', type: 'danger' as const }
  return { label: '-', type: 'info' as const }
}

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const typeLabel: Record<string, string> = {
  MINI_QUIZ: '随堂小测',
  STAGE_TEST: '阶段测试',
  USER_REQUEST: '主动评估',
}

const isQuizMode = computed(() => evalStore.activeEval !== null)
const isPending = computed(() => evalStore.activeEval?.status === 'PENDING' || evalStore.activeEval?.status === 'SUBMITTED')
const isAnalyzed = computed(() => evalStore.activeEval?.status === 'ANALYZED')
</script>

<template>
  <div class="eval-view">
    <!-- Quiz / Report Mode -->
    <template v-if="isQuizMode && evalStore.activeEval">
      <div v-if="evalStore.isSubmitting" class="loading-state">
        <el-icon class="is-loading" :size="40" color="var(--el-color-primary)">
          <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
            <path fill="currentColor" d="M512 64a32 32 0 0 1 32 32v192a32 32 0 0 1-64 0V96a32 32 0 0 1 32-32zm0 640a32 32 0 0 1 32 32v192a32 32 0 1 1-64 0V736a32 32 0 0 1 32-32zm448-192a32 32 0 0 1-32 32H736a32 32 0 1 1 0-64h192a32 32 0 0 1 32 32zM288 512a32 32 0 0 1-32 32H64a32 32 0 0 1 0-64h192a32 32 0 0 1 32 32z"/>
          </svg>
        </el-icon>
        <p>正在分析评估结果...</p>
      </div>

      <QuizPanel
        v-else-if="isPending"
        :evaluation="evalStore.activeEval"
        @answer="onAnswer"
        @submit="onSubmit"
      />

      <EvalReport
        v-else-if="isAnalyzed"
        :evaluation="evalStore.activeEval"
        @close="onReportClose"
      />
    </template>

    <!-- History Mode -->
    <template v-else>
      <div class="history-header">
        <h2>评估中心</h2>
        <el-button type="primary" @click="openDialog">发起评估</el-button>
      </div>

      <el-table :data="evalStore.history" stripe style="width: 100%">
        <el-table-column label="时间" width="140">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="knowledge_point" label="知识点" width="160" />

        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ typeLabel[row.type] ?? row.type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="得分" width="100">
          <template #default="{ row }">
            <span
              v-if="row.score !== undefined"
              :style="{ color: scoreColor(row.score), fontWeight: 600 }"
            >
              {{ row.score }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="掌握度" width="140">
          <template #default="{ row }">
            <el-progress
              v-if="row.mastery_level !== undefined"
              :percentage="Math.round(row.mastery_level * 100)"
              :stroke-width="10"
              :color="scoreColor(Math.round(row.mastery_level * 100))"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="建议" width="120">
          <template #default="{ row }">
            <el-tag
              v-if="row.recommendation"
              :type="recommendationTag(row).type"
              size="small"
            >
              {{ recommendationTag(row).label }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- Start Eval Dialog -->
      <el-dialog v-model="dialogVisible" title="发起评估" width="420px">
        <el-select
          v-model="selectedKP"
          placeholder="选择知识点"
          style="width: 100%"
        >
          <el-option
            v-for="kp in knowledgePoints"
            :key="kp.value"
            :label="kp.label"
            :value="kp.value"
          />
        </el-select>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :disabled="!selectedKP" @click="confirmStartEval">
            开始评估
          </el-button>
        </template>
      </el-dialog>
    </template>
  </div>
</template>

<style scoped>
.eval-view {
  padding: 24px;
  max-width: 960px;
  margin: 0 auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-header h2 {
  margin: 0;
  font-size: 22px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: var(--el-text-color-secondary);
}

.loading-state p {
  margin-top: 16px;
  font-size: 15px;
}
</style>
