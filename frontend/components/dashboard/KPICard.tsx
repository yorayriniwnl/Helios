import React from 'react'

type Trend = {
  direction: 'up' | 'down'
  change: number | string
  label?: string
}

type KPICardProps = {
  title: string
  value: number | string
  trend?: Trend
  icon?: React.ReactNode
  subtitle?: string
  className?: string
}

const BoltIcon = ({ className = '' }: { className?: string }) => (
  <svg viewBox="0 0 24 24" width="20" height="20" className={className} fill="currentColor" aria-hidden>
    <path d="M13 2L3 14h7l-1 8L21 10h-7l0-8z" />
  </svg>
)

const ArrowUp = ({ className = '' }: { className?: string }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
    <path d="M12 19V6" />
    <path d="M5 12l7-7 7 7" />
  </svg>
)

const ArrowDown = ({ className = '' }: { className?: string }) => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden>
    <path d="M12 5v13" />
    <path d="M19 12l-7 7-7-7" />
  </svg>
)

export default function KPICard({ title, value, trend, icon, subtitle, className = '' }: KPICardProps) {
  const trendUp = trend && trend.direction === 'up'
  const trendColor = trendUp ? 'text-green-400' : 'text-red-400'

  return (
    <div className={`card pop-in group interactive-item flex items-center justify-between ${className}`}>
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 rounded-lg flex items-center justify-center transform-gpu transition-transform duration-250 group-hover:scale-105" style={{ background: 'linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))' }}>
          {icon ?? <BoltIcon className="text-[var(--accent)]" />}
        </div>

        <div>
          <div className="text-sm text-[var(--muted)]">{title}</div>
          <div className="text-2xl font-semibold mt-1"><span className="value-anim">{value}</span></div>
          {subtitle && <div className="text-xs text-[var(--muted)] mt-1">{subtitle}</div>}
        </div>
      </div>

      <div className="flex flex-col items-end">
        <div className={`inline-flex items-center gap-2 font-medium ${trend ? trendColor : 'text-[var(--muted)]'}`}>
          {trend ? (trendUp ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />) : null}
          <span className="text-sm">{trend ? trend.change : '—'}</span>
        </div>
        <div className="text-xs text-[var(--muted)] mt-1">{trend?.label ?? 'vs last period'}</div>
      </div>
    </div>
  )
}
