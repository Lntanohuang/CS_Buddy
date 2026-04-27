<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import type { LilSealAction } from '@/components/pet/types'
import ChatInput from '@/components/chat/ChatInput.vue'
import SmartBlackboard from '@/components/chat/SmartBlackboard.vue'
import LilSealPet from '@/components/pet/LilSealPet.vue'

const chatStore = useChatStore()

const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)
const isGenerating = computed(() => isStreaming.value || isAgentWorking.value)
const sealRewardAction = ref<LilSealAction | null>(null)
const sealActionKey = ref(0)
let rewardTimer: number | undefined

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

const sealSpeechText = computed(() => {
  if (chatStore.runtimeStatus !== 'talking') return ''
  return currentResponse.value?.content ?? ''
})

function handleSend(text: string) {
  if (isGenerating.value) return
  void chatStore.sendMessage(text)
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
      <aside class="tutor-zone" aria-label="小海豹导师">
        <div class="tutor-zone__header">
          <span class="tutor-zone__status" :class="`tutor-zone__status--${sealAction}`" />
          <span>小海豹导师</span>
        </div>
        <LilSealPet
          :action="sealAction"
          :action-key="sealActionKey"
          :speech-text="sealSpeechText"
          speech-placement="local"
          :position="{
            strategy: 'absolute',
            right: 'clamp(4px, 2vw, 28px)',
            bottom: 'clamp(4px, 4vh, 28px)',
            left: 'auto',
            scale: 0.92,
            zIndex: 4,
          }"
        />
      </aside>

      <main class="blackboard-zone">
        <SmartBlackboard
          :current-message="currentResponse"
          :current-question="currentQuestion"
          :is-thinking="isAgentWorking"
          :is-generating="isGenerating"
          :agent-steps="agentSteps"
          @feedback="handleFeedback"
        />
      </main>
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
  flex: 1;
  min-height: 0;
  height: 100%;
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  gap: 16px;
  padding: 18px 24px 20px;
  background: transparent;
  overflow: hidden;
}

.classroom-stage {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(220px, 28%) minmax(0, 1fr);
  gap: 22px;
}

.tutor-zone {
  position: relative;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.62);
  border-radius: 28px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.64), rgba(255, 255, 255, 0.36)),
    color-mix(in srgb, var(--accent-secondary-light) 22%, transparent);
  box-shadow: 0 18px 56px rgba(55, 77, 96, 0.1);
  backdrop-filter: blur(20px);
}

.tutor-zone__header {
  position: relative;
  z-index: 5;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 18px;
  padding: 8px 12px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.68);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 650;
  box-shadow: var(--shadow-sm);
}

.tutor-zone__status {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--status-success);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--status-success) 18%, transparent);
}

.tutor-zone__status--thinking {
  background: var(--accent-primary);
  box-shadow: 0 0 0 4px rgba(var(--accent-primary-rgb), 0.16);
}

.tutor-zone__status--talking {
  background: var(--accent-secondary);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent-secondary) 18%, transparent);
}

.blackboard-zone {
  min-width: 0;
  min-height: 0;
}

.classroom-input {
  min-width: 0;
}

.classroom-input :deep(.chat-input-wrapper) {
  padding: 0;
}

.classroom-input :deep(.chat-input-container) {
  width: min(100%, 980px);
}

@media (max-width: 1100px) {
  .classroom-stage {
    grid-template-columns: minmax(190px, 25%) minmax(0, 1fr);
    gap: 16px;
  }
}

@media (max-width: 820px) {
  .chat-view {
    padding: 14px;
  }

  .classroom-stage {
    grid-template-columns: 1fr;
    grid-template-rows: 170px minmax(0, 1fr);
  }

  .tutor-zone__header {
    margin: 12px;
  }
}

@media (max-width: 560px) {
  .classroom-stage {
    grid-template-rows: 138px minmax(0, 1fr);
  }
}
</style>
