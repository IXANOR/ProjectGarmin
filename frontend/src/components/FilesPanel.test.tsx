import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'
import FilesPanel from './FilesPanel'

describe('FilesPanel', () => {
  beforeEach(() => {
    let listing:any[] = [
      { id: 'f1', name: 'a.pdf', session_id: null, size_bytes: 100, created_at: new Date().toISOString(), chunk_count: 2 },
      { id: 'f2', name: 'b.pdf', session_id: 'S1', size_bytes: 200, created_at: new Date().toISOString(), chunk_count: 3 },
    ]
    // @ts-ignore
    global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
      if (typeof url === 'string' && url.startsWith('/api/files?')) {
        return { ok: true, json: async () => listing }
      }
      if (typeof url === 'string' && url.startsWith('/api/files/') && init?.method === 'DELETE') {
        const id = url.split('/').slice(-1)[0].split('?')[0]
        listing = listing.filter(f => f.id !== id)
        return { ok: true, json: async () => ({}) }
      }
      if (typeof url === 'string' && url.endsWith('/api/files/upload') && init?.method === 'POST') {
        return { ok: true, json: async () => listing }
      }
      return { ok: false, json: async () => ({}) }
    })
  })
  afterEach(() => {
    // @ts-ignore
    delete global.fetch
  })

  it('lists and deletes files', async () => {
    render(<FilesPanel />)
    await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())
    expect(screen.getByText('a.pdf')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('hard-f1'))
    await waitFor(() => expect(screen.queryByText('a.pdf')).toBeNull())
  })
})


