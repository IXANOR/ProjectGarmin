import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'
import {SystemMonitorSettings} from './SystemMonitorSettings'

describe('SystemMonitorSettings', () => {
  beforeEach(() => {
    let state = { mode: 'minimal', debug_logging: false }
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.endsWith('/api/system/settings')) {
        if (!init || init.method === undefined) {
          return { ok: true, json: async () => state }
        } else {
          // POST update
          const body = init.body ? JSON.parse(init.body as string) : {}
          state = { mode: body.mode || state.mode, debug_logging: typeof body.debug_logging === 'boolean' ? body.debug_logging : state.debug_logging } as any
          return { ok: true, json: async () => state }
        }
      }
      return { ok: false, json: async () => ({}) }
    })
  })
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('loads, displays, and updates settings', async () => {
    render(<SystemMonitorSettings />)
    // Wait for initial load
    await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())

    const mode = screen.getByTestId('mode-select') as HTMLSelectElement
    const debug = screen.getByTestId('debug-toggle') as HTMLInputElement
    expect(mode.value).toBe('minimal')
    expect(debug.checked).toBe(false)

    // Change mode
    fireEvent.change(mode, { target: { value: 'expanded' } })
    await waitFor(() => expect((screen.getByTestId('mode-select') as HTMLSelectElement).value).toBe('expanded'))

    // Toggle debug
    fireEvent.click(debug)
    await waitFor(() => expect((screen.getByTestId('debug-toggle') as HTMLInputElement).checked).toBe(true))
  })
})


