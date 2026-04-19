"use client"

import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

type Props = { alert?: any; size?: number }

function mapSeverityFromScore(score?: number) {
  if (score == null) return 'medium'
  if (score >= 0.8) return 'critical'
  if (score >= 0.66) return 'high'
  if (score >= 0.33) return 'medium'
  return 'low'
}

function severityColor(s: string | undefined) {
  switch (s) {
    case 'critical':
      return '#ff6b6b'
    case 'high':
      return '#ff8a65'
    case 'medium':
      return '#f6c84c'
    case 'low':
    default:
      return '#34d399'
  }
}

function AvatarScene({ alert }: { alert?: any }) {
  const group = useRef<THREE.Group | null>(null)
  const head = useRef<THREE.Mesh | null>(null)
  const leftEye = useRef<THREE.Mesh | null>(null)
  const rightEye = useRef<THREE.Mesh | null>(null)
  const indicator = useRef<THREE.Mesh | null>(null)

  const baseColor = useMemo(() => {
    const score = alert?.score ?? alert?.decision?.confidence
    const sev = mapSeverityFromScore(typeof score === 'number' ? score : undefined)
    return severityColor(sev)
  }, [alert])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()

    // severity factor drives animation intensity
    const score = Number(alert?.score ?? alert?.decision?.confidence ?? 0.45)
    const factor = Math.max(0, Math.min(1, score))

    // gentle body bob
    const s = 1 + 0.03 * factor * Math.sin(t * 2 + 0.5)
    if (group.current) group.current.scale.set(s, s, s)

    // head subtle turn (more agitated for higher severity)
    if (head.current) head.current.rotation.y = Math.sin(t * (1 + factor * 2)) * 0.08 * (0.5 + factor * 0.8)

    // eyes glow and pulse
    if (leftEye.current && rightEye.current) {
      const glow = 0.4 + 0.6 * factor + 0.2 * Math.sin(t * 6)
      const col = new THREE.Color(baseColor)
      ;(leftEye.current.material as any).emissive = col
      ;(rightEye.current.material as any).emissive = col
      ;(leftEye.current.material as any).emissiveIntensity = glow
      ;(rightEye.current.material as any).emissiveIntensity = glow
    }

    // indicator pulse and color reflect status/severity
    if (indicator.current) {
      const p = 1 + 0.45 * factor * (0.7 + 0.3 * Math.sin(t * 5))
      indicator.current.scale.set(p, p, p)
      ;(indicator.current.material as any).color = new THREE.Color(baseColor)
      ;(indicator.current.material as any).emissive = new THREE.Color(baseColor)
      ;(indicator.current.material as any).emissiveIntensity = 0.6 + 0.8 * factor
    }
  })

  return (
    <group ref={group} position={[0, -0.12, 0]}>
      {/* body */}
      <mesh position={[0, -0.25, 0]}> 
        <cylinderGeometry args={[0.28, 0.34, 0.4, 12]} />
        <meshStandardMaterial color="#0b1220" metalness={0.2} roughness={0.6} />
      </mesh>

      {/* head */}
      <mesh ref={head} position={[0, 0.15, 0]}> 
        <sphereGeometry args={[0.22, 24, 24]} />
        <meshStandardMaterial color="#e6eef8" metalness={0.1} roughness={0.5} />
      </mesh>

      {/* eyes */}
      <mesh ref={leftEye} position={[-0.07, 0.18, 0.185]}> 
        <sphereGeometry args={[0.04, 12, 12]} />
        <meshStandardMaterial color="#000" emissive="#222" emissiveIntensity={0.4} />
      </mesh>
      <mesh ref={rightEye} position={[0.07, 0.18, 0.185]}> 
        <sphereGeometry args={[0.04, 12, 12]} />
        <meshStandardMaterial color="#000" emissive="#222" emissiveIntensity={0.4} />
      </mesh>

      {/* small status indicator above head */}
      <mesh ref={indicator} position={[0, 0.54, 0]}> 
        <sphereGeometry args={[0.07, 12, 12]} />
        <meshStandardMaterial color={baseColor} emissive={baseColor} emissiveIntensity={0.8} metalness={0.4} roughness={0.3} />
      </mesh>
    </group>
  )
}

export default function ThreeInspectorAvatar({ alert, size = 120 }: Props) {
  // Minimal DPR to keep small performance footprint
  const w = size
  const h = Math.round(size * 0.8)

  return (
    <div style={{ width: w, height: h, borderRadius: 8, overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 0, 2.8], fov: 40 }} dpr={[1, 1]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[2, 4, 2]} intensity={0.6} />
        <AvatarScene alert={alert} />
      </Canvas>
    </div>
  )
}
