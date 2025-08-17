import { useCallback, useState } from 'react'

type Message = { role: 'user' | 'assistant'; content: string }

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const sendMessage = useCallback(async () => {
    const sessionId = 'test-session'
    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage, { role: 'assistant', content: '' }])

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        // send full history up to this user message (exclude the temporary assistant placeholder)
        messages: [...messages, userMessage],
      }),
    })

    if (!response.body) return

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    let assistantText = ''
    let buffer = ''
    // parse SSE: lines starting with `data: `, separated by double newlines
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split(/\n\n/)
      buffer = parts.pop() ?? ''
      for (const part of parts) {
        const trimmed = part.trim()
        if (!trimmed) continue
        if (trimmed.startsWith('data: ')) {
          const token = trimmed.slice('data: '.length)
          assistantText += (assistantText ? ' ' : '') + token
          setMessages((prev) => {
            const updated = [...prev]
            // Update the last assistant message in-place to avoid duplicates
            for (let i = updated.length - 1; i >= 0; i--) {
              if (updated[i].role === 'assistant') {
                updated[i] = { role: 'assistant', content: assistantText }
                return updated
              }
            }
            updated.push({ role: 'assistant', content: assistantText })
            return updated
          })
        }
      }
    }
    setInput('')
  }, [input, messages])

  return (
    <div className="flex flex-col gap-3">
      <div className="border rounded p-3 min-h-24" style={{ background: 'var(--app-panel)' }}>
        {messages.map((m, i) => (
          <div key={i} data-testid={m.role === 'assistant' ? 'assistant-message' : undefined}>
            <strong>{m.role}:</strong> {m.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          aria-label="Message"
          className="border rounded px-2 py-1 flex-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button className="border rounded px-3 py-1" style={{ background: 'var(--app-panel)', borderColor: 'var(--app-border)' }} onClick={sendMessage}>Send</button>
      </div>
    </div>
  )
}


