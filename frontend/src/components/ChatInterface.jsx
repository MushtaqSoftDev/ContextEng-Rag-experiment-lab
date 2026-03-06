import { useState, useRef, useEffect } from 'react'
import { streamChat } from '../api'
import './ChatInterface.css'

export default function ChatInterface({ sessionId, params }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const q = input.trim()
    if (!q || !sessionId || streaming) return

    setError(null)
    setInput('')
    const userMsg = { role: 'user', content: q }
    const assistantMsg = { role: 'assistant', content: '' }
    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setStreaming(true)

    let full = ''
    streamChat(
      {
        sessionId,
        question: q,
        provider: params.provider,
        temperature: params.temperature,
        topP: params.topP,
        maxTokens: params.maxTokens,
        reasoningMode: params.reasoningMode,
        chunkSize: params.chunkSize,
        topK: params.topK,
      },
      (chunk) => {
        full += chunk
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last?.role === 'assistant') {
            next[next.length - 1] = { ...last, content: full }
          }
          return next
        })
      },
      () => setStreaming(false),
      (err) => {
        setError(err.message)
        setStreaming(false)
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last?.role === 'assistant') {
            next[next.length - 1] = { ...last, content: full || '[Error: ' + err.message + ']' }
          }
          return next
        })
      }
    )
  }

  const noSession = !sessionId
  const disabled = noSession || streaming

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-placeholder">
            {noSession ? (
              <p>Upload documents first, then ask questions about them.</p>
            ) : (
              <p>Ask a question about your uploaded documents.</p>
            )}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`message message-${m.role}`}>
            <span className="message-role">{m.role === 'user' ? 'You' : 'Assistant'}</span>
            <div className="message-content">
              {m.content || (m.role === 'assistant' && streaming ? (
                <span className="typing-dots"><span></span><span></span><span></span></span>
              ) : '')}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && <p className="chat-error">{error}</p>}

      <div className="chat-input-row">
        <input
          type="text"
          placeholder={noSession ? 'Upload docs to start' : 'Ask a question...'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={disabled}
        />
        <button
          type="button"
          className="btn-send"
          onClick={send}
          disabled={disabled}
        >
          {streaming ? '…' : 'Ask'}
        </button>
      </div>
    </div>
  )
}
