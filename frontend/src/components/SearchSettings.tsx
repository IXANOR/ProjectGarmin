import React from 'react'

type SearchSettings = {
  allow_internet_search: boolean
  debug_logging: boolean
  has_bing_api_key: boolean
}

export const SearchSettings: React.FC = () => {
  const [settings, setSettings] = React.useState<SearchSettings | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const r = await fetch('/api/settings/search')
        if (!r.ok) throw new Error('failed')
        const s = await r.json()
        if (!cancelled) setSettings(s)
      } catch (_) {
        if (!cancelled) setSettings({ allow_internet_search: false, debug_logging: false, has_bing_api_key: false })
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  async function save(next: Partial<SearchSettings>) {
    if (!settings) return
    const body = { ...settings, ...next }
    const r = await fetch('/api/settings/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    if (r.ok) setSettings(await r.json())
  }

  if (loading || !settings) return <div>Loading…</div>

  return (
    <div>
      <label>
        <input
          data-testid="allow-search-toggle"
          type="checkbox"
          checked={settings.allow_internet_search}
          onChange={(e) => save({ allow_internet_search: e.target.checked })}
        />
        Allow AI Internet Search
      </label>
      <label style={{ marginLeft: 12 }}>
        <input
          data-testid="search-debug-toggle"
          type="checkbox"
          checked={settings.debug_logging}
          onChange={(e) => save({ debug_logging: e.target.checked })}
        />
        Debug logging
      </label>
      <span style={{ marginLeft: 12 }} data-testid="bing-key-indicator">
        {settings.has_bing_api_key ? 'Bing key: configured' : 'Bing key: not set'}
      </span>
    </div>
  )
}


