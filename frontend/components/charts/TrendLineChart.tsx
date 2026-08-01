"use client"

import React, { useId } from 'react'
import EmptyState from '../ui/EmptyState'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
} from 'recharts'

type TrendLineChartProps = {
  data: Array<Record<string, any>>
  xKey?: string
  yKey?: string
  height?: number
  color?: string
  strokeWidth?: number
  showGrid?: boolean
  className?: string
}

export default function TrendLineChart({
  data,
  xKey = 'name',
  yKey = 'value',
  height = 220,
  color = 'var(--accent)',
  strokeWidth = 2,
  showGrid = true,
  className = '',
}: TrendLineChartProps) {
  const gradientId = useId().replace(/:/g, '')

  if (!data || (Array.isArray(data) && data.length === 0)) {
    return (
      <div className={`card ${className}`}>
        <EmptyState title="No data" description="No trend data available." />
      </div>
    )
  }

  return (
    <div className={`card ${className}`}>
      <div style={{ width: '100%', height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.18} />
                <stop offset="100%" stopColor={color} stopOpacity={0.02} />
              </linearGradient>
            </defs>

            {showGrid && <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />}
            <XAxis dataKey={xKey} stroke="var(--muted)" tick={{ fontSize: 12 }} />
            <YAxis stroke="var(--muted)" tick={{ fontSize: 12 }} />
            <Tooltip wrapperStyle={{ background: 'rgba(0,0,0,0.7)', borderRadius: 6 }} contentStyle={{ border: 'none' }} />

            <Area
              type="monotone"
              dataKey={yKey}
              stroke="none"
              fill={`url(#${gradientId})`}
              isAnimationActive={true}
              animationDuration={900}
            />

            <Line
              type="monotone"
              dataKey={yKey}
              stroke={color}
              strokeWidth={strokeWidth}
              dot={false}
              activeDot={{ r: 5 }}
              isAnimationActive={true}
              animationDuration={900}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
