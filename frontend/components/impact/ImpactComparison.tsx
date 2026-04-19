"use client"

import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts'

const DATA = [
  { name: 'Energy Theft', before: 48000, after: 6000 },
  { name: 'Transformer Loss', before: 32000, after: 7000 },
  { name: 'Metering Error', before: 12000, after: 2000 },
  { name: 'Unbilled Usage', before: 8000, after: 1500 },
]

export default function ImpactComparison() {
  const totalBefore = DATA.reduce((s, d) => s + d.before, 0)
  const totalAfter = DATA.reduce((s, d) => s + d.after, 0)
  const savings = totalBefore - totalAfter
  const pct = totalBefore > 0 ? Math.round((savings / totalBefore) * 100) : 0

  const formatCurrencyTick = (value: number | string) => {
    const numeric = typeof value === 'number' ? value : Number(value ?? 0)
    return `$${(numeric / 1000).toFixed(0)}k`
  }

  const formatTooltipValue = (value: number | string | ReadonlyArray<number | string> | undefined) => {
    const raw = Array.isArray(value) ? value[0] : value
    const numeric = typeof raw === 'number' ? raw : Number(raw ?? 0)
    return [`$${numeric.toLocaleString()}`, 'Loss (USD)'] as [string, string]
  }

  return (
    <div className="card">
      <h3 className="font-medium mb-2">Estimated Losses — Before vs After Detection</h3>
      <p className="text-sm text-[var(--muted)] mb-3">Mocked estimates for demo purposes — values are realistic but simulated.</p>

      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={DATA} margin={{ top: 8, right: 16, left: 0, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" opacity={0.06} />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={formatCurrencyTick} />
            <Tooltip formatter={formatTooltipValue} />
            <Legend />
            <Bar dataKey="before" name="Losses — Before Detection" fill="#ef4444" />
            <Bar dataKey="after" name="Losses — After Detection" fill="#34d399" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div>
          <div className="text-sm text-[var(--muted)]">Total (monthly)</div>
          <div className="text-lg font-semibold">${totalBefore.toLocaleString()}</div>
          <div className="text-sm text-[var(--muted)] mt-1">After detection: ${totalAfter.toLocaleString()} • Savings: ${savings.toLocaleString()} ({pct}%)</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-[var(--muted)]">Ops note</div>
          <div className="text-sm">Estimates based on demo data; operational tuning will refine these numbers.</div>
        </div>
      </div>
    </div>
  )
}
