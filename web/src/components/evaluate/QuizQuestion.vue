<script setup lang="ts">
import { ref, watch } from 'vue'
import type { EvalQuestion } from '@/types'

const props = defineProps<{
  question: EvalQuestion
  index: number
  disabled: boolean
}>()

const emit = defineEmits<{
  answer: [payload: { questionId: string; answer: string }]
}>()

const userAnswer = ref(props.question.user_answer ?? '')

watch(
  () => props.question.user_answer,
  (val) => {
    if (val !== undefined) userAnswer.value = val
  },
)

function onAnswerChange(val: string) {
  userAnswer.value = val
  emit('answer', { questionId: props.question.question_id, answer: val })
}
</script>

<template>
  <div
    class="quiz-question"
    :class="{
      'is-correct': disabled && question.is_correct === true,
      'is-wrong': disabled && question.is_correct === false,
    }"
  >
    <!-- Header row -->
    <div class="question-header">
      <div class="header-left">
        <span class="question-badge">{{ index + 1 }}</span>
        <span class="type-pill">
          {{ question.type === 'SINGLE_CHOICE' ? '选择题' : question.type === 'FILL_BLANK' ? '填空题' : '编程题' }}
        </span>
      </div>
      <!-- Result badge in header -->
      <span v-if="disabled && question.is_correct === true" class="result-badge result-badge--correct">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        正确
      </span>
      <span v-else-if="disabled && question.is_correct === false" class="result-badge result-badge--wrong">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        错误
      </span>
    </div>

    <!-- Question content -->
    <div class="question-content">{{ question.content }}</div>

    <!-- Single Choice options -->
    <div v-if="question.type === 'SINGLE_CHOICE'" class="options-list">
      <label
        v-for="opt in question.options"
        :key="opt.key"
        class="option-card"
        :class="{
          'is-selected': userAnswer === opt.key,
          'is-disabled': disabled,
          'is-correct-answer': disabled && question.correct_answer === opt.key,
          'is-wrong-answer': disabled && userAnswer === opt.key && question.is_correct === false,
        }"
      >
        <input
          type="radio"
          :name="`q-${question.question_id}`"
          :value="opt.key"
          :checked="userAnswer === opt.key"
          :disabled="disabled"
          class="option-radio"
          @change="onAnswerChange(opt.key)"
        />
        <span class="option-key">{{ opt.key }}</span>
        <span class="option-text">{{ opt.value }}</span>
        <!-- Correct/wrong icon -->
        <svg v-if="disabled && question.correct_answer === opt.key" class="option-icon option-icon--correct" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--status-success)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        <svg v-else-if="disabled && userAnswer === opt.key && question.is_correct === false" class="option-icon option-icon--wrong" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--status-error)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </label>
    </div>

    <!-- Fill Blank input -->
    <div v-else-if="question.type === 'FILL_BLANK'" class="fill-blank-wrapper">
      <input
        type="text"
        class="fill-input"
        :class="{
          'fill-input--correct': disabled && question.is_correct === true,
          'fill-input--wrong': disabled && question.is_correct === false,
        }"
        :value="userAnswer"
        :disabled="disabled"
        placeholder="输入你的答案"
        @input="onAnswerChange(($event.target as HTMLInputElement).value)"
      />
      <div v-if="disabled && question.is_correct === false" class="correct-answer-line">
        正确答案：<strong>{{ question.correct_answer }}</strong>
      </div>
    </div>

    <!-- Explanation (shown after submission for wrong answers) -->
    <Transition name="fade-slide">
      <div v-if="disabled && question.is_correct === false && question.explanation" class="explanation-box">
        <div class="explanation-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
        <div class="explanation-content">
          <span class="explanation-label">解析</span>
          <p class="explanation-text">{{ question.explanation }}</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.quiz-question {
  padding: 24px;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.quiz-question.is-correct {
  border-color: var(--status-success);
  box-shadow: 0 1px 3px color-mix(in srgb, var(--status-success) 10%, transparent);
}

.quiz-question.is-wrong {
  border-color: var(--status-error);
  box-shadow: 0 1px 3px color-mix(in srgb, var(--status-error) 10%, transparent);
}

/* Header */
.question-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.question-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: var(--bg-card);
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.type-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 20px;
  background: var(--accent-primary-light);
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.result-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.result-badge--correct {
  background: var(--accent-primary-light);
  color: var(--status-success);
}

.result-badge--wrong {
  background: var(--status-error-light);
  color: var(--status-error);
}

/* Question content */
.question-content {
  font-size: 18px;
  line-height: 1.7;
  color: var(--text-primary);
  margin-bottom: 20px;
  white-space: pre-wrap;
  font-weight: 500;
}

/* Options */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.option-card:hover:not(.is-disabled) {
  border-color: var(--accent-primary-light);
  background: var(--accent-secondary-light);
}

.option-card.is-selected:not(.is-disabled) {
  border-color: var(--accent-primary);
  background: var(--accent-primary-light);
}

.option-card.is-disabled {
  cursor: default;
}

.option-card.is-correct-answer {
  border-color: var(--status-success);
  background: var(--accent-primary-light);
}

.option-card.is-wrong-answer {
  border-color: var(--status-error);
  background: var(--status-error-light);
}

.option-radio {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.option-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 2px solid var(--border-strong);
  color: var(--text-tertiary);
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.option-card.is-selected .option-key {
  border-color: var(--accent-primary);
  background: var(--accent-primary);
  color: var(--bg-card);
}

.option-card.is-correct-answer .option-key {
  border-color: var(--status-success);
  background: var(--status-success);
  color: var(--bg-card);
}

.option-card.is-wrong-answer .option-key {
  border-color: var(--status-error);
  background: var(--status-error);
  color: var(--bg-card);
}

.option-text {
  flex: 1;
  font-size: 15px;
  color: var(--text-primary);
  line-height: 1.5;
}

.option-icon {
  flex-shrink: 0;
  margin-left: auto;
}

/* Fill blank */
.fill-blank-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fill-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  color: var(--text-primary);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  background: var(--bg-card);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}

.fill-input::placeholder {
  color: var(--text-secondary);
}

.fill-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent-primary) 10%, transparent);
}

.fill-input:disabled {
  background: var(--bg-primary);
  cursor: default;
}

.fill-input--correct {
  border-color: var(--status-success);
  background: var(--accent-primary-light);
}

.fill-input--wrong {
  border-color: var(--status-error);
  background: var(--status-error-light);
}

.correct-answer-line {
  font-size: 14px;
  color: var(--text-tertiary);
  padding-left: 4px;
}

.correct-answer-line strong {
  color: var(--status-success);
  font-weight: 600;
}

/* Explanation */
.explanation-box {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  padding: 14px 16px;
  background: var(--bg-primary);
  border-left: 3px solid var(--accent-primary);
  border-radius: 0 8px 8px 0;
}

.explanation-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.explanation-content {
  flex: 1;
}

.explanation-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-primary);
  display: block;
  margin-bottom: 4px;
}

.explanation-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-tertiary);
  white-space: pre-wrap;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
