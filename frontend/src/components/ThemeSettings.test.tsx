import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'

function ThemeSettings() {
  const [loading, setLoading] = React.useState(true)
  const [state, setState] = React.useState<any>(null)
  React.useEffect(() => {
    (async () => {
      const res = await fetch('/api/theme')
      const json = await res.json()
      setState(json)
      setLoading(false)
    })()
  }, [])
  if (loading) return <div>Loading…</div>
  return (
    <div>
      <div data-testid="bg">{state.background_color}</div>
      <button data-testid="set-dark" onClick={async () => {
        await fetch('/api/theme', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ background_color: '#000000' }) })
        const res = await fetch('/api/theme')
        setState(await res.json())
      }}>Set Dark BG</button>
    </div>
  )
}

describe('ThemeSettings', () => {
  beforeEach(() => {
    let theme:any = { background_color: '#ffffff', text_color: '#111111', font_type: 'system' }
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.endsWith('/api/theme')) {
        if (!init || !init.method || init.method === 'GET') {
          return { ok: true, json: async () => theme }
        }
        const body = init.body ? JSON.parse(init.body as string) : {}
        theme = { ...theme, ...body }
        return { ok: true, json: async () => theme }
      }
      return { ok: false, json: async () => ({}) }
    })
  })
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('loads and updates background color', async () => {
    render(<ThemeSettings />)
    await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())
    expect(screen.getByTestId('bg').textContent?.toLowerCase()).toBe('#ffffff')
    fireEvent.click(screen.getByTestId('set-dark'))
    await waitFor(() => expect(screen.getByTestId('bg').textContent?.toLowerCase()).toBe('#000000'))
  })
})


