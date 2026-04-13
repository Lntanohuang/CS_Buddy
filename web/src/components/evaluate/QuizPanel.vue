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

const typeLabel: Record<string, string> = {
  MINI_QUIZ: '随堂小测',
  STAGE_TEST: '阶段测试',
  USER_REQUEST: '主动评估',
}
</script>

<template>
  <div class="quiz-panel">
    <div class="panel-header">
      <div class="header-left">
        <h2 class="kp-name">{{ evaluation.knowledge_point }}</h2>
        <span class="question-count">共 {{ evaluation.question_count }} 题</span>
        <el-tag size="small">{{ typeLabel[evaluation.type] ?? evaluation.type }}</el-tag>
      </div>
      <div class="progress-info">
        已答 {{ answeredCount }} / {{ evaluation.question_count }}
      </div>
    </div>

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

    <div v-if="!isAnalyzed" class="panel-footer">
      <el-button
        type="primary"
        size="large"
        :disabled="!allAnswered"
        @click="emit('submit')"
      >
        提交答案
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.quiz-panel {
  max-width: 800px;
  margin: 0 auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.kp-name {
  margin: 0;
  font-size: 20px;
}

.question-count {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.progress-info {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-footer {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
</style>
