"use client"

import React, { useMemo } from 'react'
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import { useDashboard, useAlerts, useZones } from '../../../hooks'
import Skeleton from '../../../components/ui/Skeleton'
import ErrorMessage from '../../../components/ui/ErrorMessage'
import EmptyState from '../../../components/ui/EmptyState'
import { severityFromScore } from '../../../features/alerts'
import { sortZonesByRisk } from '../../../features/zones'

const CHART_COLORS = { low: '#34d399', medium: '#f59e0b', high: '#fb7185', critical: '#ef4444' }

export default function AnalyticsPage() {
  const { summary, recovery, loading: loadingDash, error: errorDash } = useDashboard()
  const { alerts, loading: loadingAlerts } = useAlerts({ limit: 200 })
  const { zones, loading: loadingZones } = useZones()

  // ── 14-day alert trend ───────────────────────────────────────────────────
  const trendData = useMemo(() => {
    const now = new Date()
    return Array.from({ length: 14 }).map((_, i) => {
      const d = new Date(now)
      d.setDate(now.getDate() - (13 - i))
      const label = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
      const counts = { low: 0, medium: 0, high: 0, critical: 0 }
      alerts.forEach((a) => {
        const ts = a.created_at ? new Date(a.created_at) : new Date()
        if (ts.toDateString() !== d.toDateString()) return
        const sev = a.severity ?? severityFromScore(a.score)
        counts[sev as keyof typeof counts] = (counts[sev as keyof typeof counts] ?? 0) + 1
      })
      return { name: label, ...counts, total: counts.low + counts.medium + counts.high + counts.critical }
    })
  }, [alerts])

  // ── Zone risk distribution ────────────────────────────────────────────────
  const zoneData = useMemo(() =>
    sortZonesByRisk(zones as any[]).map((z: any) => ({
      name: z.name,
      alerts: z.alert_count ?? 0,
      anomalies: z.anomaly_count ?? 0,
      meters: z.meter_count ?? 0,
    })),
    [zones]
  )

  const isLoading = loadingDash || loadingAlerts || loadingZones
  const error = errorDash

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--fg)' }}>Analytics</h1>
        <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>
          Trends, recovery metrics and zone performance
        </p>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Recovery KPIs */}
      {(isLoading ? Array(4).fill(null) : [
        { label: 'Recovered Value',      value: recovery ? `₹${recovery.total_recovered_value.toLocaleString()}` : '—', sub: `last ${recovery?.window_days ?? 30}d` },
        { label: 'Success Rate',         value: recovery ? `${Math.round(recovery.success_rate * 100)}%` : '—', sub: 'resolved / total' },
        { label: 'Avg Close Time',       value: recovery ? `${recovery.avg_time_to_close_minutes.toFixed(0)}m` : '—', sub: 'mean resolution' },
        { label: 'Inspector Efficiency', value: recovery ? `${recovery.inspector_stats.length} active` : '—', sub: 'agents on record' },
      ]).map((k, i) => (
        <div key={i} style={{ display: i === 0 ? 'contents' : 'none' }}>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {(isLoading ? Array(4).fill(null) : [
              { label: 'Recovered Value',      value: recovery ? `₹${recovery.total_recovered_value.toLocaleString()}` : '—', sub: `last ${recovery?.window_days ?? 30}d` },
              { label: 'Success Rate',         value: recovery ? `${Math.round(recovery.success_rate * 100)}%` : '—', sub: 'resolved / total' },
              { label: 'Avg Close Time',       value: recovery ? `${recovery.avg_time_to_close_minutes.toFixed(0)}m` : '—', sub: 'mean resolution' },
              { label: 'Inspector Efficiency', value: recovery ? `${recovery.inspector_stats.length} active` : '—', sub: 'agents on record' },
            ]).map((card: any, j: number) => (
              <div key={j} className="rounded-xl p-4" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
                {isLoading ? <Skeleton height={32} /> : (
                  <div className="text-xl font-bold animate-count-up" style={{ color: 'var(--accent)' }}>{card.value}</div>
                )}
                {isLoading ? <Skeleton height={12} width="60%" className="mt-2" /> : (
                  <>
                    <div className="text-xs mt-1 font-medium">{card.label}</div>
                    <div className="text-xs mt-0.5" style={{ color: 'var(--muted)' }}>{card.sub}</div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )).slice(0, 1)}

      {/* 14-day alert trend */}
      <div className="rounded-xl p-4" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
        <h2 className="font-semibold text-sm mb-4">Alert Trend — 14 Days</h2>
        {loadingAlerts ? <Skeleton height={220} /> : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={trendData} margin={{ top: 4, right: 8, bottom: 4, left: -8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
              <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
              {(['low', 'medium', 'high', 'critical'] as const).map((sev) => (
                <Bar key={sev} dataKey={sev} stackId="a" fill={CHART_COLORS[sev]} radius={sev === 'critical' ? [3, 3, 0, 0] : [0, 0, 0, 0]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Alert trend line */}
      <div className="rounded-xl p-4" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
        <h2 className="font-semibold text-sm mb-4">Total Alerts per Day</h2>
        {loadingAlerts ? <Skeleton height={180} /> : (
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={trendData} margin={{ top: 4, right: 8, bottom: 4, left: -8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
              <Line type="monotone" dataKey="total" stroke="var(--accent)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Zone performance */}
      <div className="rounded-xl p-4" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
        <h2 className="font-semibold text-sm mb-4">Zone Alert & Anomaly Counts</h2>
        {loadingZones ? <Skeleton height={200} /> : zoneData.length === 0 ? <EmptyState message="No zone data." /> : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={zoneData} layout="vertical" margin={{ top: 4, right: 8, bottom: 4, left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis type="number" tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: 'var(--muted)' }} tickLine={false} width={68} />
              <Tooltip contentStyle={{ background: '#0b1220', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} />
              <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="alerts"    fill="#fb7185" radius={[0, 3, 3, 0]} name="Alerts" />
              <Bar dataKey="anomalies" fill="#f59e0b" radius={[0, 3, 3, 0]} name="Anomalies" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Inspector stats */}
      {recovery && recovery.inspector_stats.length > 0 && (
        <div className="rounded-xl overflow-hidden" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
          <div className="px-4 py-3 border-b border-white/6">
            <h2 className="font-semibold text-sm">Inspector Performance</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider border-b border-white/4" style={{ color: 'var(--muted)' }}>
                  {['Inspector', 'Assigned', 'Resolved', 'Success Rate', 'Avg Close'].map(h => (
                    <th key={h} className="px-4 py-2 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recovery.inspector_stats.map((u) => (
                  <tr key={u.user_id} className="border-t border-white/4 hover:bg-white/3">
                    <td className="px-4 py-2 font-medium">{u.name}</td>
                    <td className="px-4 py-2">{u.assigned}</td>
                    <td className="px-4 py-2">{u.resolved}</td>
                    <td className="px-4 py-2">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-1.5 rounded-full bg-white/10 max-w-[80px]">
                          <div className="h-full rounded-full bg-green-400" style={{ width: `${Math.round(u.success_rate * 100)}%` }} />
                        </div>
                        <span>{Math.round(u.success_rate * 100)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-2" style={{ color: 'var(--muted)' }}>{u.avg_time_to_close_minutes.toFixed(0)}m</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Zone recovery breakdown */}
      {recovery && recovery.zone_recovery.length > 0 && (
        <div className="rounded-xl overflow-hidden" style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}>
          <div className="px-4 py-3 border-b border-white/6">
            <h2 className="font-semibold text-sm">Recovered Value by Zone</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wider border-b border-white/4" style={{ color: 'var(--muted)' }}>
                  {['Zone', 'Recovered (₹)'].map(h => <th key={h} className="px-4 py-2 font-medium">{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {[...recovery.zone_recovery].sort((a, b) => b.recovered_value - a.recovered_value).map((z) => (
                  <tr key={z.zone_id} className="border-t border-white/4 hover:bg-white/3">
                    <td className="px-4 py-2 font-medium">{z.zone_name}</td>
                    <td className="px-4 py-2" style={{ color: 'var(--accent)' }}>₹{z.recovered_value.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
