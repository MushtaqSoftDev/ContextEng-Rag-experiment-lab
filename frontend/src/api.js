// Use proxy in dev (vite proxies /api to backend), or explicit URL for production
const API_URL = import.meta.env.VITE_API_URL || ''

export async function getAvailableProviders() {
  try {
    const res = await fetch(`${API_URL}/api/providers`)
    if (!res.ok) return { openai: true, groq: true, deepseek: true, huggingface: true }
    return res.json()
  } catch {
    return { openai: true, groq: true, deepseek: true, huggingface: true }
  }
}

export async function uploadDocuments(files) {
  const formData = new FormData()
  for (const f of files) {
    formData.append('files', f)
  }
  const res = await fetch(`${API_URL}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Upload failed')
  }
  return res.json()
}

export async function indexDocuments(sessionId) {
  const res = await fetch(`${API_URL}/api/documents/${sessionId}/index`, {
    method: 'POST',
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Index failed')
  }
  return res.json()
}

export function streamChat(params, onChunk, onDone, onError) {
  return fetch(`${API_URL}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: params.sessionId,
      question: params.question,
      provider: params.provider,
      temperature: params.temperature,
      top_p: params.topP,
      max_tokens: params.maxTokens,
      reasoning_mode: params.reasoningMode,
      chunk_size: params.chunkSize,
      top_k: params.topK,
    }),
  }).then(async (res) => {
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }))
      onError(new Error(err.detail || 'Chat failed'))
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()
        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const obj = JSON.parse(line)
            if (obj.text) onChunk(obj.text)
          } catch (_) {}
        }
      }
      if (buffer.trim()) {
        try {
          const obj = JSON.parse(buffer)
          if (obj.text) onChunk(obj.text)
        } catch (_) {}
      }
      onDone()
    } catch (e) {
      onError(e)
    }
  })
}
