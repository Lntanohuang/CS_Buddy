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
  if (s >= 70) return 'var(--score-high)'
  if (s >= 40) return 'var(--score-mid)'
  return 'var(--score-low)'
}

function recommendationTag(eval_: Evaluation) {
  const action = eval_.recommendation?.action
  if (action === 'ADVANCE') return { label: '推进', color: 'var(--score-high)', bg: 'var(--score-high-light)' }
  if (action === 'SUPPLEMENT') return { label: '补强', color: 'var(--score-mid)', bg: 'var(--score-mid-light)' }
  if (action === 'RETREAT') return { label: '回退', color: 'var(--score-low)', bg: 'var(--score-low-light)' }
  return { label: '-', color: 'var(--text-secondary)', bg: 'var(--bg-primary)' }
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
    <Transition name="view-fade" mode="out-in">
      <div v-if="isQuizMode && evalStore.activeEval" key="quiz-mode">
        <!-- Loading state -->
        <div v-if="evalStore.isSubmitting" class="loading-state">
          <div class="loading-spinner">
            <div class="spinner-ring" />
          </div>
          <p class="loading-text">AI 正在分析你的答案...</p>
          <p class="loading-subtext">请稍候，智能评估即将完成</p>
        </div>

        <!-- Quiz -->
        <QuizPanel
          v-else-if="isPending"
          :evaluation="evalStore.activeEval"
          @answer="onAnswer"
          @submit="onSubmit"
        />

        <!-- Report -->
        <EvalReport
          v-else-if="isAnalyzed"
          :evaluation="evalStore.activeEval"
          @close="onReportClose"
        />
      </div>

      <!-- History Mode -->
      <div v-else key="history-mode">
        <div class="history-header">
          <h2 class="page-title">评估中心</h2>
          <button class="start-eval-btn" @click="openDialog">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            发起评估
          </button>
        </div>

        <!-- Empty state -->
        <div v-if="!evalStore.history || evalStore.history.length === 0" class="empty-state">
          <div class="empty-illustration">
            <div class="notepad">
              <div class="notepad-header" />
              <div class="notepad-line" />
              <div class="notepad-line notepad-line--short" />
              <div class="notepad-line" />
              <div class="notepad-line notepad-line--medium" />
            </div>
          </div>
          <p class="empty-title">暂无评估记录</p>
          <p class="empty-desc">点击「发起评估」开始你的第一次知识评估</p>
        </div>

        <!-- History cards -->
        <div v-else class="history-list">
          <div
            v-for="item in evalStore.history"
            :key="item.eval_id"
            class="history-card"
          >
            <!-- Left: score circle -->
            <div
              class="history-score"
              :style="{ background: scoreColor(item.score) }"
            >
              <span class="history-score-num">{{ item.score ?? '-' }}</span>
            </div>

            <!-- Middle: info -->
            <div class="history-info">
              <div class="history-info-top">
                <span class="history-kp">{{ item.knowledge_point }}</span>
                <span class="history-type-pill">{{ typeLabel[item.type] ?? item.type }}</span>
              </div>
              <div class="history-info-bottom">
                <span class="history-date">{{ formatTime(item.created_at) }}</span>
                <span class="history-count">{{ item.correct_count ?? 0 }}/{{ item.question_count }} 正确</span>
              </div>
            </div>

            <!-- Right: mastery + recommendation -->
            <div class="history-right">
              <div class="mastery-mini">
                <div class="mastery-mini-track">
                  <div
                    class="mastery-mini-fill"
                    :style="{
                      width: Math.round((item.mastery_level ?? 0) * 100) + '%',
                      background: scoreColor(Math.round((item.mastery_level ?? 0) * 100)),
                    }"
                  />
                </div>
                <span class="mastery-mini-label">{{ Math.round((item.mastery_level ?? 0) * 100) }}%</span>
              </div>
              <span
                v-if="item.recommendation"
                class="rec-pill"
                :style="{
                  color: recommendationTag(item).color,
                  background: recommendationTag(item).bg,
                }"
              >
                {{ recommendationTag(item).label }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Start Eval Dialog -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="dialogVisible" class="modal-overlay" @click.self="dialogVisible = false">
          <div class="modal-card">
            <div class="modal-header">
              <h3 class="modal-title">发起评估</h3>
              <button class="modal-close" @click="dialogVisible = false">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <div class="modal-body">
              <label class="modal-label">选择知识点</label>
              <select v-model="selectedKP" class="modal-select">
                <option value="" disabled>请选择知识点</option>
                <option
                  v-for="kp in knowledgePoints"
                  :key="kp.value"
                  :value="kp.value"
                >
                  {{ kp.label }}
                </option>
              </select>
            </div>
            <div class="modal-footer">
              <button class="modal-btn modal-btn--cancel" @click="dialogVisible = false">取消</button>
              <button
                class="modal-btn modal-btn--primary"
                :class="{ 'is-disabled': !selectedKP }"
                :disabled="!selectedKP"
                @click="confirmStartEval"
              >
                开始评估
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.eval-view {
  padding: 32px 24px;
  max-width: 800px;
  margin: 0 auto;
}

/* View transitions */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: all 0.3s ease;
}

