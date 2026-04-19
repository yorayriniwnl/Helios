"use client"

import React, { useMemo, useState, useCallback } from 'react'
import { MapContainer, TileLayer, Polygon, CircleMarker, Popup } from 'react-leaflet'
import HeatmapLayer from './HeatmapLayer'

type Zone = { id: number; name: string; polygon: [number, number][]; anomaly_density?: number }
type Hotspot = { id: number; name: string; lat: number; lng: number; severity?: number }

function densityColor(v: number) {
  const t = Math.max(0, Math.min(1, v))
  if (t >= 0.8) return '#ef4444'
  if (t >= 0.66) return '#fb7185'
  if (t >= 0.33) return '#f59e0b'
  return '#34d399'
}

export default function MapLayer() {
  const center = [37.7749, -122.4194] as [number, number]

  const zones: Zone[] = useMemo(() => [
    { id: 1, name: 'Downtown', polygon: [[37.789, -122.405], [37.781, -122.403], [37.776, -122.412], [37.783, -122.421]] , anomaly_density: 0.6 },
    { id: 2, name: 'Mission', polygon: [[37.759, -122.423], [37.754, -122.418], [37.748, -122.424], [37.753, -122.430]] , anomaly_density: 0.3 },
    { id: 3, name: 'Sunset', polygon: [[37.763, -122.486], [37.757, -122.478], [37.750, -122.482], [37.758, -122.489]] , anomaly_density: 0.85 },
  ], [])

  const hotspots: Hotspot[] = useMemo(() => [
    { id: 1, name: 'Cluster A', lat: 37.778, lng: -122.415, severity: 0.75 },
    { id: 2, name: 'Cluster B', lat: 37.752, lng: -122.427, severity: 0.45 },
    { id: 3, name: 'Cluster C', lat: 37.756, lng: -122.483, severity: 0.92 },
  ], [])

  const heatPoints = useMemo(() => {
    const pts: [number, number, number][] = []
    hotspots.forEach((h) => pts.push([h.lat, h.lng, h.severity ?? 0.5]))
    zones.forEach((z) => {
      const coords = z.polygon
      if (!coords || !coords.length) return
      let latSum = 0
      let lngSum = 0
      coords.forEach(([lat, lng]) => {
        latSum += lat
        lngSum += lng
      })
      const centroidLat = latSum / coords.length
      const centroidLng = lngSum / coords.length
      pts.push([centroidLat, centroidLng, z.anomaly_density ?? 0])
    })
    return pts
  }, [hotspots, zones])

  const [selectedZone, setSelectedZone] = useState<Zone | null>(null)
  const [analytics, setAnalytics] = useState<{
    alerts_count: number
    risk_score: number
    top_alerts: Array<{ id: number; title: string; severity: number; created_at: string }>
  } | null>(null)

  const generateAnalyticsForZone = useCallback((z: Zone) => {
    const risk_score = Number(z.anomaly_density ?? 0)
    const alerts_count = Math.max(0, Math.round(risk_score * 24))
    const top_alerts = Array.from({ length: Math.min(5, Math.max(1, alerts_count)) }).map((_, i) => {
      const severity = Math.min(1, risk_score + i * 0.06)
      return {
        id: i + 1,
        title: `Anomaly ${i + 1}`,
        severity,
        created_at: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
      }
    })
    return { alerts_count, risk_score, top_alerts }
  }, [])

  const handleZoneClick = useCallback((z: Zone, _ev?: any) => {
    setSelectedZone(z)
    setAnalytics(generateAnalyticsForZone(z))
  }, [generateAnalyticsForZone])

  const closePanel = useCallback(() => {
    setSelectedZone(null)
    setAnalytics(null)
  }, [])

  return (
    <div className="relative">
      <MapContainer center={center} zoom={12} style={{ height: '360px', width: '100%' }}>
        <HeatmapLayer points={heatPoints} radius={35} blur={20} max={1} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {zones.map((z) => (
          <Polygon
            key={z.id}
            positions={z.polygon}
            pathOptions={{ color: densityColor(z.anomaly_density || 0), weight: 2, fillOpacity: 0.18 }}
            eventHandlers={{ click: (ev) => handleZoneClick(z, ev) }}
          />
        ))}
        {hotspots.map((h) => (
          <CircleMarker
            key={h.id}
            center={[h.lat, h.lng]}
            radius={6 + (h.severity || 0) * 8}
            pathOptions={{ color: densityColor(h.severity || 0), fillOpacity: 1 }}
          >
            <Popup>
              <div className="text-sm font-medium">{h.name}</div>
              <div className="text-xs text-[var(--muted)]">Severity: {(h.severity || 0).toFixed(2)}</div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {selectedZone && analytics && (
        <div className="absolute right-0 top-0 h-full panel z-50 overflow-auto p-4">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-semibold">{selectedZone.name}</h3>
              <div className="text-sm text-[var(--muted)]">Risk score: {(analytics.risk_score * 100).toFixed(0)}%</div>
            </div>
            <div>
              <button onClick={closePanel} className="px-2 py-1 rounded bg-white/6">Close</button>
            </div>
          </div>

          <div className="mb-3">
            <div className="text-sm text-[var(--muted)] mb-2">Alerts: {analytics.alerts_count}</div>
            <div className="space-y-2">
              {analytics.top_alerts.map((a) => (
                <div key={a.id} className="p-2 rounded bg-[rgba(255,255,255,0.02)] border border-white/6">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">{a.title}</div>
                    <div className={`text-xs font-semibold px-2 py-1 rounded ${a.severity >= 0.8 ? 'bg-red-500 text-white' : a.severity >= 0.66 ? 'bg-pink-400 text-black' : a.severity >= 0.33 ? 'bg-yellow-400 text-black' : 'bg-green-400 text-black'}`}>{(a.severity * 100).toFixed(0)}%</div>
                  </div>
                  <div className="text-xs text-[var(--muted)]">{new Date(a.created_at).toLocaleString()}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )

}
