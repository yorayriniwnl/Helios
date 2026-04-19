/**
 * useDashboard — fetches the dashboard summary KPIs and recovery metrics.
 *
 * Automatically polls every `pollMs` milliseconds (default 30 s) so the
 * dashboard stays fresh without a full page reload.
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { get } from '../lib/api'
import type { DashboardSummary, RecoveryMetrics } from '../types/api'

export interface UseDashboardOptions {
  /** Re-fetch interval in ms. Set to 0 to disable polling. Default: 30 000 */
  pollMs?: number
}

export interface UseDashboardResult {
  summary: DashboardSummary | null
  recovery: RecoveryMetrics | null
  loading: boolean
  error: string | null
  refetch: () => void
}

const DEFAULT_SUMMARY: DashboardSummary = {
  total_meters: 0,
  total_readings: 0,
  total_alerts: 0,
  zone_loss_percentage: 0,
}

export function useDashboard(opts: UseDashboardOptions = {}): UseDashboardResult {
  const { pollMs = 30_000 } = opts

  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [recovery, setRecovery] = useState<RecoveryMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const abortRef = useRef<AbortController | null>(null)

  const fetchAll = useCallback(async () => {
    // Cancel any in-flight request
    if (abortRef.current) abortRef.current.abort()
    abortRef.current = new AbortController()

    setLoading(true)
    setError(null)

    try {
      const [sum, rec] = await Promise.allSettled([
        get<DashboardSummary>('/dashboard/summary'),
        get<RecoveryMetrics>('/dashboard/recovery'),
      ])

      if (sum.status === 'fulfilled') setSummary(sum.value ?? DEFAULT_SUMMARY)
      if (rec.status === 'fulfilled') setRecovery(rec.value ?? null)

      if (sum.status === 'rejected' && rec.status === 'rejected') {
        setError('Failed to load dashboard data')
      }
    } catch (e: any) {
      if (e?.name !== 'CanceledError' && e?.name !== 'AbortError') {
        setError(e?.message ?? 'Unknown error')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  // Initial fetch
  useEffect(() => {
    fetchAll()
    return () => abortRef.current?.abort()
  }, [fetchAll])

  // Polling
  useEffect(() => {
    if (!pollMs) return
    const id = setInterval(fetchAll, pollMs)
    return () => clearInterval(id)
  }, [fetchAll, pollMs])

  return { summary, recovery, loading, error, refetch: fetchAll }
}

export default useDashboard
