"use client"

import React, { useEffect } from 'react'

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error('Helios root error:', error)
  }, [error])

  return (
    <html lang="en">
      <body style={{ margin: 0, background: '#0b1220', color: '#e6eef8', fontFamily: 'system-ui, -apple-system, Arial, sans-serif' }}>
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
          <div
            style={{
              maxWidth: 420,
              textAlign: 'center',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: 16,
              padding: 32,
            }}
          >
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Helios hit an unexpected error</h2>
            <p style={{ fontSize: 14, color: '#94a3b8', marginBottom: 20 }}>
              Reloading usually resolves this. If it keeps happening, restart the app.
            </p>
            <button
              onClick={() => reset()}
              style={{
                background: '#5eead4',
                color: '#052e21',
                border: 'none',
                borderRadius: 999,
                padding: '10px 20px',
                fontSize: 14,
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Reload
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
