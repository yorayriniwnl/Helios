"use client"

import React from 'react'

type Props = {
  created_at?: string | null
  responded_at?: string | null
  resolved_at?: string | null
  status?: string
}

function fmtDate(iso?: string | null) {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    return d.toLocaleString()
  } catch (e) {
    return iso
  }
}

function humanDuration(start?: string | null, end?: string | null) {
  if (!start) return '—'
  const s = new Date(start).getTime()
  const e = end ? new Date(end).getTime() : Date.now()
  const diff = Math.max(0, e - s)
  const mins = Math.floor(diff / (1000 * 60))
  if (mins < 60) return `${mins}m`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ${mins % 60}m`
  const days = Math.floor(hours / 24)
  return `${days}d ${hours % 24}h`
}

export default function AlertTimeline({ created_at, responded_at, resolved_at, status }: Props) {
  const hasAssigned = !!responded_at
  const hasResolved = !!resolved_at

  return (
    <div className="flex flex-col sm:flex-row sm:items-center gap-3">
      <div className="flex items-center gap-3 w-full">
        {/* Created node */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-white/6 flex items-center justify-center text-xs font-semibold">C</div>
          <div className="text-xs">
            <div className="font-medium">Created</div>
            <div className="text-[var(--muted)]">{fmtDate(created_at)}</div>
          </div>
        </div>

        {/* connector to Assigned */}
        <div className={`flex-1 h-0.5 ${hasAssigned ? 'bg-[var(--accent)]' : 'bg-white/6'} mx-3`} />

        {/* Assigned node */}
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${hasAssigned ? 'bg-[var(--accent)] text-white' : 'bg-white/6'}`}>A</div>
          <div className="text-xs">
            <div className="font-medium">Assigned</div>
            <div className="text-[var(--muted)]">{responded_at ? fmtDate(responded_at) : '—'}</div>
          </div>
        </div>

        {/* connector to Resolved */}
        <div className={`flex-1 h-0.5 ${hasResolved ? 'bg-[var(--accent)]' : hasAssigned ? 'bg-white/6' : 'bg-white/6'} mx-3`} />

        {/* Resolved node */}
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold ${hasResolved ? 'bg-green-500 text-white' : 'bg-white/6'}`}>R</div>
          <div className="text-xs">
            <div className="font-medium">Resolved</div>
            <div className="text-[var(--muted)]">{resolved_at ? fmtDate(resolved_at) : '—'}</div>
          </div>
        </div>
      </div>

      {/* Durations */}
      <div className="text-xs text-[var(--muted)] mt-2 sm:mt-0 sm:ml-4">
        <div>To assign: {humanDuration(created_at, responded_at)}</div>
        <div>To resolve: {responded_at ? humanDuration(responded_at, resolved_at) : humanDuration(created_at, resolved_at)}</div>
        {status && <div className="mt-1">Status: <span className="font-medium text-sm">{status}</span></div>}
      </div>
    </div>
  )
}
