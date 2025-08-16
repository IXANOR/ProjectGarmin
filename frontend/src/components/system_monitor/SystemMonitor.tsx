import React from 'react'

type Mode = 'minimal' | 'expanded'

type Usage = {
  cpu: { percent: number; used_gb: number; total_gb: number }
  memory: { percent: number; used_gb: number; total_gb: number }
  gpu: { percent: number; used_gb: number; total_gb: number }
}

async function fetchUsage(): Promise<Usage> {
  const resp = await fetch('/api/system/usage')
  if (!resp.ok) throw new Error('usage fetch failed')
  return resp.json()
}

async function fetchSettings(): Promise<{ mode: Mode }> {
  const resp = await fetch('/api/system/settings')
  if (!resp.ok) throw new Error('settings fetch failed')
  const json = await resp.json()
  // tolerate missing fields
  const mode = (json?.mode === 'expanded' ? 'expanded' : 'minimal') as Mode
  return { mode }
}

export const SystemMonitor: React.FC<{ mode?: Mode }> = ({ mode }) => {
  const [usage, setUsage] = React.useState<Usage | null>(null)
  const [history, setHistory] = React.useState<Array<{ t: number; u: Usage }>>([])
  const [effectiveMode, setEffectiveMode] = React.useState<Mode>(mode ?? 'minimal')

  React.useEffect(() => {
    let cancelled = false
    async function tick() {
      try {
        const [u, s] = await Promise.all([
          fetchUsage(),
          mode ? Promise.resolve<{ mode: Mode }>({ mode }) : fetchSettings(),
        ])
        if (cancelled) return
        setEffectiveMode(s.mode)
        setUsage(u)
        setHistory((prev) => {
          const next = [...prev, { t: Date.now(), u }]
          // Keep ~4 minutes at 3s cadence => ~80 samples
          while (next.length > 80) next.shift()
          return next
        })
      } catch (_) {
        // ignore failures
      }
    }
    // initial
    tick()
    const id = setInterval(tick, 3000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [mode])

  return (
    <div data-testid="system-monitor-root" data-history-length={history.length} className="flex gap-4 items-center">
      <Metric label="CPU" usage={usage?.cpu} mode={effectiveMode} percentTestId="cpu-percent" rawTestId="cpu-raw" barTestId="cpu-bar" />
      <Metric label="Memory" usage={usage?.memory} mode={effectiveMode} percentTestId="memory-percent" rawTestId="memory-raw" barTestId="memory-bar" />
      <Metric label="GPU" usage={usage?.gpu} mode={effectiveMode} percentTestId="gpu-percent" rawTestId="gpu-raw" barTestId="gpu-bar" />
    </div>
  )
}

const Metric: React.FC<{
  label: string
  usage?: { percent: number; used_gb: number; total_gb: number }
  mode: Mode
  percentTestId: string
  rawTestId: string
  barTestId: string
}> = ({ label, usage, mode, percentTestId, rawTestId, barTestId }) => {
  const percent = usage ? `${usage.percent}%` : '—'
  const raw = usage ? `${usage.used_gb} / ${usage.total_gb} GB` : '—'
  return (
    <div className="flex flex-col text-sm">
      <div className="font-semibold">{label}</div>
      <div data-testid={percentTestId}>{percent}</div>
      {mode === 'expanded' ? (
        <>
          <div data-testid={rawTestId} className="text-xs opacity-70">{raw}</div>
          <div data-testid={barTestId} className="h-1 bg-gray-300 w-24">
            <div className="h-1 bg-green-600" style={{ width: `${Math.max(0, Math.min(100, usage?.percent ?? 0))}%` }} />
          </div>
        </>
      ) : null}
    </div>
  )
}


