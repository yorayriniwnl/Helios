import React from 'react'
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center text-center px-6" style={{ minHeight: '60vh' }}>
      <div
        className="rounded-2xl p-8 max-w-md"
        style={{ background: 'var(--card-bg)', border: '1px solid var(--card-border)', boxShadow: 'var(--shadow-1)' }}
      >
        <div className="text-xs uppercase tracking-wide mb-2" style={{ color: 'var(--accent)', letterSpacing: '0.08em' }}>
          404
        </div>
        <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--fg)' }}>
          Page not found
        </h2>
        <p className="text-sm mb-6" style={{ color: 'var(--muted)' }}>
          That page doesn&apos;t exist, or the link is out of date.
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-4 py-2 rounded-full text-sm font-semibold"
          style={{ background: 'var(--accent)', color: '#052e21' }}
        >
          Back to dashboard
        </Link>
      </div>
    </div>
  )
}
