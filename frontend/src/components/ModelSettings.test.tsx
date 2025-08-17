import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'
import ModelSettings from './ModelSettings'

describe('ModelSettings', () => {
  beforeEach(() => {
    let g:any = { temperature: 0.7, top_p: 1.0, max_tokens: 1024, presence_penalty: 0, frequency_penalty: 0 }
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.endsWith('/api/settings/global')) {
        if (!init || !init.method || init.method === 'GET') return { ok: true, json: async () => g }
        g = { ...g, ...(init?.body ? JSON.parse(init.body as string) : {}) }
        return { ok: true, json: async () => g }
      }
      return { ok: false, json: async () => ({}) }
    })
  })
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('loads and saves model settings', async () => {
    render(<ModelSettings />)
    await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())
    const temp = screen.getByTestId('temperature') as HTMLInputElement
    fireEvent.change(temp, { target: { value: '0.5' } })
    fireEvent.click(screen.getByTestId('save-model-settings'))
    await waitFor(() => expect((screen.getByTestId('temperature') as HTMLInputElement).value).toBe('0.5'))
  })
})


