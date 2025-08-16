import {describe, it, expect, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, fireEvent, waitFor} from '@testing-library/react'
import React from 'react'

function PersonalitySettings() {
	const [loading, setLoading] = React.useState(true)
	const [state, setState] = React.useState<any>(null)
	React.useEffect(() => {
		(async () => {
			const res = await fetch('/api/personality')
			const json = await res.json()
			setState(json)
			setLoading(false)
		})()
	}, [])
	if (loading) return <div>Loading…</div>
	return (
		<div>
			<div data-testid="formality">{state.formality}</div>
			<button data-testid="set-formal" onClick={async () => {
				await fetch('/api/personality', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({formality: 'formal'})})
				const res = await fetch('/api/personality')
				setState(await res.json())
			}}>Set Formal</button>
		</div>
	)
}

describe('PersonalitySettings', () => {
	beforeEach(() => {
		let state:any = { formality: 'neutral', humor: 'none', swearing: false, length: 'normal', detail: 'medium', proactivity: false, style: 'mixed', last_updated: new Date().toISOString() }
		// @ts-ignore
		global.fetch = vi.fn(async (url: RequestInfo, init?: RequestInit) => {
			if (typeof url === 'string' && url.endsWith('/api/personality')) {
				if (!init || !init.method || init.method === 'GET') {
					return { ok: true, json: async () => state }
				}
				const body = init.body ? JSON.parse(init.body as string) : {}
				state = { ...state, ...body, last_updated: new Date().toISOString() }
				return { ok: true, json: async () => state }
			}
			return { ok: false, json: async () => ({}) }
		})
	})
	afterEach(() => {
		// @ts-ignore
		delete global.fetch
	})

	it('loads and updates formality', async () => {
		render(<PersonalitySettings />)
		await waitFor(() => expect(screen.queryByText('Loading…')).toBeNull())
		expect(screen.getByTestId('formality').textContent).toBe('neutral')
		fireEvent.click(screen.getByTestId('set-formal'))
		await waitFor(() => expect(screen.getByTestId('formality').textContent).toBe('formal'))
	})
})


