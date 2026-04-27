import { ref, shallowRef, computed, triggerRef } from 'vue'
import { defineStore } from 'pinia'
import type { ChatSession, ChatMessage, AgentStep } from '@/types'
import { mockSessions, mockMessages, mockAgentSteps } from '@/mock/data'
import { usePathStore } from './path'
import { useNotificationStore } from './notification'
import { useProfileStore } from './profile'
import { streamChat } from '@/api/chat'

const STORAGE_SESSIONS_KEY = 'csbuddy_sessions'
const STORAGE_MESSAGES_KEY = 'csbuddy_messages'

function loadFromStorage<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function saveToStorage(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // ignore quota errors
  }
}

export type ChatRuntimeStatus = 'idle' | 'thinking' | 'talking'

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

  // Load from localStorage first, fallback to mock data
  const storedSessions = loadFromStorage<ChatSession[]>(STORAGE_SESSIONS_KEY)
  const storedMessages = loadFromStorage<Record<string, ChatMessage[]>>(STORAGE_MESSAGES_KEY)

  const now = new Date().toISOString()

  let seededSessions: ChatSession[]
  let seededMessagesBySession: Record<string, ChatMessage[]>

  if (storedSessions && storedSessions.length > 0) {
    seededSessions = storedSessions.filter(isValidSession)
    seededMessagesBySession = storedMessages ?? {}
  } else {
    const validSessions = mockSessions.filter(isValidSession)
    const validMessages = mockMessages.filter(isValidMessage)

    seededSessions = validSessions.length > 0
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

    seededMessagesBySession = seededSessions.reduce<Record<string, ChatMessage[]>>(
      (acc, session) => {
        acc[session.session_id] = validMessages
          .filter((msg) => msg.session_id === session.session_id)
          .map((msg) => ({ ...msg }))
        return acc
      },
      {},
    )
  }

  const sessions = ref<ChatSession[]>(seededSessions)
  const activeSessionId = shallowRef<string>(seededSessions[0].session_id)
  const messagesBySession = ref<Record<string, ChatMessage[]>>(seededMessagesBySession)
  const isStreaming = shallowRef(false)
  const agentSteps = ref<AgentStep[]>([])
  const isAgentWorking = shallowRef(false)
  let sendCounter = 0

  function persist() {
    saveToStorage(STORAGE_SESSIONS_KEY, sessions.value)
    saveToStorage(STORAGE_MESSAGES_KEY, messagesBySession.value)
  }

  const activeSession = computed(() =>
    sessions.value.find((s) => s.session_id === activeSessionId.value)
  )

  const activeMessages = computed(
    () => messagesBySession.value[activeSessionId.value] ?? []
  )

  const runtimeStatus = computed<ChatRuntimeStatus>(() => {
    if (isAgentWorking.value) return 'thinking'
    if (isStreaming.value) return 'talking'
    return 'idle'
  })

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
    persist()
  }

  async function sendMessage(content: string) {
    if (!activeSessionId.value) {
      createSession()
    }
    const sid = activeSessionId.value
    if (!sid) return

    sendCounter++
    const isFirstMessage = sendCounter === 1

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

    // --- Multi-agent simulation on first message ---
    if (isFirstMessage) {
      isAgentWorking.value = true
      agentSteps.value = mockAgentSteps.map((s) => ({ ...s, status: 'pending' }))

      for (let i = 0; i < agentSteps.value.length; i++) {
        agentSteps.value[i].status = 'working'
        await new Promise((r) => setTimeout(r, 800 + Math.random() * 400))
        agentSteps.value[i].status = 'done'
      }
      isAgentWorking.value = false
    }

    const assistantMsg: ChatMessage = {
      message_id: `msg_${Date.now() + 1}`,
      session_id: sid,
      role: 'ASSISTANT',
      content: '',
      created_at: new Date().toISOString(),
    }
    const msgArray = messagesBySession.value[sid]
    msgArray.push(assistantMsg)
    const assistantIdx = msgArray.length - 1
    isStreaming.value = true

    try {
      await streamChat(
        sid,
        content,
        (token) => {
          msgArray[assistantIdx] = {
            ...msgArray[assistantIdx],
            content: msgArray[assistantIdx].content + token,
          }
          triggerRef(messagesBySession)
        },
        () => {
          isStreaming.value = false
          if (session) session.message_count += 1
          persist()
        },
        (error) => {
          msgArray[assistantIdx] = {
            ...msgArray[assistantIdx],
            content: msgArray[assistantIdx].content + `\n\n⚠️ ${error}`,
          }
          triggerRef(messagesBySession)
          isStreaming.value = false
          persist()
        },
      )
    } catch {
      msgArray[assistantIdx] = {
        ...msgArray[assistantIdx],
        content: msgArray[assistantIdx].content + '\n\n⚠️ 网络连接失败，请检查后端服务是否启动',
      }
      triggerRef(messagesBySession)
      isStreaming.value = false
      persist()
    }

    // --- Cross-store side effects ---
    if (isFirstMessage) {
      const pathStore = usePathStore()
      pathStore.addNodes([
        {
          node_id: `node_chat_${Date.now()}`,
          title: '二叉树遍历练习',
          knowledge_point: 'binary_tree',
          order: 11,
          status: 'PENDING',
          difficulty: 'INTERMEDIATE',
          est_minutes: 60,
          prerequisites: ['node_006'],
          is_supplement: false,
        },
      ])

      const notificationStore = useNotificationStore()
      notificationStore.addNotification({
        type: 'DAILY_RECOMMEND',
        title: '学习路径已更新',
        content: '根据你的最新对话，已新增「二叉树遍历练习」节点',
        action_url: '/app/path',
      })
    }

    const profileStore = useProfileStore()
    profileStore.updateMastery('binary_tree', Math.min(1, (profileStore.profile.knowledge_mastery['binary_tree'] ?? 0) + 0.05))
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    activeMessages,
    runtimeStatus,
    isStreaming,
    agentSteps,
    isAgentWorking,
    selectSession,
    createSession,
    sendMessage,
  }
})
