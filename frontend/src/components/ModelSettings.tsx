import React from 'react'

type Global = {
  temperature: number
  top_p: number
  max_tokens: number
  presence_penalty: number
  frequency_penalty: number
}

export const ModelSettings: React.FC = () => {
  const [loading, setLoading] = React.useState(true)
  const [g, setG] = React.useState<Global>({
    temperature: 0.7,
    top_p: 1.0,
    max_tokens: 12000,
    presence_penalty: 0,
    frequency_penalty: 1.1,
  })

  React.useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const r = await fetch('/api/settings/global')
        const j = await r.json()
        if (!cancelled) setG(j)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  async function save() {
    await fetch('/api/settings/global', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(g) })
    const r = await fetch('/api/settings/global')
    setG(await r.json())
  }

  if (loading) return <div>Loading…</div>

  return (
    <div>
      <div className="grid grid-cols-2 gap-2">
        <label>Temperature <input data-testid="temperature" type="number" step="0.1" value={g.temperature} onChange={(e)=>setG({...g, temperature: Number(e.target.value)})} /></label>
        <label>Top P <input data-testid="top_p" type="number" step="0.1" value={g.top_p} onChange={(e)=>setG({...g, top_p: Number(e.target.value)})} /></label>
        <label>Max Tokens <input data-testid="max_tokens" type="number" step="1" value={g.max_tokens} onChange={(e)=>setG({...g, max_tokens: Number(e.target.value)})} /></label>
        <label>Presence Penalty <input data-testid="presence_penalty" type="number" step="0.1" value={g.presence_penalty} onChange={(e)=>setG({...g, presence_penalty: Number(e.target.value)})} /></label>
        <label>Frequency Penalty <input data-testid="frequency_penalty" type="number" step="0.1" value={g.frequency_penalty} onChange={(e)=>setG({...g, frequency_penalty: Number(e.target.value)})} /></label>
      </div>
      <button className="mt-3" data-testid="save-model-settings" onClick={save}>Save</button>
    </div>
  )
}

export default ModelSettings


