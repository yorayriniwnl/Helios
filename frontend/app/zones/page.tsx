"use client"

import React from 'react'
import ZoneHeatmap from '../../components/zones/ZoneHeatmap'

export default function ZonesPage() {
  return (
    <div className="container mx-auto">
      <h1 className="mb-4 text-3xl font-bold">Zone Intelligence</h1>
      <p className="mb-4 text-sm text-[var(--muted)]">Heatmap showing prioritized zones - click a zone to view recommended actions and schedule inspections.</p>

      <ZoneHeatmap />
    </div>
  )
}
