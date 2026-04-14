import { ref, shallowRef, computed } from 'vue'
import { defineStore } from 'pinia'
import type { ChatSession, ChatMessage } from '@/types'
import { mockSessions, mockMessages, mockStreamReply } from '@/mock/data'

export const useChatStore = defineStore('chat', () => {
  const isValidSession = (session: unknown): session is ChatSession => {
    if (!session || typeof session !== 'object') return false
    const item = session as Partial<ChatSession>
    return (
      typeof item.session_id === 'string' &&
      item.session_id.length > 0 &&
      typeof item.title === 'string' &&
      typeof item.status === 'string' &&
      (item.session_type === 'NORMAL' || item.session_type === 'WELCOME') &&
      typeof item.message_count === 'number' &&
      typeof item.created_at === 'string' &&
      typeof item.updated_at === 'string'
    )
  }

  const isValidMessage = (message: unknown): message is ChatMessage => {
    if (!message || typeof message !== 'object') return false
    const item = message as Partial<ChatMessage>
    return (
      typeof item.message_id === 'string' &&
      item.message_id.length > 0 &&
      typeof item.session_id === 'string' &&
      item.session_id.length > 0 &&
      (item.role === 'USER' || item.role === 'ASSISTANT') &&
      typeof item.content === 'string' &&
      typeof item.created_at === 'string'
    )
  }

  const now = new Date().toISOString()
  const validSessions = mockSessions.filter(isValidSession)
  const validMessages = mockMessages.filter(isValidMessage)

  const seededSessions: ChatSession[] = validSessions.length > 0
    ? validSessions.map((session) => ({ ...session }))
    : [{
        session_id: `sess_bootstrap_${Date.now()}`,
        title: '新对话',
        status: 'ACTIVE',
        session_type: 'NORMAL',
        message_count: 0,
        created_at: now,
        updated_at: now,
      }]

  const seededMessagesBySession = seededSessions.reduce<Record<string, ChatMessage[]>>(
    (acc, session) => {
      acc[session.session_id] = validMessages
        .filter((msg) => msg.session_id === session.session_id)
        .map((msg) => ({ ...msg }))
      return acc
    },
    {},
  )

  const sessions = ref<ChatSession[]>(seededSessions)
  const activeSessionId = shallowRef<string>(seededSessions[0].session_id)
  const messagesBySession = ref<Record<string, ChatMessage[]>>(seededMessagesBySession)
  const isStreaming = shallowRef(false)

  const activeSession = computed(() =>
    sessions.value.find((s) => s.session_id === activeSessionId.value)
  )

  const activeMessages = computed(
    () => messagesBySession.value[activeSessionId.value] ?? []
  )

  function selectSession(id: string) {
    if (!messagesBySession.value[id]) return
    activeSessionId.value = id
  }

  function createSession() {
    const id = `sess_${Date.now()}`
    const session: ChatSession = {
      session_id: id,
      title: '新对话',
      status: 'ACTIVE',
      session_type: 'NORMAL',
      message_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    sessions.value.unshift(session)
    messagesBySession.value[id] = []
    activeSessionId.value = id
  }

  async function sendMessage(content: string) {
    if (!activeSessionId.value) {
      createSession()
    }
    const sid = activeSessionId.value
    if (!sid) return

    const userMsg: ChatMessage = {
      message_id: `msg_${Date.now()}`,
      session_id: sid,
      role: 'USER',
      content,
      created_at: new Date().toISOString(),
    }

    if (!messagesBySession.value[sid]) {
      messagesBySession.value[sid] = []
    }
    messagesBySession.value[sid].push(userMsg)

    // Update session title from first message
    const session = sessions.value.find((s) => s.session_id === sid)
    if (session && session.message_count === 0) {
      session.title = content.slice(0, 20) + (content.length > 20 ? '...' : '')
    }
    if (session) {
      session.message_count += 1
      session.updated_at = new Date().toISOString()
    }

    // Simulate streaming reply
    const assistantMsg: ChatMessage = {
      message_id: `msg_${Date.now() + 1}`,
      session_id: sid,
      role: 'ASSISTANT',
      content: '',
      intent: 'learn',
      metadata: {
        type: 'resource_card',
        title: '二叉树',
        difficulty: 'INTERMEDIATE',
        est_minutes: 15,
        knowledge_point: 'binary_tree',
      },
      created_at: new Date().toISOString(),
    }
    messagesBySession.value[sid].push(assistantMsg)
    isStreaming.value = true

    const chars = mockStreamReply.split('')
    for (let i = 0; i < chars.length; i++) {
      assistantMsg.content += chars[i]
      // Yield to the event loop periodically for smooth rendering
      if (i % 3 === 0) {
        await new Promise((r) => setTimeout(r, 15))
      }
    }

    isStreaming.value = false
    if (session) {
      session.message_count += 1
    }
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    activeMessages,
    isStreaming,
    selectSession,
    createSession,
    sendMessage,
  }
})
