/**
 * useReadings — fetches paginated meter readings for a given meter ID.
 *
 * Automatically prepends live readings pushed via WebSocket so charts
 * update in real-time without needing a full refresh.
 */
import { useEffect, useState, useCallback, useRef } from 'react'
import { get } from '../lib/api'
import { addWebSocketListener } from '../lib/websocket'
import type { ApiReading } from '../types/api'

export interface UseReadingsOptions {
  meterId: number | null
  limit?: number
  skip?: number
  /** Automatically prepend new readings from WebSocket. Default: true */
  liveUpdates?: boolean
}

export interface UseReadingsResult {
  readings: ApiReading[]
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useReadings(opts: UseReadingsOptions): UseReadingsResult {
  const { meterId, limit = 100, skip = 0, liveUpdates = true } = opts

  const [readings, setReadings] = useState<ApiReading[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isMounted = useRef(true)
  useEffect(() => {
    isMounted.current = true
    return () => { isMounted.current = false }
  }, [])

  const fetchReadings = useCallback(async () => {
    if (meterId == null) {
      setReadings([])
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await get<ApiReading[]>(`/readings/by-meter/${meterId}`, {
        params: { skip, limit },
      })
      if (isMounted.current) setReadings(Array.isArray(data) ? data : [])
    } catch (e: any) {
      if (isMounted.current) setError(e?.message ?? 'Failed to load readings')
    } finally {
      if (isMounted.current) setLoading(false)
    }
  }, [meterId, limit, skip])

  useEffect(() => {
    fetchReadings()
  }, [fetchReadings])

  // Live prepend from WebSocket
  useEffect(() => {
    if (!liveUpdates || meterId == null) return

    const remove = addWebSocketListener((raw: string) => {
      try {
        const msg = typeof raw === 'string' ? JSON.parse(raw) : raw
        if (msg?.type === 'reading' && msg.data?.meter_id === meterId) {
          const incoming: ApiReading = msg.data
          if (!isMounted.current) return
          setReadings((prev) => {
            if (prev.some((r) => r.id === incoming.id)) return prev
            // Prepend newest; keep list bounded at limit * 2
            return [incoming, ...prev].slice(0, limit * 2)
          })
        }
      } catch {
        // ignore parse errors
      }
    })

    return remove
  }, [liveUpdates, meterId, limit])

  return { readings, loading, error, refetch: fetchReadings }
}

export default useReadings
