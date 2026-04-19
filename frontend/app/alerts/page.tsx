"use client"

import React, { useEffect, useState } from 'react'
import { get, post, patch } from '../../lib/api'
import connectWebSocket, { addWebSocketListener } from '../../lib/websocket'
import Spinner from '../../components/ui/Spinner'
import ErrorMessage from '../../components/ui/ErrorMessage'
import EmptyState from '../../components/ui/EmptyState'

type AlertItem = {
  id: number
  meter_id?: number
  reading_id?: number
  type: string
  score?: number
  explanation?: string
  assigned_to?: number | null
  status: string
  created_at?: string
}

function mapSeverityFromScore(score?: number) {
  if (score == null) return 'medium'
  if (score >= 0.8) return 'critical'
  if (score >= 0.66) return 'high'
  if (score >= 0.33) return 'medium'
  return 'low'
}

function severityClass(s: string) {
  switch (s) {
    case 'critical':
      return 'inline-flex items-center px-2 py-1 text-xs font-semibold rounded bg-red-600 text-white'
    case 'high':
      return 'inline-flex items-center px-2 py-1 text-xs font-semibold rounded bg-red-500 text-white'
    case 'medium':
      return 'inline-flex items-center px-2 py-1 text-xs font-semibold rounded bg-yellow-400 text-black'
    case 'low':
    default:
      return 'inline-flex items-center px-2 py-1 text-xs font-semibold rounded bg-green-400 text-black'
  }
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [severityFilter, setSeverityFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    let mounted = true
    async function fetchAlerts() {
      setLoading(true)
      setError(null)
      try {
        const res = await get<AlertItem[]>('/alerts', undefined, { cacheMs: 10000 })
        if (!mounted) return
        setAlerts(res || [])
      } catch (err: any) {
        if (!mounted) return
        setError(err?.message || 'Failed to load alerts')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    fetchAlerts()

    function listener(msg: any) {
      if (!msg || !msg.type) return
      if (msg.type === 'alert') {
        const a = msg.data || {}
        const item: AlertItem = {
          id: a.id ?? Math.floor(Math.random() * 1000000),
          meter_id: a.meter_id,
          reading_id: a.reading_id,
          type: a.type || 'alert',
          score: a.score,
          explanation: a.explanation,
          assigned_to: a.assigned_to ?? null,
          status: a.status ?? 'open',
          created_at: a.created_at || a.timestamp || new Date().toISOString(),
        }
        setAlerts((prev) => [item, ...prev].slice(0, 500))
      }
    }

    const remove = addWebSocketListener(listener)
    try {
      connectWebSocket()
    } catch {
      // best effort for local demo
    }

    return () => {
      mounted = false
      try {
        remove()
      } catch {
        // ignore cleanup errors
      }
    }
  }, [])

  function filteredAlerts() {
    return alerts.filter((alert) => {
      const severity = mapSeverityFromScore(alert.score)
      if (severityFilter !== 'all' && severity !== severityFilter) return false
      if (statusFilter !== 'all' && alert.status !== statusFilter) return false
      return true
    })
  }

  async function handleAssign(alertId: number) {
    const raw = window.prompt('Assign to user id (numeric):')
    if (!raw) return
    const userId = parseInt(raw, 10)
    if (Number.isNaN(userId)) {
      alert('Invalid user id')
      return
    }
    try {
      const res = await post(`/alerts/${alertId}/assign`, { user_id: userId })
      setAlerts((prev) => prev.map((item) => (item.id === res.id ? res : item)))
    } catch (err: any) {
      alert(err?.message || 'Assign failed')
    }
  }

  async function handleResolve(alertId: number) {
    const notes = window.prompt('Resolution notes (optional):', '')
    try {
      const res = await patch(`/alerts/${alertId}/resolve`, { notes })
      setAlerts((prev) => prev.map((item) => (item.id === res.id ? res : item)))
    } catch (err: any) {
      alert(err?.message || 'Resolve failed')
    }
  }

  return (
    <div className="container mx-auto">
      <h1 className="mb-4 text-3xl font-bold">Alerts</h1>

      <div className="mb-4 flex items-center gap-3">
        <div className="card flex items-center gap-3 p-3">
          <label className="text-sm text-[var(--muted)]">Severity</label>
          <select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)} className="rounded border border-white/6 bg-transparent px-2 py-1">
            <option value="all">All</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="card flex items-center gap-3 p-3">
          <label className="text-sm text-[var(--muted)]">Status</label>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="rounded border border-white/6 bg-transparent px-2 py-1">
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div>
          <button
            onClick={() => {
              setLoading(true)
              get('/alerts', undefined, { cacheMs: 10000 })
                .then((result) => setAlerts(result || []))
                .catch((err) => setError(err?.message || 'Failed'))
                .finally(() => setLoading(false))
            }}
            className="btn"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="card flex justify-center py-6"><Spinner /></div>
      ) : error ? (
        <div className="mb-4"><ErrorMessage message={error} /></div>
      ) : filteredAlerts().length === 0 ? (
        <div className="mb-4">
          <EmptyState title="No alerts" description="There are no alerts matching the selected filters." />
        </div>
      ) : (
        <div className="card overflow-auto">
          <table className="min-w-full table-auto">
            <thead>
              <tr className="text-sm text-[var(--muted)]">
                <th className="px-4 py-2 text-left">Severity</th>
                <th className="px-4 py-2 text-left">Type</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Assigned</th>
                <th className="px-4 py-2 text-left">Created</th>
                <th className="px-4 py-2 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts().map((alert) => {
                const severity = mapSeverityFromScore(alert.score)
                const isCritical = severity === 'critical'
                return (
                  <tr key={alert.id} className={`${isCritical ? 'bg-red-600 text-white' : ''} hover:bg-white/2`}>
                    <td className="px-4 py-3">
                      <span className={severityClass(severity)}>{severity.toUpperCase()}</span>
                    </td>
                    <td className="px-4 py-3">{alert.type}</td>
                    <td className="px-4 py-3">{alert.status}</td>
                    <td className="px-4 py-3">{alert.assigned_to ?? 'Unassigned'}</td>
                    <td className="px-4 py-3">{alert.created_at ? new Date(alert.created_at).toLocaleString() : ''}</td>
                    <td className="px-4 py-3">
                      <button onClick={() => handleAssign(alert.id)} className="mr-2 rounded bg-white/6 px-3 py-1">Assign</button>
                      <button onClick={() => handleResolve(alert.id)} className="rounded bg-white/6 px-3 py-1">Resolve</button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
