import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'
import {SearchSettings} from './SearchSettings'

describe('SearchSettings', () => {
  beforeEach(() => {
    let state = { allow_internet_search: false, debug_logging: false, has_bing_api_key: false }
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.endsWith('/api/settings/search')) {
        if (!init || !init.method) {
          return { ok: true, json: async () => state }
        }
        const body = init.body ? JSON.parse(init.body as string) : {}
        state = {
          allow_internet_search: typeof body.allow_internet_search === 'boolean' ? body.allow_internet_search : state.allow_internet_search,
          debug_logging: typeof body.debug_logging === 'boolean' ? body.debug_logging : state.debug_logging,
          has_bing_api_key: state.has_bing_api_key,
        }
        return { ok: true, json: async () => state }
      }
      return { ok: false, json: async () => ({}) }
    })
  })
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('loads, toggles allow search and debug logging', async () => {
    render(<SearchSettings />)
    await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())
    const allow = screen.getByTestId('allow-search-toggle') as HTMLInputElement
    const dbg = screen.getByTestId('search-debug-toggle') as HTMLInputElement
    expect(allow.checked).toBe(false)
    expect(dbg.checked).toBe(false)
    fireEvent.click(allow)
    await waitFor(() => expect((screen.getByTestId('allow-search-toggle') as HTMLInputElement).checked).toBe(true))
    fireEvent.click(dbg)
    await waitFor(() => expect((screen.getByTestId('search-debug-toggle') as HTMLInputElement).checked).toBe(true))
  })
})


