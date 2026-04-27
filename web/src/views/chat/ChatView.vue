<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useUserStore } from '@/stores/user'
import type { LilSealAction } from '@/components/pet/types'
import ChatInput from '@/components/chat/ChatInput.vue'
import SmartBlackboard from '@/components/chat/SmartBlackboard.vue'
import LilSealPet from '@/components/pet/LilSealPet.vue'

const chatStore = useChatStore()
const userStore = useUserStore()

const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)
const isGenerating = computed(() => isStreaming.value || isAgentWorking.value)
const sealRewardAction = ref<LilSealAction | null>(null)
const sealActionKey = ref(0)
let rewardTimer: number | undefined
const quickPrompts = ['解释这段代码', '出一道类似题', '我没听懂', '帮我总结']

const knowledgeLabels: Record<string, string> = {
  array: '数组基础',
  linked_list: '链表',
  stack: '栈与队列',
  sorting: '排序算法',
  quick_sort: '快速排序',
  binary_tree: '二叉树 / 前序遍历',
  graph: '图论基础',
  hash_table: '哈希表',
}

const recommendationLabels: Record<string, string> = {
  sorting: '排序算法稳定性专项',
  quick_sort: '快速排序分区练习',
  binary_tree: '二叉树遍历专项',
  graph: '图遍历 BFS / DFS 练习',
  hash_table: '哈希冲突处理练习',
}

const sealAction = computed<LilSealAction>(() => {
  if (sealRewardAction.value) return sealRewardAction.value
  if (chatStore.runtimeStatus === 'thinking') return 'thinking'
  if (chatStore.runtimeStatus === 'talking') return 'talking'
  return 'idle'
})

const currentQuestion = computed(() => {
  return [...activeMessages.value].reverse().find((message) => message.role === 'USER')?.content ?? ''
})

const currentResponse = computed(() => {
  const latestMessage = activeMessages.value[activeMessages.value.length - 1]
  return latestMessage?.role === 'ASSISTANT' ? latestMessage : null
})

const currentKnowledgeKey = computed(() => {
  const value = currentResponse.value?.metadata?.knowledge_point
  if (typeof value === 'string') return value

  if (/快排|快速排序|排序/.test(currentQuestion.value)) return 'sorting'
  if (/树|二叉树|递归|遍历/.test(currentQuestion.value)) return 'binary_tree'
  if (/图|BFS|DFS/i.test(currentQuestion.value)) return 'graph'

  return 'binary_tree'
})

const currentKnowledgeLabel = computed(() => {
  return knowledgeLabels[currentKnowledgeKey.value] ?? currentKnowledgeKey.value
})

const currentLessonTitle = computed(() => {
  const title = currentResponse.value?.metadata?.title
  if (typeof title === 'string' && title.trim()) return title.trim()
  if (currentQuestion.value) return currentQuestion.value.slice(0, 24)
  return currentKnowledgeLabel.value
})

const currentMastery = computed(() => {
  const key = currentKnowledgeKey.value
  const normalizedKey = key === 'quick_sort' ? 'sorting' : key
  return Math.round((userStore.knowledgeMastery[normalizedKey] ?? 0.72) * 100)
})

const boardModeLabel = computed(() => {
  const content = currentResponse.value?.content ?? ''
  if (sealRewardAction.value === 'happy') return '鼓励中'
  if (sealRewardAction.value === 'starry') return '记录反馈'
  if (chatStore.runtimeStatus === 'thinking') return '思考中'
  if (/```(python|py|javascript|js|ts|java|cpp)/i.test(content)) return '写代码示例'
  if (/```mermaid/i.test(content)) return '画图讲解'
  if (/练习|题目|巩固/.test(content)) return '布置练习'
  if (chatStore.runtimeStatus === 'talking') return '板书中'
  return '待命'
})

const stateLabel = computed(() => {
  if (sealRewardAction.value === 'happy') return '收到正反馈'
  if (sealRewardAction.value === 'starry') return '记录你的反馈'
  if (chatStore.runtimeStatus === 'thinking') return '正在拆解问题'
  if (boardModeLabel.value === '写代码示例') return '正在写代码示例'
  if (boardModeLabel.value === '画图讲解') return '正在画图讲解'
  if (boardModeLabel.value === '布置练习') return '正在布置练习'
  if (chatStore.runtimeStatus === 'talking') return `正在讲解${currentKnowledgeLabel.value}`
  return '等待提问'
})

const currentRecommendation = computed(() => {
  return recommendationLabels[currentKnowledgeKey.value] ?? '基础概念巩固练习'
})

const sealSpeechText = computed(() => {
  return ''
})

