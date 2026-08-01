/**
 * features/alerts — alert management feature module.
 *
 * Provides composable helpers that sit between raw API calls and UI
 * components: severity utilities, alert display formatting, and the
 * `AlertManager` class for orchestrating fetch + WS merge + optimistic
 * updates from a single place.
 *
 * Usage in a component:
 *   const manager = useMemo(() => new AlertManager(), [])
 *   useEffect(() => manager.destroy, [manager])
 */

import { post, patch } from '../lib/api'
import { addWebSocketListener } from '../lib/websocket'
import type { ApiAlert, AlertSeverity } from '../types/api'

// ─── Severity helpers ────────────────────────────────────────────────────────

export const SEVERITY_ORDER: Record<AlertSeverity | string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
}

export function severityFromScore(score?: number | null): AlertSeverity {
  if (score == null) return 'medium'
  if (score >= 0.8) return 'critical'
  if (score >= 0.66) return 'high'
  if (score >= 0.33) return 'medium'
  return 'low'
}

export function severityColor(severity: string): string {
  switch (severity) {
    case 'critical': return 'text-red-600'
    case 'high':     return 'text-red-500'
    case 'medium':   return 'text-yellow-500'
    case 'low':      return 'text-green-500'
    default:         return 'text-gray-400'
  }
}

export function severityBadgeClass(severity: string): string {
  switch (severity) {
    case 'critical': return 'bg-red-600 text-white'
    case 'high':     return 'bg-red-500 text-white'
    case 'medium':   return 'bg-yellow-400 text-black'
    case 'low':      return 'bg-green-400 text-black'
    default:         return 'bg-gray-500 text-white'
  }
}

// ─── Display formatting ──────────────────────────────────────────────────────

export function formatAlertType(type: string): string {
  return type
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function alertAge(createdAt?: string | null): string {
  if (!createdAt) return '—'
  const diffMs = Date.now() - new Date(createdAt).getTime()
  const mins = Math.floor(diffMs / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

// ─── Sorting ─────────────────────────────────────────────────────────────────

export function sortAlertsByPriority(alerts: ApiAlert[]): ApiAlert[] {
  return [...alerts].sort((a, b) => {
    const sevDiff =
      (SEVERITY_ORDER[b.severity] ?? 0) - (SEVERITY_ORDER[a.severity] ?? 0)
    if (sevDiff !== 0) return sevDiff
    // secondary: score descending
    return (b.score ?? 0) - (a.score ?? 0)
  })
}

// ─── AlertManager class ───────────────────────────────────────────────────────

type Listener = (alerts: ApiAlert[]) => void

export class AlertManager {
  private alerts: ApiAlert[] = []
  private listeners: Set<Listener> = new Set()
  private removeWs: (() => void) | null = null

  constructor() {
    this.removeWs = addWebSocketListener(this.handleWsMessage)
  }

  private handleWsMessage = (raw: any) => {
    try {
      const msg = typeof raw === 'string' ? JSON.parse(raw) : raw
      if (msg?.type === 'alert' && msg.data) {
        this.pushAlert(msg.data)
      }
    } catch {
      // ignore
    }
  }

  private notify() {
    this.listeners.forEach((cb) => cb([...this.alerts]))
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener)
    listener([...this.alerts])
    return () => this.listeners.delete(listener)
  }

  setAlerts(alerts: ApiAlert[]) {
    this.alerts = alerts
    this.notify()
  }

  pushAlert(alert: ApiAlert) {
    if (this.alerts.some((a) => a.id === alert.id)) return
    this.alerts = [alert, ...this.alerts].slice(0, 500)
    this.notify()
  }

  async assign(alertId: number, userId: number): Promise<ApiAlert | null> {
    try {
      const updated = await post<ApiAlert>(`/alerts/${alertId}/assign`, { user_id: userId })
      this.alerts = this.alerts.map((a) => (a.id === alertId ? { ...a, ...updated } : a))
      this.notify()
      return updated
    } catch {
      return null
    }
  }

  async resolve(alertId: number, notes?: string): Promise<ApiAlert | null> {
    try {
      const updated = await patch<ApiAlert>(`/alerts/${alertId}/resolve`, { notes })
      this.alerts = this.alerts.map((a) => (a.id === alertId ? { ...a, ...updated } : a))
      this.notify()
      return updated
    } catch {
      return null
    }
  }

  destroy() {
    this.removeWs?.()
    this.listeners.clear()
  }
}

export default AlertManager
