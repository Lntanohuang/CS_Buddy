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
  <div class="quiz-question">
    <div class="question-header">
      <span class="question-index">第 {{ index + 1 }} 题</span>
      <el-tag size="small" type="info">
        {{ question.type === 'SINGLE_CHOICE' ? '单选' : question.type === 'FILL_BLANK' ? '填空' : '编程' }}
      </el-tag>
    </div>

    <div class="question-content">{{ question.content }}</div>

    <!-- Single Choice -->
    <el-radio-group
      v-if="question.type === 'SINGLE_CHOICE'"
      :model-value="userAnswer"
      :disabled="disabled"
      class="options-group"
      @update:model-value="onAnswerChange($event as string)"
    >
      <el-radio
        v-for="opt in question.options"
        :key="opt.key"
        :value="opt.key"
        class="option-item"
      >
        {{ opt.key }}. {{ opt.value }}
      </el-radio>
    </el-radio-group>

    <!-- Fill Blank -->
    <el-input
      v-else-if="question.type === 'FILL_BLANK'"
      :model-value="userAnswer"
      :disabled="disabled"
      placeholder="请输入答案"
      @update:model-value="onAnswerChange($event as string)"
    />

    <!-- Result indicator (shown after submission) -->
    <div v-if="disabled && question.is_correct !== undefined" class="result-indicator">
      <div v-if="question.is_correct" class="result-correct">
        <el-icon color="#67c23a"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm-55.808 536.384-99.52-99.584a38.4 38.4 0 1 0-54.336 54.336l126.72 126.72a38.272 38.272 0 0 0 54.336 0l262.4-262.464a38.4 38.4 0 1 0-54.336-54.336L456.192 600.384z"/></svg></el-icon>
        <span>正确</span>
      </div>
      <div v-else class="result-wrong">
        <el-icon color="#f56c6c"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm0 393.664L407.936 353.6a38.4 38.4 0 1 0-54.336 54.336L457.664 512 353.6 616.064a38.4 38.4 0 1 0 54.336 54.336L512 566.336 616.064 670.4a38.4 38.4 0 1 0 54.336-54.336L566.336 512 670.4 407.936a38.4 38.4 0 1 0-54.336-54.336L512 457.664z"/></svg></el-icon>
        <span>错误</span>
        <span class="correct-answer">正确答案：{{ question.correct_answer }}</span>
        <div v-if="question.explanation" class="explanation">
          {{ question.explanation }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.quiz-question {
  padding: 20px;
  border: 1px solid var(--el-border-color-lighter, #e4e7ed);
  border-radius: 8px;
  background: #fff;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.question-index {
  font-weight: 600;
  font-size: 15px;
  color: var(--el-text-color-primary);
}

.question-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 16px;
  white-space: pre-wrap;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option-item {
  height: auto;
  line-height: 1.5;
}

.result-indicator {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--el-border-color-lighter, #e4e7ed);
}

.result-correct {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #67c23a;
  font-weight: 600;
}

.result-wrong {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  font-weight: 600;
}

.correct-answer {
  margin-left: 8px;
  color: var(--el-text-color-regular);
  font-weight: 400;
}

.explanation {
  width: 100%;
  margin-top: 8px;
  padding: 10px 12px;
  background: #fef0f0;
  border-radius: 4px;
  color: var(--el-text-color-regular);
  font-weight: 400;
  font-size: 13px;
  line-height: 1.5;
}
</style>
