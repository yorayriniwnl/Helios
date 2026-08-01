/**
 * useAlerts — paginated alert list with optional severity/status filtering,
 * real-time prepending of WebSocket alert events, and helpers for
 * assigning / resolving individual alerts.
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { get, patch, post } from '../lib/api'
import { addWebSocketListener } from '../lib/websocket'
import type { ApiAlert, AlertSeverity, AlertStatus } from '../types/api'

export interface AlertFilters {
  severity?: AlertSeverity | ''
  status?: AlertStatus | ''
  limit?: number
  skip?: number
}

export interface UseAlertsResult {
  alerts: ApiAlert[]
  loading: boolean
  error: string | null
  total: number
  refetch: () => void
  assign: (alertId: number, userId: number) => Promise<void>
  resolve: (alertId: number, notes?: string) => Promise<void>
}

export function useAlerts(filters: AlertFilters = {}): UseAlertsResult {
  const { severity = '', status = '', limit = 50, skip = 0 } = filters

  const [alerts, setAlerts] = useState<ApiAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

  const isMounted = useRef(true)
  useEffect(() => {
    isMounted.current = true
    return () => { isMounted.current = false }
  }, [])

  const fetchAlerts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, string | number> = { limit, skip }
      if (severity) params.severity = severity
      if (status) params.status = status

      const data = await get<ApiAlert[] | { items: ApiAlert[]; total: number }>('/alerts', { params })

      if (!isMounted.current) return

      if (Array.isArray(data)) {
        setAlerts(data)
        setTotal(data.length)
      } else if (data && 'items' in data) {
        setAlerts(data.items)
        setTotal(data.total ?? data.items.length)
      }
    } catch (e: any) {
      if (isMounted.current) setError(e?.message ?? 'Failed to load alerts')
    } finally {
      if (isMounted.current) setLoading(false)
    }
  }, [severity, status, limit, skip])

  // Initial + dependency-change fetch
  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  // Prepend real-time alerts from WebSocket
  useEffect(() => {
    const remove = addWebSocketListener((raw: string) => {
      try {
        const msg = JSON.parse(raw)
        if (msg.type === 'alert' && msg.data) {
          const incoming: ApiAlert = msg.data
          if (!isMounted.current) return
          setAlerts((prev) => {
            // avoid duplicates
            if (prev.some((a) => a.id === incoming.id)) return prev
            return [incoming, ...prev]
          })
          setTotal((t) => t + 1)
        }
      } catch {
        // ignore parse errors
      }
    })
    return remove
  }, [])

  // Assign an alert to a user
  const assign = useCallback(async (alertId: number, userId: number) => {
    const updated = await post<ApiAlert>(`/alerts/${alertId}/assign`, { user_id: userId })
    if (updated && isMounted.current) {
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, ...updated } : a)))
    }
  }, [])

  // Resolve an alert with optional notes
  const resolve = useCallback(async (alertId: number, notes?: string) => {
    const updated = await patch<ApiAlert>(`/alerts/${alertId}/resolve`, { notes })
    if (updated && isMounted.current) {
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, ...updated } : a)))
    }
  }, [])

  return { alerts, loading, error, total, refetch: fetchAlerts, assign, resolve }
}

export default useAlerts
