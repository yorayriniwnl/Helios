"use client"

import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { OrbitControls } from '@react-three/drei'

function FloatingNodes({ count = 8 }: { count?: number }) {
  const nodes = useMemo(() => {
    const out: { base: THREE.Vector3; seed: number; color: string }[] = []
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2
      const radius = 1.6 + Math.random() * 1.0
      const x = Math.cos(angle) * radius
      const y = (Math.random() - 0.5) * 0.6
      const z = Math.sin(angle) * radius
      out.push({ base: new THREE.Vector3(x, y, z), seed: Math.random() * 1000, color: ['#6ef', '#4ff', '#9f6'][i % 3] })
    }
    return out
  }, [count])

  const meshRefs = useRef<Array<THREE.Mesh | null>>([])
  const lineRefs = useRef<Array<THREE.LineSegments | null>>([])

  const pairs = useMemo(() => {
    const p: [number, number][] = []
    for (let i = 0; i < count; i++) {
      p.push([i, (i + 1) % count])
      if (i % 2 === 0) p.push([i, (i + 2) % count])
    }
    return p
  }, [count])

  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    for (let i = 0; i < nodes.length; i++) {
      const m = meshRefs.current[i]
      if (!m) continue
      const seed = nodes[i].seed
      const amp = 0.25
      const speed = 0.6
      const nx = nodes[i].base.x + Math.sin(t * speed + seed) * amp
      const ny = nodes[i].base.y + Math.cos(t * speed * 1.2 + seed * 0.7) * amp * 0.7
      const nz = nodes[i].base.z + Math.cos(t * speed * 0.9 + seed * 1.3) * amp * 0.4
      m.position.set(nx, ny, nz)
      const s = 0.9 + Math.sin(t * 3 + seed) * 0.15
      m.scale.set(s, s, s)
      m.rotation.y += 0.01
    }

    for (let k = 0; k < pairs.length; k++) {
      const l = lineRefs.current[k]
      if (!l) continue
      const [i, j] = pairs[k]
      const p1 = meshRefs.current[i]?.position
      const p2 = meshRefs.current[j]?.position
      if (!p1 || !p2) continue
      const pts = [new THREE.Vector3().copy(p1), new THREE.Vector3().copy(p2)]
      l.geometry.setFromPoints(pts)
      if ((l.geometry.attributes as any).position) (l.geometry.attributes as any).position.needsUpdate = true
    }
  })

  return (
      <group>
      {nodes.map((n, i) => (
        <mesh
          key={i}
          ref={(el) => {
            meshRefs.current[i] = el
          }}
          position={n.base}
        >
          <sphereGeometry args={[0.08, 12, 12]} />
          <meshStandardMaterial color={n.color} emissive={n.color} emissiveIntensity={0.9} metalness={0.2} roughness={0.25} />
        </mesh>
      ))}

      {pairs.map((pr, k) => (
        <lineSegments
          key={k}
          ref={(el) => {
            lineRefs.current[k] = el
          }}
        >
          <bufferGeometry />
          <lineBasicMaterial color="#66f6ff" transparent opacity={0.6} />
        </lineSegments>
      ))}
    </group>
  )
}

export default function ThreeHero() {
  return (
    <div style={{ width: '100%', height: 360, borderRadius: 12, overflow: 'hidden' }}>
      <Canvas camera={{ position: [0, 0, 6], fov: 45 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 5, 5]} intensity={0.6} />
        <FloatingNodes count={10} />
        <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} autoRotate autoRotateSpeed={0.18} />
      </Canvas>
    </div>
  )
}
