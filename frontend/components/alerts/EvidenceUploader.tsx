"use client"

import React, { useState } from 'react'

type EvidenceItem = {
  id?: number
  alert_id?: number
  file_url?: string
  original_filename?: string
  gps_lat?: number | null
  gps_lon?: number | null
  evidence_ts?: string | null
  notes?: string | null
  before_after?: string | null
  created_at?: string | null
}

type Props = {
  alertId: number
  onUploaded?: (item: EvidenceItem) => void
}

const API_HOST = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function EvidenceUploader({ alertId, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [notes, setNotes] = useState('')
  const [beforeAfter, setBeforeAfter] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!file) {
      setError('Choose a file to upload.')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (notes.trim()) formData.append('notes', notes.trim())
      if (beforeAfter) formData.append('before_after', beforeAfter)

      const headers: HeadersInit = {}

      try {
        const raw = localStorage.getItem('helios.auth')
        if (raw) {
          const parsed = JSON.parse(raw)
          if (parsed?.token) {
            headers.Authorization = `Bearer ${parsed.token}`
          }
        }
      } catch {
        // Ignore auth rehydration failures; backend will reject unauthorized uploads.
      }

      const response = await fetch(`${API_HOST.replace(/\/$/, '')}/api/v1/alerts/${alertId}/evidence`, {
        method: 'POST',
        body: formData,
        headers,
      })

      if (!response.ok) {
        let detail = 'Upload failed.'
        try {
          const body = await response.json()
          detail = body?.detail || detail
        } catch {
          // Ignore JSON parsing errors.
        }
        throw new Error(detail)
      }

      const item = (await response.json()) as EvidenceItem
      setFile(null)
      setNotes('')
      setBeforeAfter('')
      onUploaded?.(item)
    } catch (err: any) {
      setError(err?.message || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-1">
        <label className="text-xs font-medium text-[var(--muted)]">Evidence file</label>
        <input
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="block w-full text-xs"
        />
      </div>

      <div className="space-y-1">
        <label className="text-xs font-medium text-[var(--muted)]">Stage</label>
        <select
          value={beforeAfter}
          onChange={(event) => setBeforeAfter(event.target.value)}
          className="w-full rounded border bg-transparent px-2 py-1 text-xs"
        >
          <option value="">Unspecified</option>
          <option value="before">Before</option>
          <option value="after">After</option>
        </select>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-medium text-[var(--muted)]">Notes</label>
        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={3}
          className="w-full rounded border bg-transparent px-2 py-1 text-xs"
          placeholder="Optional inspection notes"
        />
      </div>

      {error && <div className="text-xs text-red-300">{error}</div>}

      <button
        type="submit"
        disabled={uploading}
        className="rounded border px-3 py-1 text-xs disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : 'Upload evidence'}
      </button>
    </form>
  )
}
