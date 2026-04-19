"use client"

import React from 'react'

type Props = {
  title?: string
  description?: string
  message?: string
  actionText?: string
  onAction?: () => void
}

export default function EmptyState({
  title,
  description,
  message,
  actionText,
  onAction,
}: Props) {
  const resolvedTitle = title ?? (description ? 'No items' : message ?? 'No items')
  const resolvedDescription = description ?? (title ? message ?? '' : '')

  return (
    <div className="py-12 text-center text-[var(--muted)]">
      <div className="mb-3 text-2xl">-</div>
      <div className="text-lg font-semibold mb-1">{resolvedTitle}</div>
      {resolvedDescription && <div className="text-sm mb-3">{resolvedDescription}</div>}
      {actionText && onAction && (
        <div>
          <button onClick={onAction} className="btn-primary">{actionText}</button>
        </div>
      )}
    </div>
  )
}
