<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessageList from '@/components/chat/ChatMessageList.vue'
import ChatInput from '@/components/chat/ChatInput.vue'

const chatStore = useChatStore()

const activeMessages = computed(() => chatStore.activeMessages)
const isStreaming = computed(() => chatStore.isStreaming)
const agentSteps = computed(() => chatStore.agentSteps)
const isAgentWorking = computed(() => chatStore.isAgentWorking)

function handleSend(text: string) {
  void chatStore.sendMessage(text)
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
      />
      <ChatInput :disabled="isStreaming" @send="handleSend" />
    </div>
  </div>
</template>

<style scoped>
.chat-view {
  flex: 1;
  min-height: 0;
  height: 100%;
  display: flex;
  background: var(--bg-primary);
  overflow: hidden;
}

.chat-main {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(55, 53, 47, 0.06);
}

@media (max-width: 720px) {
  .chat-main {
    border-radius: 20px;
  }
}
</style>
