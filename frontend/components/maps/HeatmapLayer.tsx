"use client"

import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'

type Point = [number, number, number]

interface HeatmapLayerProps {
  points?: Point[]
  radius?: number
  blur?: number
  max?: number
}

export default function HeatmapLayer({ points = [], radius = 25, blur = 15, max = 1 }: HeatmapLayerProps) {
  const map = useMap()

  useEffect(() => {
    if (!map || !points || !points.length) return
    const heat = (L as any).heatLayer(points, { radius, blur, maxZoom: 18, max })
    heat.addTo(map)
    return () => {
      try {
        map.removeLayer(heat)
      } catch (e) {
        // ignore
      }
    }
  }, [map, points, radius, blur, max])

  return null
}
