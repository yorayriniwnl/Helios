"use client"

import React, { useEffect } from 'react'

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    console.error('Helios root error:', error)
  }, [error])

  return (
    <html lang="en">
      <body style={{ margin: 0, background: '#000000', color: '#f5eaea', fontFamily: 'Inter, system-ui, -apple-system, Arial, sans-serif' }}>
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
            <p style={{ fontSize: 14, color: '#c4c4c4', marginBottom: 20 }}>
              Reloading usually resolves this. If it keeps happening, restart the app.
            </p>
            <button
              onClick={() => reset()}
              style={{
                background: '#e84b4b',
                color: '#000000',
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