.view-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.view-fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* History header */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.page-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
}

.start-eval-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  font-size: 14px;
  font-weight: 600;
  color: var(--bg-card);
  background: var(--accent-primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent-primary) 30%, transparent);
}

.start-eval-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px color-mix(in srgb, var(--accent-primary) 40%, transparent);
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 0;
}

.empty-illustration {
  margin-bottom: 24px;
}

.notepad {
  width: 72px;
  height: 88px;
  background: var(--bg-card);
  border: 2px solid var(--border);
  border-radius: 8px;
  padding: 16px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.notepad-header {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: var(--accent-primary);
  margin-bottom: 4px;
}

.notepad-line {
  width: 100%;
  height: 3px;
  border-radius: 1.5px;
  background: var(--border);
}

.notepad-line--short {
  width: 55%;
}

.notepad-line--medium {
  width: 75%;
}

.empty-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-desc {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* History list */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
  cursor: default;
}

.history-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.history-score {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  flex-shrink: 0;
}

.history-score-num {
  font-size: 18px;
  font-weight: 800;
  color: var(--bg-card);
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-info-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.history-kp {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-type-pill {
  display: inline-flex;
  align-items: center;
  padding: 1px 8px;
  border-radius: 20px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.history-info-bottom {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-date {
  font-size: 13px;
  color: var(--text-secondary);
}

.history-count {
  font-size: 13px;
  color: var(--text-tertiary);
}

.history-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.mastery-mini {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mastery-mini-track {
  width: 64px;
  height: 5px;
  border-radius: 3px;
  background: var(--border);
  overflow: hidden;
}

.mastery-mini-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.mastery-mini-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  min-width: 30px;
  text-align: right;
}

.rec-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
}

.loading-spinner {
  margin-bottom: 20px;
}

.spinner-ring {
  width: 44px;
  height: 44px;
  border: 3px solid var(--border);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.loading-subtext {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--overlay-dark);
  backdrop-filter: blur(4px);
}

.modal-card {
  width: 420px;
  max-width: 90vw;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-close:hover {
  background: var(--bg-hover);
  color: var(--text-tertiary);
}

.modal-body {
  padding: 20px 24px;
}

.modal-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.modal-select {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s ease;
  appearance: auto;
  box-sizing: border-box;
}

.modal-select:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent-primary) 10%, transparent);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 24px 20px;
}

.modal-btn {
  padding: 9px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

.modal-btn--cancel {
  background: var(--bg-hover);
  color: var(--text-tertiary);
}

.modal-btn--cancel:hover {
  background: var(--border);
}

.modal-btn--primary {
  background: var(--accent-primary);
  color: var(--bg-card);
  box-shadow: 0 2px 6px color-mix(in srgb, var(--accent-primary) 30%, transparent);
}

.modal-btn--primary:hover:not(.is-disabled) {
  box-shadow: 0 4px 10px color-mix(in srgb, var(--accent-primary) 40%, transparent);
}

.modal-btn--primary.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
  transition: transform 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-card {
  transform: scale(0.95) translateY(10px);
}

.modal-fade-leave-to .modal-card {
  transform: scale(0.95) translateY(10px);
}
</style>
