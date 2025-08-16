import React from 'react'

type Personality = {
	formality: 'formal' | 'neutral' | 'casual'
	humor: 'none' | 'moderate' | 'frequent'
	swearing: boolean
	length: 'concise' | 'normal' | 'elaborate'
	detail: 'low' | 'medium' | 'high'
	proactivity: boolean
	style: 'technical' | 'creative' | 'mixed'
	last_updated: string
}

export const PersonalitySettings: React.FC = () => {
	const [state, setState] = React.useState<Personality | null>(null)
	const [loading, setLoading] = React.useState(true)

	React.useEffect(() => {
		let cancelled = false
		async function load() {
			try {
				const res = await fetch('/api/personality')
				const json = await res.json()
				if (!cancelled) setState(json)
			} finally {
				if (!cancelled) setLoading(false)
			}
		}
		load()
		return () => { cancelled = true }
	}, [])

	async function update(partial: Partial<Personality>) {
		await fetch('/api/personality', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(partial) })
		const res = await fetch('/api/personality')
		setState(await res.json())
	}

	if (loading || !state) return <div>Loading…</div>

	return (
		<div>
			<div data-testid="formality">{state.formality}</div>
			<button data-testid="set-formal" onClick={() => update({ formality: 'formal' })}>Set Formal</button>
		</div>
	)
}