const sealCoachLine = computed(() => {
  if (sealRewardAction.value === 'happy') return '做得很好，我们继续保持这个节奏。'
  if (sealRewardAction.value === 'starry') return '我记下来了，下一版讲解会更贴近你。'
  if (chatStore.runtimeStatus === 'thinking') return `我正在帮你拆解「${currentLessonTitle.value}」。`
  if (boardModeLabel.value === '写代码示例') return `我正在把「${currentKnowledgeLabel.value}」写成代码演示。`
  if (boardModeLabel.value === '画图讲解') return '我正在把结构画出来，方便你看清关系。'
  if (boardModeLabel.value === '布置练习') return '我给你准备一道随堂练习。'
  if (chatStore.runtimeStatus === 'talking') return `我正在讲解「${currentLessonTitle.value}」。`
  return '问我一个学习问题，我们马上开讲。'
})

function handleSend(text: string) {
  if (isGenerating.value) return
  void chatStore.sendMessage(text)
}

function handleQuickPrompt(prompt: string) {
  handleSend(prompt)
}

function handleFeedback(payload: { messageId: string; feedback: 'USEFUL' | 'NOT_USEFUL' }) {
  sealRewardAction.value = payload.feedback === 'USEFUL' ? 'happy' : 'starry'
  sealActionKey.value += 1

  if (rewardTimer !== undefined) {
    window.clearTimeout(rewardTimer)
  }

  rewardTimer = window.setTimeout(() => {
    sealRewardAction.value = null
    rewardTimer = undefined
  }, 1400)
}
</script>

<template>
  <div class="chat-view">
    <div class="classroom-stage">
      <main class="teaching-zone">
        <SmartBlackboard
          :current-message="currentResponse"
          :current-question="currentQuestion"
          :is-thinking="isAgentWorking"
          :is-generating="isGenerating"
          :agent-steps="agentSteps"
          @feedback="handleFeedback"
        />
      </main>

      <aside class="learning-status" aria-label="小海豹学习状态区">
        <section class="learning-status__seal">
          <div class="learning-status__speech">
            <span>小海豹：</span>
            <p>{{ sealCoachLine }}</p>
          </div>
          <LilSealPet
            :action="sealAction"
            :action-key="sealActionKey"
            :speech-text="sealSpeechText"
            speech-placement="local"
            :position="{
              strategy: 'absolute',
              right: '20px',
              bottom: '30px',
              left: 'auto',
              scale: 0.64,
              zIndex: 4,
            }"
          />
        </section>

        <section class="learning-status__info">
          <div class="learning-status__header">
            <span class="learning-status__dot" :class="`learning-status__dot--${sealAction}`" />
            <div>
              <h2>小海豹导师</h2>
              <p>{{ stateLabel }}</p>
            </div>
          </div>

          <dl class="learning-status__list">
            <div>
              <dt>正在讲解</dt>
              <dd>{{ currentLessonTitle }}</dd>
            </div>
            <div>
              <dt>当前状态</dt>
              <dd>{{ boardModeLabel }} / {{ stateLabel }}</dd>
            </div>
            <div>
              <dt>当前知识点</dt>
              <dd>{{ currentKnowledgeLabel }}</dd>
            </div>
            <div>
              <dt>掌握度</dt>
              <dd>
                <span>{{ currentMastery }}%</span>
                <span class="learning-status__bar" aria-hidden="true">
                  <span :style="{ width: `${currentMastery}%` }" />
                </span>
              </dd>
            </div>
            <div>
              <dt>今日学习</dt>
              <dd>35 分钟</dd>
            </div>
            <div>
              <dt>推荐练习</dt>
              <dd>{{ currentRecommendation }}</dd>
            </div>
          </dl>
        </section>

        <section class="learning-status__quick" aria-label="快捷提问">
          <p>快捷提问</p>
          <div class="learning-status__quick-list">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              type="button"
              :disabled="isGenerating"
              @click="handleQuickPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </section>
      </aside>
    </div>

    <footer class="classroom-input">
      <ChatInput
        :disabled="isGenerating"
        @send="handleSend"
      />
    </footer>
  </div>
</template>

<style scoped>
.chat-view {
  --classroom-pad-x: 24px;
  --learning-status-width: 320px;
  --classroom-gap: 16px;

  flex: 1;
  position: relative;
  min-height: 0;
  height: 100%;
  display: grid;
  grid-template-columns: minmax(0, 1fr) var(--learning-status-width);
  grid-template-rows: minmax(0, 1fr);
  gap: var(--classroom-gap);
  padding: 18px var(--classroom-pad-x) 20px;
  background: transparent;
  overflow: hidden;
}

.classroom-stage {
  display: contents;
}

.teaching-zone,
.learning-status {
  min-width: 0;
  min-height: 0;
}

