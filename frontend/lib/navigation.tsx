import type { ComponentType, ReactNode, SVGProps } from 'react'

type YorIcon = ComponentType<SVGProps<SVGSVGElement>>

function makeIcon(children: ReactNode): YorIcon {
  return function YorInlineIcon(props) {
    return (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
        {children}
      </svg>
    )
  }
}

const Activity = makeIcon(<><path d="M3 12h4l2.2-7 4.1 14L16 12h5" /></>)
const AlertTriangle = makeIcon(<><path d="m10.3 3.8-8 14A1.4 1.4 0 0 0 3.5 20h17a1.4 1.4 0 0 0 1.2-2.2l-8-14a2 2 0 0 0-3.4 0Z" /><path d="M12 9v4" /><path d="M12 17h.01" /></>)
const BarChart3 = makeIcon(<><path d="M4 19V5" /><path d="M4 19h16" /><path d="M8 16v-5" /><path d="M12 16V7" /><path d="M16 16v-8" /></>)
const Bell = makeIcon(<><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" /><path d="M10 21h4" /></>)
const Bolt = makeIcon(<path d="m13 2-9 12h7l-1 8 9-12h-7l1-8Z" />)
const Gauge = makeIcon(<><path d="M4.5 16a8 8 0 1 1 15 0" /><path d="m12 12 3-3" /><path d="M6 18h12" /></>)
const Map = makeIcon(<><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" /><path d="M9 3v15" /><path d="M15 6v15" /></>)
const Radio = makeIcon(<><circle cx="12" cy="12" r="2" /><path d="M7.8 7.8a6 6 0 0 0 0 8.4" /><path d="M16.2 7.8a6 6 0 0 1 0 8.4" /><path d="M4.9 4.9a10 10 0 0 0 0 14.2" /><path d="M19.1 4.9a10 10 0 0 1 0 14.2" /></>)
const ShieldCheck = makeIcon(<><path d="M12 3 5 6v5c0 4.6 2.9 8.2 7 10 4.1-1.8 7-5.4 7-10V6l-7-3Z" /><path d="m9 12 2 2 4-4" /></>)
const Siren = makeIcon(<><path d="M6 18h12" /><path d="M8 18v-5a4 4 0 0 1 8 0v5" /><path d="M12 3v2" /><path d="m4.9 6.1 1.4 1.4" /><path d="m19.1 6.1-1.4 1.4" /><path d="M3 18h18" /></>)
const Waves = makeIcon(<><path d="M2 9c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2" /><path d="M2 15c2.5 0 2.5 2 5 2s2.5-2 5-2 2.5 2 5 2 2.5-2 5-2" /></>)

export const YOR_CRIMSON = '#e84b4b'
export const YOR_SIGNAL = '#ff8a7f'
export const YOR_DEEP_CRIMSON = '#671515'

export const BoltIcon = Bolt
export const BellIcon = Bell

export interface DashboardNavItem {
  href: string
  title: string
  shortTitle: string
  description: string
  icon: YorIcon
  accent: string
}

export const DASHBOARD_NAV_ITEMS: DashboardNavItem[] = [
  { href: '/dashboard', title: 'Operations Dashboard', shortTitle: 'Overview', description: 'See the signal before it becomes downtime.', icon: Gauge, accent: YOR_SIGNAL },
  { href: '/dashboard/alerts', title: 'Alert Triage', shortTitle: 'Alerts', description: 'Prioritize, assign, and resolve anomalies.', icon: Siren, accent: YOR_CRIMSON },
  { href: '/dashboard/analytics', title: 'Analytics', shortTitle: 'Analytics', description: 'Inspect trends, recovery, and evidence.', icon: BarChart3, accent: YOR_SIGNAL },
  { href: '/dashboard/meters', title: 'Meter Network', shortTitle: 'Meters', description: 'Drill into readings and asset health.', icon: Activity, accent: '#f5eaea' },
  { href: '/dashboard/zones', title: 'Zone Risk', shortTitle: 'Zones', description: 'Compare hotspots and response load.', icon: Map, accent: YOR_SIGNAL },
]

export function getPageMeta(pathname: string): DashboardNavItem {
  return DASHBOARD_NAV_ITEMS.find((item) => pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(`${item.href}/`))) ?? DASHBOARD_NAV_ITEMS[0]
}

export const HOME_HIGHLIGHTS = [
  { value: 'METER → ALERT', label: 'A traceable path from ingestion to response.' },
  { value: 'REST + WS', label: 'REST snapshots with live WebSocket updates.' },
  { value: 'DEMO READY', label: 'Synthetic data for a repeatable local walkthrough.' },
] as const

export const HOME_PAGE_GROUPS = [
  {
    title: 'Command surface',
    description: 'Start with the operational views that turn raw readings into a response queue.',
    links: [
      { href: '/dashboard', title: 'Open the dashboard', description: 'KPIs, live feed, trend context, recovery guidance, and zone risk in one workspace.', icon: Gauge, accent: YOR_SIGNAL },
      { href: '/dashboard/alerts', title: 'Triage alerts', description: 'Review severity, explanations, assignments, and resolution notes.', icon: AlertTriangle, accent: YOR_CRIMSON },
    ],
  },
  {
    title: 'Evidence and context',
    description: 'Move from a suspicious signal to the asset and zone context around it.',
    links: [
      { href: '/dashboard/meters', title: 'Inspect meters', description: 'Compare individual readings and drill into the most relevant asset history.', icon: Activity, accent: '#f5eaea' },
      { href: '/dashboard/zones', title: 'Compare zones', description: 'Use enriched zone metrics and heatmap context to focus field attention.', icon: Map, accent: YOR_SIGNAL },
      { href: '/dashboard/analytics', title: 'Read the recovery signal', description: 'Separate observed alert history from calculated recovery and forecast views.', icon: Waves, accent: YOR_SIGNAL },
    ],
  },
] as const

export const HOME_WORKFLOWS = [
  { href: '/dashboard', title: 'Monitor', description: 'See readings, alert count, and current operator status.', icon: Radio },
  { href: '/dashboard/alerts', title: 'Investigate', description: 'Open the alert queue and move from score to explanation.', icon: ShieldCheck },
  { href: '/dashboard/analytics', title: 'Recover', description: 'Review recovery metrics and document the response path.', icon: BarChart3 },
] as const

export function getZoneRiskLabel(risk: number): 'low' | 'medium' | 'high' | 'critical' {
  if (risk >= 0.8) return 'critical'
  if (risk >= 0.6) return 'high'
  if (risk >= 0.35) return 'medium'
  return 'low'
}
