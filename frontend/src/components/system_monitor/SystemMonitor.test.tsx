import {describe, expect, it, vi, beforeEach, afterEach} from 'vitest'
import {render, screen, act} from '@testing-library/react'
import React from 'react'
import {SystemMonitor} from './SystemMonitor'

const mockUsage = {
  cpu: {percent: 32.5, used_gb: 1.5, total_gb: 32},
  memory: {percent: 58.1, used_gb: 18.6, total_gb: 32},
  gpu: {percent: 67.2, used_gb: 12.0, total_gb: 20},
}

describe('SystemMonitor', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // @ts-ignore
    global.fetch = vi.fn(async () => ({ ok: true, json: async () => mockUsage }))
  })

  afterEach(() => {
    vi.useRealTimers()
    // @ts-ignore
    delete global.fetch
  })

  it('renders minimal mode with percents and refreshes every 3s', async () => {
    render(<SystemMonitor mode="minimal" />)

    // Allow initial effect + fetch to resolve
    await act(async () => {
      await Promise.resolve()
    })
    expect(screen.getByTestId('cpu-percent')).toHaveTextContent('32.5%')
    expect(screen.getByTestId('memory-percent')).toHaveTextContent('58.1%')
    expect(screen.getByTestId('gpu-percent')).toHaveTextContent('67.2%')

    // Ensure periodic refresh
    const fetchSpy = global.fetch as unknown as ReturnType<typeof vi.fn>
    expect(fetchSpy).toHaveBeenCalledTimes(1)
    await act(async () => {
      vi.advanceTimersByTime(3000)
      await Promise.resolve()
    })
    expect(fetchSpy).toHaveBeenCalledTimes(2)
  })

  it('renders expanded mode with raw values and maintains ~4-min rolling history', async () => {
    render(<SystemMonitor mode="expanded" />)
    await act(async () => {
      await Promise.resolve()
    })

    // Expanded shows raw values
    expect(screen.getByTestId('cpu-raw')).toHaveTextContent('1.5 / 32 GB')
    expect(screen.getByTestId('memory-raw')).toHaveTextContent('18.6 / 32 GB')
    expect(screen.getByTestId('gpu-raw')).toHaveTextContent('12 / 20 GB')

    // Simulate many intervals (>80 samples) and ensure history length is capped
    for (let i = 0; i < 100; i++) {
      await act(async () => {
        vi.advanceTimersByTime(3000)
        await Promise.resolve()
      })
    }
    // Access internal history length via attribute on root (exposed for testing)
    const root = screen.getByTestId('system-monitor-root')
    const histLen = Number(root.getAttribute('data-history-length'))
    expect(histLen).toBeLessThanOrEqual(80)
    expect(histLen).toBeGreaterThan(0)
  })
})


