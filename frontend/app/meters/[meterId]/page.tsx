"use client"

import React, { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { get } from '../../../lib/api'
import ConsumptionChart from '../../../components/charts/ConsumptionChart'
import Spinner from '../../../components/ui/Spinner'
import ErrorMessage from '../../../components/ui/ErrorMessage'

type Meter = {
  id: number
  meter_number: string
  household_name?: string
  status: string
}

type Anomaly = {
  id: number
  type: string
  score?: number
  explanation?: string
  created_at?: string
  severity?: string
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

export default function MeterDetailPage() {
  const params = useParams() as any
  const router = useRouter()
  const meterId = Number(params?.meterId)

  const [meter, setMeter] = useState<Meter | null>(null)
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [m, an] = await Promise.all([
          get(`/meters/${meterId}`).catch(() => null),
          get<any[]>(`/anomalies?meter_id=${meterId}`).catch(() => []),
        ])
        if (!mounted) return
        setMeter(m)
        setAnomalies((an || []).map((a) => ({ ...a, severity: a.severity ?? mapSeverityFromScore(a.score) })))
      } catch (err: any) {
        if (!mounted) return
        setError(err?.message || 'Failed to load meter')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    if (meterId) load()
    return () => {
      mounted = false
    }
  }, [meterId])

  if (!meterId) {
    return <div className="container mx-auto py-8">Invalid meter</div>
  }

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/40" onClick={() => router.back()} />

      <div className="absolute right-0 top-0 h-full w-full md:w-2/3 lg:w-1/2 bg-[var(--bg)] shadow-2xl transform transition-transform duration-300">
        <div className="p-4 border-b border-white/6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Meter {meter?.meter_number ?? meterId}</h2>
            <div className="text-sm text-[var(--muted)]">{meter?.household_name}</div>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => router.back()} className="px-3 py-1 rounded bg-white/6">Close</button>
          </div>
        </div>

        <div className="p-4 space-y-4 h-full overflow-auto">
          {loading ? (
            <div className="py-6 flex justify-center"><Spinner /></div>
          ) : error ? (
            <div className="py-4"><ErrorMessage message={error} /></div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <ConsumptionChart meterId={meterId} />
                </div>

                <div className="card">
                  <h3 className="font-medium">Details</h3>
                  <dl className="mt-3 text-sm text-[var(--muted)] space-y-2">
                    <div>
                      <dt className="font-medium">Status</dt>
                      <dd>{meter?.status}</dd>
                    </div>
                    <div>
                      <dt className="font-medium">Household</dt>
                      <dd>{meter?.household_name ?? '—'}</dd>
                    </div>
                    <div>
                      <dt className="font-medium">Meter Number</dt>
                      <dd>{meter?.meter_number}</dd>
                    </div>
                  </dl>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Issue History</h3>
                <div className="card">
                  {anomalies.length === 0 ? (
                    <div className="p-6 text-sm text-[var(--muted)]">No current issues detected — continue monitoring.</div>
                  ) : (
                    <ul className="space-y-2">
                      {anomalies.map((a) => (
                        <li key={a.id} className="flex items-start justify-between gap-4 p-3 rounded-md hover:bg-white/2">
                          <div>
                            <div className="font-medium">{a.type}</div>
                            {a.explanation && <div className="text-xs text-[var(--muted)] mt-1">{a.explanation}</div>}
                            <div className="text-xs text-[var(--muted)] mt-1">{a.created_at ? new Date(a.created_at).toLocaleString() : ''}</div>
                          </div>

                          <div className="text-right">
                            <div className={severityClass(a.severity || mapSeverityFromScore(a.score))}>{(a.severity || mapSeverityFromScore(a.score)).toUpperCase()}</div>
                            {typeof a.score === 'number' && <div className="text-xs text-[var(--muted)] mt-2">Score: {a.score}</div>}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
