import React from 'react'

type Settings = { mode: 'minimal' | 'expanded'; debug_logging: boolean }

export const SystemMonitorSettings: React.FC = () => {
  const [settings, setSettings] = React.useState<Settings>({ mode: 'minimal', debug_logging: false })
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const r = await fetch('/api/system/settings')
        if (!r.ok) throw new Error('failed')
        const s = await r.json()
        if (!cancelled) setSettings(s)
      } catch (_) {
        // ignore
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  async function save(next: Partial<Settings>) {
    const body = { ...settings, ...next }
    const r = await fetch('/api/system/settings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    if (r.ok) {
      setSettings(await r.json())
    }
  }

  if (loading) return <div>Loading…</div>

  return (
    <div>
      <label>
        Mode:
        <select data-testid="mode-select" value={settings.mode} onChange={(e) => save({ mode: e.target.value as Settings['mode'] })}>
          <option value="minimal">Minimal</option>
          <option value="expanded">Expanded</option>
        </select>
      </label>
      <label style={{ marginLeft: 12 }}>
        <input data-testid="debug-toggle" type="checkbox" checked={settings.debug_logging} onChange={(e) => save({ debug_logging: e.target.checked })} />
        Debug logging
      </label>
    </div>
  )
}


