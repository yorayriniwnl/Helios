'use client'

import React, { useEffect } from 'react'
import Sidebar from '../../components/layout/Sidebar'
import Header from '../../components/layout/Header'
import connectWebSocket from '../../lib/websocket'
import { addWebSocketListener } from '../../lib/websocket'
import useAlertStore from '../../store/alertStore'
import type { ApiAlert } from '../../types/api'

/**
 * DashboardLayout — wraps all dashboard pages.
 *
 * Responsibilities:
 * 1. Renders the persistent Sidebar + Header chrome.
 * 2. Opens (and keeps alive) the WebSocket connection for the entire
 *    dashboard session — child pages just subscribe via hooks.
 * 3. Pushes incoming WS alert events into the global alertStore so the
 *    unread badge in the Header updates in real time.
 */
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pushAlert = useAlertStore((s) => s.pushAlert)

  useEffect(() => {
    // Connect WS (reuses existing socket if already open)
    const isDemoMode =
      typeof window !== 'undefined' && localStorage.getItem('helios.demo') === '1'
    if (!isDemoMode) {
      connectWebSocket()
    }

    // Route incoming alert messages to the global store
    const remove = addWebSocketListener((raw: any) => {
      try {
        const msg = typeof raw === 'string' ? JSON.parse(raw) : raw
        if (msg?.type === 'alert' && msg.data) {
          pushAlert(msg.data as ApiAlert)
        }
      } catch {
        // ignore malformed messages
      }
    })

    return remove
  }, [pushAlert])

  return (
    <div className="min-h-screen flex bg-[var(--bg)] text-[var(--fg)]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </div>
  )
}
