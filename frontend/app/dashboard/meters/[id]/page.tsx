"use client"

import React from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { useReadings, useAnomalies } from '../../../../hooks'
import { useMeters } from '../../../../hooks'
import Skeleton from '../../../../components/ui/Skeleton'
import ErrorMessage from '../../../../components/ui/ErrorMessage'
import EmptyState from '../../../../components/ui/EmptyState'
import { severityBadgeClass, severityFromScore, formatAlertType, alertAge } from '../../../../features/alerts'

const ConsumptionChart = dynamic(() => import('../../../../components/charts/ConsumptionChart'), { ssr: false })

export default function MeterDetailPage() {
  const params = useParams() as { id?: string }
  const meterId = params?.id ? Number(params.id) : null

  const { fetchMeter } = useMeters()
  const [meter, setMeter] = React.useState<any>(null)
  const [meterLoading, setMeterLoading] = React.useState(true)

  React.useEffect(() => {
    if (meterId == null) return
    setMeterLoading(true)
    fetchMeter(meterId).then((m) => {
      setMeter(m)
      setMeterLoading(false)
    })
  }, [meterId, fetchMeter])

  const { readings, loading: readingsLoading } = useReadings({ meterId, limit: 96 })
  const { anomalies, loading: anomaliesLoading } = useAnomalies({ meterId, limit: 50 })

  // Format readings for consumption chart
  const chartData = [...readings]
    .reverse()
    .map((r) => ({
      time: r.timestamp ? new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—',
      power: r.power_consumption ?? 0,
      voltage: r.voltage ?? 0,
    }))

  if (!params?.id) {
    return <ErrorMessage message="No meter ID specified." />
  }

  return (
    <div className="space-y-6">
      {/* Back nav */}
      <Link
        href="/dashboard/meters"
        className="inline-flex items-center gap-1.5 text-sm transition-colors hover:opacity-80"
        style={{ color: 'var(--muted)' }}
      >
        ← Back to Meters
      </Link>

      {/* Meter header */}
      <div
        className="rounded-xl p-5"
        style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
      >
        {meterLoading ? (
          <div className="space-y-2">
            <Skeleton height={28} width="40%" />
            <Skeleton height={16} width="30%" />
          </div>
        ) : meter ? (
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="text-xl font-bold">{meter.meter_number}</h1>
              <p className="text-sm mt-1" style={{ color: 'var(--muted)' }}>
                {meter.household_name ?? 'Unknown Household'}
                {meter.zone_id ? ` · Zone ${meter.zone_id}` : ''}
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-lg text-xs font-bold ${
                meter.status === 'active'
                  ? 'bg-green-500/20 text-green-300'
                  : 'bg-gray-500/20 text-gray-400'
              }`}
            >
              {meter.status?.toUpperCase() ?? 'UNKNOWN'}
            </span>
          </div>
        ) : (
          <ErrorMessage message={`Meter #${params.id} not found.`} />
        )}
      </div>

      {/* Latest reading KPIs */}
      {readings.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Power (W)',   value: readings[0]?.power_consumption?.toFixed(1) ?? '—' },
            { label: 'Voltage (V)', value: readings[0]?.voltage?.toFixed(1) ?? '—' },
            { label: 'Current (A)', value: readings[0]?.current?.toFixed(3) ?? '—' },
          ].map((k) => (
            <div
              key={k.label}
              className="rounded-xl p-4"
              style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
            >
              <div className="text-xl font-bold" style={{ color: 'var(--accent)' }}>{k.value}</div>
              <div className="text-xs mt-1" style={{ color: 'var(--muted)' }}>{k.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Consumption chart */}
      <div
        className="rounded-xl p-4"
        style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
      >
        <h2 className="font-semibold text-sm mb-4">Power Consumption (last 48h)</h2>
        {readingsLoading ? (
          <Skeleton height={200} />
        ) : chartData.length === 0 ? (
          <EmptyState message="No readings yet." />
        ) : (
          <ConsumptionChart data={chartData} />
        )}
      </div>

      {/* Anomaly events */}
      <div
        className="rounded-xl overflow-hidden"
        style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }}
      >
        <div className="px-4 py-3 border-b border-white/6">
          <h2 className="font-semibold text-sm">Anomaly Events</h2>
        </div>
        {anomaliesLoading ? (
          <div className="p-4 space-y-2">
            {[...Array(3)].map((_, i) => <Skeleton key={i} height={36} />)}
          </div>
        ) : anomalies.length === 0 ? (
          <EmptyState message="No anomalies detected for this meter." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr
                  className="text-left text-xs uppercase tracking-wider border-b border-white/4"
                  style={{ color: 'var(--muted)' }}
                >
                  {['Type', 'Severity', 'Score', 'When', 'Explanation'].map((h) => (
                    <th key={h} className="px-4 py-2 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {anomalies.map((a) => {
                  const sev = severityFromScore(a.score)
                  return (
                    <tr key={a.id} className="border-t border-white/4 hover:bg-white/3">
                      <td className="px-4 py-2 font-medium">{formatAlertType(a.type)}</td>
                      <td className="px-4 py-2">
                        <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${severityBadgeClass(sev)}`}>
                          {sev.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-2 font-mono text-xs" style={{ color: 'var(--muted)' }}>
                        {a.score?.toFixed(3) ?? '—'}
                      </td>
                      <td className="px-4 py-2 text-xs" style={{ color: 'var(--muted)' }}>
                        {alertAge(a.created_at)}
                      </td>
                      <td className="px-4 py-2 text-xs max-w-[280px] truncate" style={{ color: 'var(--muted)' }}>
                        {a.explanation ?? '—'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
