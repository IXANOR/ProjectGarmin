import React from 'react'

const FONT_OPTIONS = [
  'system',
  'arial',
  'helvetica',
  'times_new_roman',
  'georgia',
  'courier_new',
  'consolas',
  'fira_code',
  'roboto',
  'inter',
]

type Theme = {
  background_color: string
  text_color: string
  panel_color: string
  border_color?: string
  font_type: string
  preset_name?: string
}

export const ThemeSettings: React.FC = () => {
  const [loading, setLoading] = React.useState(true)
  const [theme, setTheme] = React.useState<Theme | null>(null)
  const [customName, setCustomName] = React.useState('')
  const rootRef = React.useRef<HTMLDivElement | null>(null)

  React.useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const res = await fetch('/api/theme')
        if (!res.ok) throw new Error('theme fetch failed')
        const json = await res.json()
        if (!cancelled) {
          setTheme(json)
          applyCssVars(json)
        }
      } catch (_e) {
        // Fallback to defaults so UI is usable even if backend unavailable
        if (!cancelled) {
          const def = { background_color: '#ffffff', text_color: '#111111', panel_color: '#ffffff', font_type: 'system' }
          setTheme(def)
          applyCssVars(def)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    ;(async () => {
      try {
        const r = await fetch('/api/theme/presets')
        // optional usage in this component (rendered below)
        if (r.ok) {
          const p = await r.json()
          ;(window as any).__theme_presets__ = p
        }
      } catch {}
    })()
    return () => { cancelled = true }
  }, [])

  async function save(partial: Partial<Theme>) {
    await fetch('/api/theme', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(partial) })
    const res = await fetch('/api/theme')
    const next = await res.json()
    setTheme(next)
    // Apply to document root for live preview using canonical values from backend
    applyCssVars(next)
  }

  async function applyPreset(name: string) {
    await fetch('/api/theme', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ preset: name }) })
    const res = await fetch('/api/theme')
    const next = await res.json()
    setTheme(next)
    applyCssVars(next)
  }

  async function savePreset() {
    if (!theme || !customName.trim()) return
    await fetch('/api/theme/presets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
      name: customName.trim(),
      background_color: theme.background_color,
      text_color: theme.text_color,
      panel_color: theme.panel_color,
      border_color: theme.border_color || '#e5e7eb',
      font_type: theme.font_type,
    })})
    setCustomName('')
    try {
      const r = await fetch('/api/theme/presets')
      if (r.ok) (window as any).__theme_presets__ = await r.json()
    } catch {}
  }

  if (loading || !theme) return <div>Loading…</div>

  return (
    <div className="space-y-3" ref={rootRef}>
      <div className="mb-1 text-sm text-gray-600">Background</div>
      <input
        data-testid="bg-input"
        type="color"
        value={theme.background_color}
        onChange={(e) => setTheme({ ...theme, background_color: e.target.value })}
      />
      <div className="mb-1 mt-2 text-sm text-gray-600">Text color</div>
      <input
        data-testid="fg-input"
        type="color"
        value={theme.text_color}
        onChange={(e) => setTheme({ ...theme, text_color: e.target.value })}
      />
      <div className="mb-1 mt-2 text-sm text-gray-600">Panel color</div>
      <input
        data-testid="panel-input"
        type="color"
        value={theme.panel_color}
        onChange={(e) => setTheme({ ...theme, panel_color: e.target.value })}
      />
      <div className="mb-1 mt-2 text-sm text-gray-600">Border color</div>
      <input
        data-testid="border-input"
        type="color"
        value={theme.border_color || '#e5e7eb'}
        onChange={(e) => setTheme({ ...theme, border_color: e.target.value })}
      />
      <div className="mb-1 mt-2 text-sm text-gray-600">Font</div>
      <select
        data-testid="font-select"
        value={theme.font_type}
        onChange={(e) => setTheme({ ...theme, font_type: e.target.value })}
      >
        {FONT_OPTIONS.map((f) => <option key={f} value={f}>{f}</option>)}
      </select>
      <div className="mt-3 flex items-center gap-2">
        <button className="px-3 py-1 rounded bg-gray-900 text-white" data-testid="save-theme" onClick={() => save({
          background_color: theme.background_color,
          text_color: theme.text_color,
          panel_color: theme.panel_color,
          border_color: theme.border_color || '#e5e7eb',
          font_type: theme.font_type,
        })}>Save</button>
      </div>
      <div className="mt-3 flex gap-2 items-center">
        <input
          data-testid="preset-name"
          type="text"
          placeholder="Preset name"
          value={customName}
          onChange={(e) => setCustomName(e.target.value)}
        />
        <button className="px-2 py-1 rounded border" data-testid="save-preset" onClick={savePreset}>Save as preset</button>
      </div>
      {Boolean((window as any).__theme_presets__) && (
        <div className="mt-3 space-y-2">
          <div className="text-sm text-gray-600">Saved presets</div>
          <div className="flex flex-wrap gap-2">
            {((window as any).__theme_presets__.built_in || []).map((p: any) => (
              <button key={p.name} className="px-2 py-1 rounded border" onClick={() => applyPreset(p.name)}>{p.name}</button>
            ))}
            {((window as any).__theme_presets__.custom || []).map((p: any) => (
              <div key={p.name} className="preset-pill">
                <button onClick={() => applyPreset(p.name)}>{p.name}</button>
                <button
                  className="delete"
                  aria-label={`delete ${p.name}`}
                  onClick={async (e) => {
                    e.stopPropagation()
                    if (!confirm(`Delete preset "${p.name}"?`)) return
                    await fetch(`/api/theme/presets/${encodeURIComponent(p.name)}`, { method: 'DELETE' })
                    const r = await fetch('/api/theme/presets')
                    if (r.ok) (window as any).__theme_presets__ = await r.json()
                    // force re-render
                    try { (window as any).dispatchEvent(new Event('theme-presets-changed')) } catch {}
                  }}
                >×</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function applyCssVars(theme: Partial<Theme>) {
  const root = document.documentElement
  if (theme.background_color) root.style.setProperty('--app-bg', theme.background_color)
  if (theme.text_color) root.style.setProperty('--app-fg', theme.text_color)
  // Font map to CSS font-family quickly
  if (theme.font_type) {
    const map: Record<string, string> = {
      system: 'system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Arial, sans-serif',
      helvetica: 'Helvetica, Arial, sans-serif',
      arial: 'Arial, Helvetica, sans-serif',
      times_new_roman: '"Times New Roman", Times, serif',
      georgia: 'Georgia, serif',
      courier_new: '"Courier New", Courier, monospace',
      consolas: 'Consolas, monospace',
      fira_code: '"Fira Code", Consolas, monospace',
      roboto: 'Roboto, system-ui, sans-serif',
      inter: 'Inter, system-ui, sans-serif',
    }
    root.style.setProperty('--app-font', map[theme.font_type] || map.system)
  }
  if ((theme as any).panel_color) {
    root.style.setProperty('--app-panel', (theme as any).panel_color)
  }
  if ((theme as any).border_color) {
    root.style.setProperty('--app-border', (theme as any).border_color)
  }
}

export default ThemeSettings


