export interface SSEEvent {
  type: 'token' | 'done' | 'error'
  content?: string
  data?: Record<string, unknown>
}

export async function streamChat(
  sessionId: string,
  message: string,
  onToken: (token: string) => void,
  onDone: (data?: Record<string, unknown>) => void,
  onError: (error: string) => void,
  signal?: AbortSignal,
) {
  const res = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal,
  })

  if (!res.ok) {
    onError(`请求失败: ${res.status}`)
    return
  }

  const reader = res.body?.getReader()
  if (!reader) {
    onError('无法读取响应流')
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let receivedToken = false
  let receivedTerminalEvent = false

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data:')) continue
      const raw = line.slice(5).trim()
      if (!raw) continue

      if (raw === '[DONE]') {
        receivedTerminalEvent = true
        onDone()
        return
      }

      try {
        const event: SSEEvent = JSON.parse(raw)
        if (event.type === 'token' && event.content) {
          receivedToken = true
          onToken(event.content)
        } else if (event.type === 'done') {
          receivedTerminalEvent = true
          onDone(event.data)
          return
        } else if (event.type === 'error') {
          receivedTerminalEvent = true
          onError(event.content ?? '未知错误')
          return
        }
      } catch {
        // skip malformed lines
      }
    }
  }

  if (!receivedTerminalEvent) {
    if (receivedToken) {
      onDone()
    } else {
      onError('模型没有返回内容，请稍后重试')
    }
  }
}
