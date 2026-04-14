<script setup lang="ts">
import { computed } from 'vue'
import type { Evaluation } from '@/types'
import QuizQuestion from './QuizQuestion.vue'

const props = defineProps<{
  evaluation: Evaluation
}>()

const emit = defineEmits<{
  submit: []
  answer: [payload: { questionId: string; answer: string }]
}>()

const answeredCount = computed(() =>
  props.evaluation.questions.filter((q) => q.user_answer && q.user_answer.trim() !== '').length,
)

const allAnswered = computed(() => answeredCount.value === props.evaluation.question_count)

const isAnalyzed = computed(() => props.evaluation.status === 'ANALYZED')

const progressPercent = computed(() =>
  props.evaluation.question_count > 0
    ? Math.round((answeredCount.value / props.evaluation.question_count) * 100)
    : 0,
)

const typeLabel: Record<string, string> = {
  MINI_QUIZ: '随堂小测',
  STAGE_TEST: '阶段测试',
  USER_REQUEST: '主动评估',
}
</script>

<template>
  <div class="quiz-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-top">
        <h2 class="kp-name">{{ evaluation.knowledge_point }}</h2>
        <span class="type-pill">{{ typeLabel[evaluation.type] ?? evaluation.type }}</span>
      </div>
      <div class="header-meta">
        <span class="question-count">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          共 {{ evaluation.question_count }} 题
        </span>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="progress-section">
      <div class="progress-text">
        <span>已完成 <strong>{{ answeredCount }}/{{ evaluation.question_count }}</strong> 题</span>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <div class="progress-track">
        <div
          class="progress-fill"
          :style="{ width: progressPercent + '%' }"
        />
      </div>
    </div>

    <!-- Questions -->
    <div class="questions-list">
      <QuizQuestion
        v-for="(q, idx) in evaluation.questions"
        :key="q.question_id"
        :question="q"
        :index="idx"
        :disabled="isAnalyzed"
        @answer="emit('answer', $event)"
      />
    </div>

    <!-- Submit -->
    <div v-if="!isAnalyzed" class="panel-footer">
      <button
        class="submit-btn"
        :class="{ 'is-disabled': !allAnswered }"
        :disabled="!allAnswered"
        @click="emit('submit')"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/></svg>
        提交答案
      </button>
      <p v-if="!allAnswered" class="submit-hint">请回答所有题目后提交</p>
    </div>
  </div>
</template>

<style scoped>
.quiz-panel {
  max-width: 720px;
  margin: 0 auto;
}

/* Header */
.panel-header {
  margin-bottom: 20px;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.kp-name {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.type-pill {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  border-radius: 20px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.question-count {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-tertiary);
}

/* Progress */
.progress-section {
  margin-bottom: 28px;
  padding: 16px 20px;
  background: var(--bg-card);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.progress-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  color: var(--text-tertiary);
}

.progress-text strong {
  color: var(--text-primary);
}

.progress-percent {
  font-weight: 600;
  color: var(--accent-primary);
}

.progress-track {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--border);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  transition: width 0.4s ease;
}

/* Questions */
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Footer */
.panel-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 36px;
  padding-top: 28px;
  border-top: 1px solid var(--border);
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 48px;
  font-size: 16px;
  font-weight: 600;
  color: var(--bg-card);
  background: var(--accent-primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent-primary) 30%, transparent);
}

.submit-btn:hover:not(.is-disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 14px color-mix(in srgb, var(--accent-primary) 40%, transparent);
}

.submit-btn:active:not(.is-disabled) {
  transform: translateY(0);
}

.submit-btn.is-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.submit-hint {
  margin-top: 10px;
  font-size: 13px;
  color: var(--text-secondary);
}
</style>
