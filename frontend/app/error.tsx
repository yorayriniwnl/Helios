"use client"

import React, { useEffect } from 'react'
import Link from 'next/link'

export default function ErrorBoundary({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // Surfaced in the console for whoever's debugging; never shown to the viewer.
    console.error('Helios route error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center text-center px-6" style={{ minHeight: '60vh' }}>
      <div
        className="rounded-2xl p-8 max-w-md"
        style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)', boxShadow: 'var(--shadow-1)' }}
      >
        <div
          className="mx-auto mb-4 flex items-center justify-center rounded-full"
          style={{ width: 48, height: 48, background: 'rgba(251,113,133,0.12)' }}
        >
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fb7185" strokeWidth={1.75}>
            <path d="M12 4 2 20h20L12 4Z" />
            <path d="M12 10v5" />
            <circle cx="12" cy="17.5" r="0.6" fill="#fb7185" />
          </svg>
        </div>
        <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--fg)' }}>
          Something went wrong
        </h2>
        <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
          This view hit an unexpected error. The rest of Helios is unaffected — try again, or head back to the
          dashboard.
        </p>
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={() => reset()}
            className="px-4 py-2 rounded-full text-sm font-semibold"
            style={{ background: 'var(--accent)', color: '#052e21' }}
          >
            Try again
          </button>
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-full text-sm font-semibold"
            style={{ border: '1px solid var(--card-border)', color: 'var(--fg)' }}
          >
            Back to dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
