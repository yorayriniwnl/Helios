"use client"

import React, { useEffect, useState } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

type SeverityBarChartProps = {
  data: Array<Record<string, any>>
  xKey?: string
  categories?: string[]
  colors?: string[]
  height?: number
  stacked?: boolean
  className?: string
}

export default function SeverityBarChart({
  data,
  xKey = 'name',
  categories = ['low', 'medium', 'high'],
  colors = ['#34d399', '#f59e0b', '#fb7185'],
  height = 220,
  stacked = true,
  className = '',
}: SeverityBarChartProps) {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  return (
    <div className={`card ${className}`}>
      <div style={{ width: '100%', height }}>
        {isMounted ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
              <XAxis dataKey={xKey} stroke="var(--muted)" tick={{ fontSize: 12 }} />
              <YAxis stroke="var(--muted)" tick={{ fontSize: 12 }} />
              <Tooltip wrapperStyle={{ background: 'rgba(0,0,0,0.8)', borderRadius: 6 }} />
              <Legend />

              {categories.map((cat, idx) => (
                <Bar
                  key={cat}
                  dataKey={cat}
                  stackId={stacked ? 'a' : undefined}
                  fill={colors[idx] ?? colors[idx % colors.length]}
                  isAnimationActive={true}
                  animationDuration={700}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : null}
      </div>
    </div>
  )
}
