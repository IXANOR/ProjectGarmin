import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Chat from './Chat'

function createSSEStream(lines: string[]) {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      const encoder = new TextEncoder()
      for (const line of lines) {
        controller.enqueue(encoder.encode(line))
      }
      controller.close()
    },
  })
}

describe('Chat (SSE)', () => {
  it('renders streamed tokens in order', async () => {
    const sseLines = [
      'data: Hello\n\n',
      'data: from\n\n',
      'data: mock\n\n',
      'data: AI!\n\n',
    ]

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'content-type': 'text/event-stream' }),
      body: createSSEStream(sseLines),
    }))

    render(<Chat />)

    const input = screen.getByRole('textbox') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.click(screen.getByRole('button', { name: /send/i }))

    await waitFor(async () => {
      const el = await screen.findByTestId('assistant-message')
      expect(el).toHaveTextContent('Hello from mock AI!')
    })
  })
})


