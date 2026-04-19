/**
 * alertStore — Zustand store for live alert state.
 *
 * Maintains an in-memory list of alerts that can be updated optimistically
 * from UI actions and merged with WebSocket push events. Designed as a
 * complement to the server-side truth obtained via useAlerts().
 *
 * Actions:
 *   pushAlert   – prepend a new alert (from WS or API)
 *   setAlerts   – bulk replace (e.g. after fetch)
 *   markAssigned(id, userId) – optimistic update
 *   markResolved(id)         – optimistic update
 *   incrementUnread          – badge counter
 *   clearUnread              – reset after user opens alert panel
 */
import { create } from 'zustand'
import type { ApiAlert } from '../types/api'

const MAX_ALERTS = 500  // keep memory bounded

interface AlertState {
  // ── data ──────────────────────────────────────────────────────────────────
  alerts: ApiAlert[]
  unreadCount: number

  // ── actions ───────────────────────────────────────────────────────────────
  setAlerts: (alerts: ApiAlert[]) => void
  pushAlert: (alert: ApiAlert) => void
  markAssigned: (id: number, userId: number) => void
  markResolved: (id: number, notes?: string) => void
  removeAlert: (id: number) => void
  incrementUnread: () => void
  clearUnread: () => void
}

export const useAlertStore = create<AlertState>()((set) => ({
  alerts: [],
  unreadCount: 0,

  setAlerts: (alerts) =>
    set({ alerts: alerts.slice(0, MAX_ALERTS) }),

  pushAlert: (alert) =>
    set((state) => {
      // skip duplicates
      if (state.alerts.some((a) => a.id === alert.id)) return state
      return {
        alerts: [alert, ...state.alerts].slice(0, MAX_ALERTS),
        unreadCount: state.unreadCount + 1,
      }
    }),

  markAssigned: (id, userId) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id ? { ...a, status: 'assigned' as const, assigned_to: userId } : a
      ),
    })),

  markResolved: (id, notes) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === id
          ? {
              ...a,
              status: 'resolved' as const,
              resolved_at: new Date().toISOString(),
              resolution_notes: notes ?? a.resolution_notes,
            }
          : a
      ),
    })),

  removeAlert: (id) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.id !== id),
    })),

  incrementUnread: () =>
    set((state) => ({ unreadCount: state.unreadCount + 1 })),

  clearUnread: () => set({ unreadCount: 0 }),
}))

export default useAlertStore
