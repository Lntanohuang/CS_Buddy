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

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data:')) continue
      const raw = line.slice(5).trim()
      if (!raw || raw === '[DONE]') continue

      try {
        const event: SSEEvent = JSON.parse(raw)
        if (event.type === 'token' && event.content) {
          onToken(event.content)
        } else if (event.type === 'done') {
          onDone(event.data)
        } else if (event.type === 'error') {
          onError(event.content ?? '未知错误')
        }
      } catch {
        // skip malformed lines
      }
    }
  }
}
