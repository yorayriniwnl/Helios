"use client"

import React from 'react'

export default function ErrorMessage({ message }: { message?: string | null }) {
  if (!message) return null
  return (
    <div className="p-3 rounded bg-[rgba(255,0,0,0.04)] border border-red-600/10 text-red-400">
      {message}
    </div>
  )
}
