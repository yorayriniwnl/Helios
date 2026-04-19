"use client"

import React from 'react'

type SpinnerProps = {
  size?: number
  className?: string
}

export default function Spinner({ size = 24, className = '' }: SpinnerProps) {
  const s = `${size}px`
  return (
    <div
      className={`animate-spin rounded-full ${className}`}
      style={{
        width: s,
        height: s,
        borderWidth: 3,
        borderStyle: 'solid',
        borderColor: 'rgba(255,255,255,0.12)',
        borderTopColor: 'var(--accent)',
      }}
    />
  )
}
