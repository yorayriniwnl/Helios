"use client"

import React, { useEffect, useState } from 'react'
import { isDemoRunning, triggerShockAlert } from '../../lib/demo'

/**
 * The "shock moment" trigger from docs/demo_shock_moment.md, built in as a
 * real feature instead of a browser-console snippet an operator has to paste
 * live. Only renders in demo mode. Deterministic and offline-safe: the chime
 * is synthesized locally, so it works with no internet at the venue.
 */
export default function ShockAlertButton() {
  const [visible, setVisible] = useState(false)
  const [firing, setFiring] = useState(false)
  const [banner, setBanner] = useState<string | null>(null)

  useEffect(() => {
    setVisible(isDemoRunning())
  }, [])

  function playChime() {
    try {
      const AudioContextCtor = window.AudioContext || (window as any).webkitAudioContext
      if (!AudioContextCtor) return
      const ctx = new AudioContextCtor()
      const now = ctx.currentTime
      ;[880, 1318.5].forEach((freq, i) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.type = 'sine'
        osc.frequency.value = freq
        const start = now + i * 0.16
        gain.gain.setValueAtTime(0.0001, start)
        gain.gain.exponentialRampToValueAtTime(0.22, start + 0.02)
        gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.45)
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.start(start)
        osc.stop(start + 0.5)
      })
    } catch {
      // Web Audio unavailable — the visual treatment still lands without sound
    }
  }

  function highlightAlertRow(alertId: number) {
    try {
      const el = document.querySelector<HTMLElement>(`[data-alert-id="${alertId}"]`)
      if (!el) return
      el.classList.add('helios-shock')
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      setTimeout(() => el.classList.remove('helios-shock'), 5000)
    } catch {
      // no matching row currently mounted on this page — the banner still shows
    }
  }

  function handleTrigger() {
    if (firing) return
    setFiring(true)
    const alert = triggerShockAlert()
    playChime()
    setBanner(alert.explanation)
    setTimeout(() => highlightAlertRow(alert.id), 150)
    setTimeout(() => setBanner(null), 7000)
    setTimeout(() => setFiring(false), 1200)
  }

  if (!visible) return null

  return (
    <>
      <button
        onClick={handleTrigger}
        disabled={firing}
        className="inline-flex items-center gap-2 h-8 px-3 rounded-full text-xs font-semibold transition-all disabled:opacity-60"
        style={{ background: 'rgba(255,60,60,0.12)', border: '1px solid rgba(255,60,60,0.4)', color: '#ff6b6b' }}
        title="Trigger a live high-value anomaly for a presentation moment"
      >
        Trigger live anomaly
      </button>
      {banner && (
        <div className="helios-shock-banner" role="alert">
          <div className="text-xs uppercase tracking-wide" style={{ color: '#ff6b6b', letterSpacing: '0.06em' }}>
            Live anomaly detected
          </div>
          <div className="mt-1.5 text-sm leading-snug" style={{ color: 'var(--fg)' }}>
            {banner}
          </div>
        </div>
      )}
    </>
  )
}
