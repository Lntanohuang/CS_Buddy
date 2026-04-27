<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import type { LilSealAction } from '@/components/pet/types'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import LilSealPet from '@/components/pet/LilSealPet.vue'

const chatStore = useChatStore()

const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)
const sealRewardAction = ref<LilSealAction | null>(null)
const sealActionKey = ref(0)
let rewardTimer: number | undefined

const sealAction = computed<LilSealAction>(() => {
  if (sealRewardAction.value) return sealRewardAction.value
  if (chatStore.runtimeStatus === 'thinking') return 'thinking'
  if (chatStore.runtimeStatus === 'talking') return 'talking'
  return 'idle'
})

const sealSpeechText = computed(() => {
  if (chatStore.runtimeStatus !== 'talking') return ''

  const lastAssistantMessage = [...activeMessages.value]
    .reverse()
    .find((message) => message.role === 'ASSISTANT')

  return lastAssistantMessage?.content ?? ''
})

function handleSend(text: string) {
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
    <div class="chat-main">
      <ChatMessageList
        :messages="activeMessages"
        :is-streaming="isStreaming"
        :agent-steps="agentSteps"
        :is-agent-working="isAgentWorking"
        @feedback="handleFeedback"
      />
      <ChatInput :disabled="isStreaming" @send="handleSend" />
    </div>

    <LilSealPet
      :action="sealAction"
      :action-key="sealActionKey"
      :speech-text="sealSpeechText"
    />
  </div>
</template>

<style scoped>
.chat-view {
  flex: 1;
  min-height: 0;
  height: 100%;
  display: flex;
  background: transparent;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: transparent;
  box-shadow: none;
}
</style>
