<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useNotificationStore } from '@/stores/notification'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import RecommendCard from '@/components/notification/RecommendCard.vue'

const chatStore = useChatStore()
const notificationStore = useNotificationStore()

const showRecommend = shallowRef(true)
const recommendation = computed(() => notificationStore.todayRecommendation)
const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)

function handleStartRecommend() {
  if (recommendation.value) {
    void chatStore.sendMessage(`帮我学习${recommendation.value.title}`)
    showRecommend.value = false
  }
}

function handleDismissRecommend() {
  showRecommend.value = false
}

function handleSend(text: string) {
  void chatStore.sendMessage(text)
}
</script>

<template>
  <div class="chat-view">
    <RecommendCard
      v-if="showRecommend && recommendation"
      :title="recommendation.title"
      :reason="recommendation.reason"
      :est-minutes="recommendation.est_minutes"
      class="chat-recommend"
      @start="handleStartRecommend"
      @dismiss="handleDismissRecommend"
    />

    <div class="chat-main">
      <ChatMessageList
        :messages="activeMessages"
        :is-streaming="isStreaming"
        :agent-steps="agentSteps"
        :is-agent-working="isAgentWorking"
      />
      <ChatInput :disabled="isStreaming" @send="handleSend" />
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100%;
  background: var(--bg-primary);
}

.chat-main {
  display: flex;
  flex-direction: column;
  min-height: calc(100dvh - 132px);
  overflow: hidden;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(55, 53, 47, 0.06);
}

.chat-recommend {
  flex-shrink: 0;
}

@media (max-width: 720px) {
  .chat-main {
    min-height: calc(100dvh - 118px);
    border-radius: 20px;
  }
}
</style>
