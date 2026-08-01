"use client"

import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const sampleData = [
  { name: '00:00', value: 100 },
  { name: '04:00', value: 120 },
  { name: '08:00', value: 180 },
  { name: '12:00', value: 220 },
  { name: '16:00', value: 190 },
  { name: '20:00', value: 140 },
  { name: '24:00', value: 110 },
]

export default function SimpleChart({ data = sampleData }: { data?: Array<Record<string, any>> }) {
  return (
    <div className="card">
      <h3 className="text-lg font-medium mb-2">Power (sample)</h3>
      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
            <XAxis dataKey="name" stroke="var(--muted)" />
            <YAxis stroke="var(--muted)" />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
