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
  const [profiles, setProfiles] = React.useState<string[]>([])

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
    ;(async () => {
      try {
        const r = await fetch('/api/personality/profiles')
        if (r.ok) {
          const j = await r.json()
          setProfiles(j.profiles || [])
        }
      } catch {}
    })()
		return () => { cancelled = true }
	}, [])

	async function update(partial: Partial<Personality>) {
		await fetch('/api/personality', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(partial) })
		const res = await fetch('/api/personality')
		setState(await res.json())
	}

	if (loading || !state) return <div>Loading…</div>

	return (
		<div className="space-y-2">
			<div className="text-sm text-gray-600">Current: <span data-testid="formality">{state.formality}</span></div>
			<div className="flex flex-wrap gap-2">
				{profiles.map((p) => (
					<button key={p} className="px-2 py-1 rounded border" onClick={async () => {
						await fetch('/api/personality', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ profile: p }) })
						const res = await fetch('/api/personality')
						setState(await res.json())
					}}>{p}</button>
				))}
			</div>
		</div>
	)
}


