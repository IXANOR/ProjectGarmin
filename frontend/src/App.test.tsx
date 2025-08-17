import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
// To keep this simple test passing after adding extra settings components
// we mock them to avoid fetch wiring in this shallow test
vi.mock('./components/SearchSettings', () => ({
  __esModule: true,
  default: () => null,
  SearchSettings: () => null,
}))
vi.mock('./components/PersonalitySettings', () => ({
  __esModule: true,
  default: () => null,
  PersonalitySettings: () => null,
}))
import App from './App'

describe('App', () => {
  beforeEach(() => {
    // Provide a minimal fetch stub for components rendered in App (e.g., ThemeSettings)
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.endsWith('/api/theme')) {
        return { ok: true, json: async () => ({ background_color: '#ffffff', text_color: '#111111', font_type: 'system' }) }
      }
      if (typeof url === 'string' && url.includes('/api/files')) {
        if (url.includes('?')) {
          return { ok: true, json: async () => ([{ id: 'f1', name: 'doc.pdf', session_id: null, size_bytes: 10, created_at: new Date().toISOString(), chunk_count: 1 }]) }
        }
        if (init?.method === 'DELETE') return { ok: true, json: async () => ({}) }
        if (url.endsWith('/api/files/upload') && init?.method === 'POST') return { ok: true, json: async () => ([]) }
      }
      if (typeof url === 'string' && url.endsWith('/api/settings/global')) {
        if (!init || !init.method || init.method === 'GET') return { ok: true, json: async () => ({ temperature: 0.7, top_p: 1.0, max_tokens: 1024, presence_penalty: 0, frequency_penalty: 0 }) }
        return { ok: true, json: async () => ({ temperature: 0.5, top_p: 1.0, max_tokens: 1024, presence_penalty: 0, frequency_penalty: 0 }) }
      }
      return { ok: false, json: async () => ({}) }
    })
  })

  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('renders chat placeholder', () => {
    render(<App />)
    expect(screen.getByText(/Chat placeholder/i)).toBeInTheDocument()
  })
})


