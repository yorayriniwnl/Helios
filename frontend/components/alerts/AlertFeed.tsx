"use client"

import React, { useEffect, useState } from 'react'
import { get } from '../../lib/api'
import Spinner from '../ui/Spinner'
import ErrorMessage from '../ui/ErrorMessage'
import EvidenceUploader from './EvidenceUploader'
import connectWebSocket, { addWebSocketListener, removeWebSocketListener } from '../../lib/websocket'

type Severity = 'low' | 'medium' | 'high' | 'critical'

type AlertItem = {
  id: number
  message: string
  severity: Severity
  timestamp: string
  root_cause?: string
  confidence?: number
  recommended_action?: string
  est_recovery_minutes?: number
  est_recovery_value_usd?: number
  priority_score?: number
  components?: Record<string, number>
}

const mockAlerts: AlertItem[] = [
  { id: 1, message: 'Voltage spike detected on Meter 12', severity: 'high', timestamp: new Date().toISOString() },
  { id: 2, message: 'Frequent disconnects on Meter 7', severity: 'medium', timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString() },
  { id: 3, message: 'Tamper detected on Meter 3', severity: 'critical', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString() },
  { id: 4, message: 'Scheduled maintenance completed', severity: 'low', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() },
]

function severityClass(s: Severity) {
  switch (s) {
    case 'critical':
      return 'bg-red-600 text-white'
    case 'high':
      return 'bg-red-500 text-white'
    case 'medium':
      return 'bg-yellow-400 text-black'
    case 'low':
    default:
      return 'bg-green-400 text-black'
  }
}

function mapSeverityFromScore(score?: number): Severity {
  if (score == null) return 'medium'
  if (score >= 0.8) return 'critical'
  if (score >= 0.66) return 'high'
  if (score >= 0.33) return 'medium'
  return 'low'
}

function severityLabel(s: Severity) {
  switch (s) {
    case 'critical':
      return 'IMMEDIATE'
    case 'high':
      return 'PRIORITY'
    case 'medium':
      return 'REVIEW'
    case 'low':
    default:
      return 'MONITOR'
  }
}

function formatAlertMessage(a: any) {
  const raw = (a.explanation || a.type || `Alert ${a.id}`) as string
  const txt = raw.toLowerCase()
  const sev = mapSeverityFromScore(a.score)

  if (txt.includes('tamper') || txt.includes('tampering')) return 'Likely theft — schedule inspection'
  if (txt.includes('spike') || txt.includes('voltage') || txt.includes('overvoltage')) return 'Transformer stress — inspect equipment'
  if ((txt.includes('anomaly') || txt.includes('critical')) && (sev === 'high' || sev === 'critical')) return 'High priority area — prioritize inspections'

  // Fall back to the original explanation
  return raw
}

