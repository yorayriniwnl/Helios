"use client"

import React from 'react'

type SkeletonProps = {
  height?: number | string
  width?: number | string
  className?: string
  rounded?: boolean
}

export default function Skeleton({ height = 16, width = '100%', className = '', rounded = true }: SkeletonProps) {
  const h = typeof height === 'number' ? `${height}px` : height
  const w = typeof width === 'number' ? `${width}px` : width
  return (
    <div
      className={`animate-pulse bg-white/6 ${rounded ? 'rounded-md' : ''} ${className}`}
      style={{ height: h, width: w }}
      aria-hidden
    />
  )
}
