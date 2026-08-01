"use client"

import React, { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { OrbitControls, Html } from '@react-three/drei'

type Zone = { id: number; x: number; z: number; radius: number; risk: number; label?: string }

function ZoneMeshes({ zones, onClick }: { zones: Zone[]; onClick?: (z: Zone) => void }) {
  const refs = useRef<(THREE.Mesh | null)[]>([])
  const ringRefs = useRef<(THREE.Mesh | null)[]>([])
  const [hovered, setHovered] = useState<number | null>(null)

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    for (let i = 0; i < zones.length; i++) {
      const mesh = refs.current[i]
      const ring = ringRefs.current[i]
      const zone = zones[i]
      if (!mesh) continue
      const pulse = 1 + Math.sin(t * 3 + i) * 0.06 + zone.risk * 0.18
      mesh.scale.set(pulse, 1, pulse)
      const mat = mesh.material as THREE.MeshStandardMaterial
      if (mat) {
        mat.emissive = new THREE.Color(zone.risk > 0.6 ? '#ff5e5e' : zone.risk > 0.3 ? '#ffb86b' : '#66f6ff')
        mat.emissiveIntensity = 0.6 + zone.risk * 1.1 + (hovered === zone.id ? 0.6 : 0)
      }
      if (ring) {
        ring.rotation.z += 0.008 + zone.risk * 0.02
        ring.scale.set(1 + Math.sin(t * 2 + i) * 0.03 + zone.risk * 0.04, 1, 1 + Math.sin(t * 2 + i) * 0.03 + zone.risk * 0.04)
      }
    }
  })

  return (
    <group>
      {zones.map((z, i) => (
        <group key={z.id} position={[z.x, 0.05, z.z]}>
          <mesh
            ref={(el) => {
              refs.current[i] = el
            }}
            onPointerOver={(e) => { e.stopPropagation(); setHovered(z.id) }}
            onPointerOut={(e) => { e.stopPropagation(); setHovered(null) }}
            onPointerDown={(e) => { e.stopPropagation(); onClick && onClick(z) }}
          >
            <cylinderGeometry args={[z.radius, z.radius, 0.12, 32]} />
            <meshStandardMaterial color={'#081026'} metalness={0.2} roughness={0.4} emissive={'#000'} emissiveIntensity={0.6} transparent />
          </mesh>

          <mesh
            ref={(el) => {
              ringRefs.current[i] = el
            }}
            rotation={[Math.PI / 2, 0, 0]}
            position={[0, 0.06, 0]}
          >
            <torusGeometry args={[z.radius + 0.03, 0.01, 8, 64]} />
            <meshBasicMaterial color={z.risk > 0.6 ? '#ff5e5e' : z.risk > 0.3 ? '#ffb86b' : '#66f6ff'} transparent opacity={0.45} blending={THREE.AdditiveBlending} />
          </mesh>

          <Html position={[0, 0.2, 0]} center>
            <div style={{ padding: '4px 8px', background: 'rgba(0,0,0,0.6)', color: 'white', fontSize: 12, borderRadius: 6 }}>
              {z.label || `Zone ${z.id}`}
            </div>
          </Html>
        </group>
      ))}
    </group>
  )
}

export default function ThreeRiskMap({ onZoneClick }: { onZoneClick?: (zone: Zone) => void }) {
  const zones = useMemo<Zone[]>(
    () => [
      { id: 1, x: -2, z: -1.6, radius: 0.6, risk: 0.8, label: 'Zone A' },
      { id: 2, x: 0, z: -2.1, radius: 0.9, risk: 0.4, label: 'Zone B' },
      { id: 3, x: 2, z: -1.2, radius: 0.7, risk: 0.2, label: 'Zone C' },
      { id: 4, x: -1.2, z: 1.6, radius: 0.85, risk: 0.65, label: 'Zone D' },
      { id: 5, x: 1.6, z: 1.2, radius: 0.5, risk: 0.95, label: 'Zone E' },
    ],
    []
  )

  return (
    <div style={{ width: '100%', height: 420, borderRadius: 12, overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 6, 6], fov: 50 }} dpr={[1, 1.5]} shadows>
        <color attach="background" args={["#041024"]} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={0.6} />

        <group rotation={[-Math.PI / 2, 0, 0]}>
          <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, -0.01, 0]}>
            <planeGeometry args={[12, 12]} />
            <meshStandardMaterial color="#071024" metalness={0.2} roughness={0.9} />
          </mesh>

          <ZoneMeshes zones={zones} onClick={(z) => onZoneClick && onZoneClick(z)} />
        </group>

        <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} maxPolarAngle={Math.PI / 2.1} />
      </Canvas>
    </div>
  )
}