export default function AlertFeed({ alerts }: { alerts?: AlertItem[] }) {
  const [list, setList] = useState<AlertItem[]>(alerts ?? mockAlerts)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [priorityView, setPriorityView] = useState(false)
  const [loadingPriority, setLoadingPriority] = useState(false)
  const [evidenceMap, setEvidenceMap] = useState<Record<number, any[]>>({})
  const [showEvidenceForm, setShowEvidenceForm] = useState<Record<number, boolean>>({})

  useEffect(() => {
    let mounted = true
    async function fetchAlerts() {
      setLoading(true)
      setError(null)
      try {
        const res = await get<any[]>('/alerts', undefined, { cacheMs: 10000 })
        if (!mounted) return
        const mapped = (res || []).map((a) => {
          const ts = a.created_at || a.timestamp || new Date().toISOString()
          const sev = mapSeverityFromScore(a.score)
          const msg = formatAlertMessage(a)
          const root = a.decision?.root_cause || a.root_cause || null
          const conf = a.confidence != null ? Number(a.confidence) : (a.decision && a.decision.confidence ? Number(a.decision.confidence) : undefined)
          const rec = a.decision?.recommended_action?.title || a.recommended_action || undefined
          const estMin = a.decision?.estimated_recovery_minutes || a.est_recovery_minutes || undefined
          const estVal = a.decision?.estimated_recovery_value_usd || a.est_recovery_value_usd || undefined
          return { id: a.id, message: msg, severity: sev as Severity, timestamp: ts, root_cause: root, confidence: conf, recommended_action: rec, est_recovery_minutes: estMin, est_recovery_value_usd: estVal }
        })
        // sort newest first
        mapped.sort((x, y) => new Date(y.timestamp).getTime() - new Date(x.timestamp).getTime())
        setList(mapped.length ? mapped : mockAlerts)
      } catch (err: any) {
        if (!mounted) return
        setError(err?.response?.data?.detail || err?.message || 'Failed to load alerts')
        setList(alerts ?? mockAlerts)
      } finally {
        if (mounted) setLoading(false)
      }
    }

    async function fetchPriority() {
      setLoadingPriority(true)
      setError(null)
      try {
        const res = await get<any[]>('/alerts/priority', undefined, { cacheMs: 10000 })
        if (!mounted) return
        const mapped = (res || []).map((a) => {
          const ts = a.created_at || new Date().toISOString()
          const sev = mapSeverityFromScore(a.score)
          const msg = formatAlertMessage(a)
          return {
            id: a.id,
            message: msg,
            severity: sev as Severity,
            timestamp: ts,
            priority_score: a.priority_score,
            components: a.components,
          }
        })
        mapped.sort((x, y) => new Date(y.timestamp).getTime() - new Date(x.timestamp).getTime())
        setList(mapped.length ? mapped : mockAlerts)
      } catch (err: any) {
        if (!mounted) return
        setError(err?.response?.data?.detail || err?.message || 'Failed to load priority alerts')
      } finally {
        if (mounted) setLoadingPriority(false)
      }
    }

    fetchAlerts()
    try {
      connectWebSocket()
    } catch (e) {
      // ignore
    }
    return () => {
      mounted = false
    }
  }, [alerts])

  return (
    <div className="card">
      <h3 className="text-lg font-medium mb-3">Action Queue</h3>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium">Action Queue</h3>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    // toggle priority view and fetch prioritized alerts when enabling
                    const next = !priorityView
                    setPriorityView(next)
                    if (next) {
                      setLoadingPriority(true)
                      get<any[]>('/alerts/priority', undefined, { cacheMs: 10000 })
                        .then((res) => {
                          const mapped = (res || []).map((a) => {
                            const ts = a.created_at || new Date().toISOString()
                            const sev = mapSeverityFromScore(a.score)
                            const msg = formatAlertMessage(a)
                            return {
                              id: a.id,
                              message: msg,
                              severity: sev as Severity,
                              timestamp: ts,
                              priority_score: a.priority_score,
                              components: a.components,
                            }
                          })
                          mapped.sort((x, y) => new Date(y.timestamp).getTime() - new Date(x.timestamp).getTime())
                          setList(mapped.length ? mapped : mockAlerts)
                        })
                        .catch((err) => setError(err?.message || 'Failed to load priority alerts'))
                        .finally(() => setLoadingPriority(false))
                    } else {
                      // refresh normal alerts
                      setLoading(true)
                      get<any[]>('/alerts', undefined, { cacheMs: 10000 })
                        .then((res) => {
                          const mapped = (res || []).map((a) => {
                            const ts = a.created_at || a.timestamp || new Date().toISOString()
                            const sev = mapSeverityFromScore(a.score)
                            const msg = formatAlertMessage(a)
                            const root = a.decision?.root_cause || a.root_cause || null
                            const conf = a.confidence != null ? Number(a.confidence) : (a.decision && a.decision.confidence ? Number(a.decision.confidence) : undefined)
                            const rec = a.decision?.recommended_action?.title || a.recommended_action || undefined
                            const estMin = a.decision?.estimated_recovery_minutes || a.est_recovery_minutes || undefined
                            const estVal = a.decision?.estimated_recovery_value_usd || a.est_recovery_value_usd || undefined
                            return { id: a.id, message: msg, severity: sev as Severity, timestamp: ts, root_cause: root, confidence: conf, recommended_action: rec, est_recovery_minutes: estMin, est_recovery_value_usd: estVal }
                          })
                          mapped.sort((x, y) => new Date(y.timestamp).getTime() - new Date(x.timestamp).getTime())
                          setList(mapped.length ? mapped : mockAlerts)
                        })
                        .catch((err) => setError(err?.message || 'Failed to load alerts'))
                        .finally(() => setLoading(false))
                    }
                  }}
                  className={`px-3 py-1 rounded border text-sm ${priorityView ? 'bg-[rgba(255,255,255,0.04)]' : 'bg-transparent'}`}
                >
                  Priority view
                </button>
              </div>
            </div>
      {loading ? (
        <div className="py-6 flex justify-center"><Spinner /></div>
      ) : error ? (
        <div className="py-4"><ErrorMessage message={error} /></div>
      ) : (
        <ul className="space-y-3">
            {list.map((a) => (
            <li key={a.id} className="interactive-item flex items-start gap-3 p-3 rounded-md pop-in" style={{ background: 'transparent' }}>
              <span className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded ${severityClass(a.severity)} shadow-sm` }>
                {severityLabel(a.severity)}
              </span>
              <div className="flex-1">
                <div className="text-sm font-medium">{a.message}</div>
                <div className="text-xs text-[var(--muted)] mt-1">
                  {new Date(a.timestamp).toLocaleString()}
                  {a.root_cause ? <span className="ml-2">• Root cause: {a.root_cause}</span> : null}
                  {a.confidence != null ? <span className="ml-2">• Conf: {Math.round(a.confidence * 100)}%</span> : null}
                </div>
                  {a.priority_score != null && a.components ? (
                    <div className="mt-2 text-xs text-[var(--muted)] flex items-center gap-3">
                      <div className="font-semibold">Priority: {Math.round((a.priority_score || 0) * 100)}</div>
                      <div className="flex items-center gap-2">
                        {Object.entries(a.components).map(([k, v]) => (
                          <div key={k} className="text-[10px] px-2 py-0.5 bg-[rgba(255,255,255,0.02)] rounded">
                            {k.replace(/_/g, ' ')}: {Math.round((v || 0) * 100)}%
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                {a.recommended_action ? (
                  <div className="text-xs text-[var(--muted)] mt-1">Recommended: <span className="font-medium text-sm">{a.recommended_action}</span>{a.est_recovery_minutes ? ` • est ${a.est_recovery_minutes}m (${a.est_recovery_value_usd ? `$${a.est_recovery_value_usd}` : ''})` : ''}</div>
                ) : null}
                <div className="mt-2 flex items-center gap-2">
                  <button
                    onClick={() => {
                      const next = !(showEvidenceForm[a.id] === true)
                      setShowEvidenceForm({ ...showEvidenceForm, [a.id]: next })
                      // fetch evidence when opening
                      if (next && !(evidenceMap[a.id] && evidenceMap[a.id].length)) {
                        get<any[]>(`/alerts/${a.id}/evidence`).then((res) => setEvidenceMap({ ...evidenceMap, [a.id]: res || [] })).catch(() => {})
                      }
                    }}
                    className="text-xs px-2 py-1 rounded border bg-transparent"
                  >
                    Evidence
                  </button>
                </div>
                {showEvidenceForm[a.id] ? (
                  <div className="mt-2 p-2 border rounded bg-[rgba(255,255,255,0.01)]">
                    <EvidenceUploader alertId={a.id} onUploaded={(item: any) => {
                      setEvidenceMap({ ...evidenceMap, [a.id]: [item].concat(evidenceMap[a.id] || []) })
                      setShowEvidenceForm({ ...showEvidenceForm, [a.id]: false })
                    }} />
                    <div className="mt-2">
                      {(evidenceMap[a.id] || []).map((ev: any) => (
                        <div key={ev.id} className="text-xs text-[var(--muted)] mt-1">
                          {ev.before_after ? <strong className="mr-2">[{ev.before_after}]</strong> : null}
                          <a href={ev.file_url} target="_blank" rel="noreferrer" className="underline">{ev.original_filename || `evidence-${ev.id}`}</a>
                          {ev.notes ? <span className="ml-2">• {ev.notes}</span> : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
