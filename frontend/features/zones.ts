/**
 * features/zones — zone display helpers and formatting utilities.
 *
 * Keeps zone-specific logic out of components so it can be shared and tested.
 */

import type { ZoneOverview } from '../types/api'

// ─── Risk level helpers ──────────────────────────────────────────────────────

export type ZoneRisk = 'low' | 'medium' | 'high'

export function zoneRiskColor(risk: string): string {
  switch (risk) {
    case 'high':   return 'text-red-400'
    case 'medium': return 'text-yellow-400'
    case 'low':    return 'text-green-400'
    default:       return 'text-gray-400'
  }
}

export function zoneRiskBadge(risk: string): string {
  switch (risk) {
    case 'high':   return 'bg-red-500/20 text-red-300 border border-red-500/30'
    case 'medium': return 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30'
    case 'low':    return 'bg-green-500/20 text-green-300 border border-green-500/30'
    default:       return 'bg-gray-500/20 text-gray-300'
  }
}

export function zoneRiskFromDensity(density: number): ZoneRisk {
  if (density >= 2) return 'high'
  if (density >= 0.5) return 'medium'
  return 'low'
}

// ─── Anomaly density color (for heatmap overlays) ────────────────────────────

export function densityHexColor(density: number): string {
  const t = Math.max(0, Math.min(1, density / 3))
  if (t >= 0.8) return '#ef4444'   // red
  if (t >= 0.6) return '#fb7185'   // rose
  if (t >= 0.4) return '#f97316'   // orange
  if (t >= 0.2) return '#f59e0b'   // amber
  return '#34d399'                  // green
}

// ─── Loss percentage formatting ──────────────────────────────────────────────

export function formatLossPct(pct?: number | null): string {
  if (pct == null || isNaN(pct)) return '—'
  return `${(pct * 100).toFixed(1)}%`
}

// ─── Sorting ─────────────────────────────────────────────────────────────────

const RISK_ORDER: Record<string, number> = { high: 3, medium: 2, low: 1 }

export function sortZonesByRisk(zones: ZoneOverview[]): ZoneOverview[] {
  return [...zones].sort((a, b) => {
    const bRisk = b.risk ?? 'low'
    const aRisk = a.risk ?? 'low'
    const rDiff = (RISK_ORDER[bRisk] ?? 0) - (RISK_ORDER[aRisk] ?? 0)
    if (rDiff !== 0) return rDiff
    return (b.alert_count ?? 0) - (a.alert_count ?? 0)
  })
}

// ─── Heatmap point generation ────────────────────────────────────────────────

export interface HeatPoint {
  lat: number
  lng: number
  intensity: number
  zoneId: number
  zoneName: string
}

/**
 * Convert a ZoneOverview list into heatmap intensity points.
 * Requires the zone to have a lat/lng centre; falls back to a grid layout
 * centred on San Francisco if coordinates aren't stored.
 */
export function zonesToHeatPoints(
  zones: ZoneOverview[],
  centres?: Record<number, { lat: number; lng: number }>
): HeatPoint[] {
  return zones.map((z, i) => {
    const centre = centres?.[z.id]
    // Fallback grid: spread zones in a small area
    const lat = centre?.lat ?? 37.75 + (i % 3) * 0.03
    const lng = centre?.lng ?? -122.44 + Math.floor(i / 3) * 0.04
    const intensity = Math.min(1, (z.anomaly_density ?? 0) / 3)
    return { lat, lng, intensity, zoneId: z.id, zoneName: z.name }
  })
}