.teaching-zone {
  grid-column: 1;
  grid-row: 1;
}

.learning-status {
  grid-column: 2;
  grid-row: 1;
  position: relative;
  display: grid;
  grid-template-rows: 260px minmax(0, 1fr) auto;
  gap: 0;
  padding-left: 22px;
  border-left: 1px solid rgba(29, 29, 31, 0.1);
}

.learning-status::before {
  display: none;
}

.learning-status::after {
  display: none;
}

.learning-status__seal,
.learning-status__info {
  min-width: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.learning-status__seal {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid rgba(29, 29, 31, 0.1);
}

.learning-status__seal :deep(.lil-seal-pet) {
  position: absolute;
  inset: 0;
}

.learning-status__speech {
  position: relative;
  z-index: 6;
  max-width: 100%;
  margin: 0;
  padding: 2px 0 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.learning-status__speech::after {
  display: none;
}

.learning-status__speech span {
  display: block;
  margin-bottom: 4px;
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 800;
}

.learning-status__speech p {
  margin: 0;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 650;
  line-height: 1.45;
}

.learning-status__info {
  overflow: visible;
  padding: 18px 0 0;
}

.learning-status__header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding-bottom: 6px;
  border-bottom: 0;
}

.learning-status__header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 760;
}

.learning-status__header p {
  margin: 3px 0 0;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.learning-status__dot {
  position: relative;
  z-index: 1;
  flex: 0 0 10px;
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border-radius: 50%;
  background: var(--status-success);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--status-success) 18%, transparent);
}

.learning-status__dot--thinking {
  background: var(--accent-primary);
  box-shadow: 0 0 0 4px rgba(var(--accent-primary-rgb), 0.16);
}

.learning-status__dot--talking {
  background: var(--accent-secondary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-secondary) 18%, transparent);
}

.learning-status__list {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin: 14px 0 0;
}

.learning-status__list div {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  gap: 10px;
  padding: 0;
  border-top: 0;
}

.learning-status__list dt {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.learning-status__list dd {
  min-width: 0;
  margin: 0;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.45;
}

.learning-status__bar {
  display: block;
  height: 7px;
  margin-top: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(var(--accent-primary-rgb), 0.12);
}

.learning-status__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
}

.learning-status__quick {
  align-self: end;
  padding-top: 14px;
  border-top: 1px solid rgba(29, 29, 31, 0.1);
}

.learning-status__quick p {
  margin: 0 0 6px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 700;
}

.learning-status__quick-list {
  display: grid;
  gap: 4px;
}

.learning-status__quick button {
  width: 100%;
  min-height: 34px;
  padding: 8px 0;
  border: 0;
  background: transparent;
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 650;
  text-align: left;
  cursor: pointer;
  transition: color 0.18s ease, opacity 0.18s ease;
}

.learning-status__quick button:hover:not(:disabled) {
  color: var(--accent-primary);
}

.learning-status__quick button:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

.classroom-input {
  position: absolute;
  left: var(--classroom-pad-x);
  right: calc(var(--classroom-pad-x) + var(--learning-status-width) + var(--classroom-gap));
  bottom: 20px;
  z-index: 10;
  min-width: 0;
  padding-top: 0;
  border-top: 0;
  background: transparent;
  pointer-events: none;
}

.classroom-input :deep(.chat-input-wrapper) {
  width: 100%;
  pointer-events: auto;
}

.classroom-input :deep(.chat-input-container) {
  width: 100%;
}

@media (max-width: 1180px) {
  .chat-view {
    --learning-status-width: 300px;
  }
}

@media (max-width: 920px) {
  .chat-view {
    --classroom-pad-x: 14px;
    grid-template-columns: 1fr;
    grid-template-rows: minmax(0, 1fr) auto;
    padding: 14px;
  }

  .teaching-zone {
    grid-column: 1;
    grid-row: 1;
  }

  .learning-status {
    grid-column: 1;
    grid-row: 2;
    grid-template-columns: minmax(180px, 240px) minmax(0, 1fr) minmax(160px, 0.8fr);
    grid-template-rows: 180px;
    padding-left: 0;
    padding-top: 14px;
    border-top: 1px solid rgba(29, 29, 31, 0.1);
    border-left: 0;
  }

  .classroom-input {
    left: 14px;
    right: 14px;
    bottom: 14px;
  }

  .learning-status::before,
  .learning-status::after {
    display: none;
  }
}

@media (max-width: 640px) {
  .learning-status {
    grid-template-columns: 1fr;
    grid-template-rows: 150px auto auto;
  }

  .learning-status__list div {
    grid-template-columns: 76px minmax(0, 1fr);
  }
}
</style>
