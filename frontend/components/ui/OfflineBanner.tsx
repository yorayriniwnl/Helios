"use client"

import React, { useEffect, useState } from 'react'
import { isOnline, getQueueLength, processQueue, onQueueUpdated } from '../../lib/offline'
import Spinner from './Spinner'

function OfflineBanner() {
  const [online, setOnline] = useState<boolean>(() => (typeof window === 'undefined' ? true : isOnline()))
  const [queued, setQueued] = useState<number>(() => (typeof window === 'undefined' ? 0 : getQueueLength()))
  const [working, setWorking] = useState(false)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const handler = () => setOnline(isOnline())
    window.addEventListener('online', handler)
    window.addEventListener('offline', handler)
    const unsub = onQueueUpdated((len) => setQueued(len))
    return () => {
      window.removeEventListener('online', handler)
      window.removeEventListener('offline', handler)
      try { unsub && unsub() } catch (e) {}
    }
  }, [])

  async function handleSyncNow() {
    if (!online) return
    setWorking(true)
    try {
      await processQueue()
      setQueued(getQueueLength())
    } catch (e) {
      // ignore
    } finally {
      setWorking(false)
    }
  }

  if (online && queued === 0) return null

  const bg = !online ? 'bg-amber-700' : 'bg-emerald-700'

  return (
    <div className={`${bg} text-white text-sm py-2 px-4 flex items-center justify-between`}>
      <div>
        {!online ? (
          <span>You are offline — actions will be queued locally.</span>
        ) : (
          <span>Back online — syncing queued actions ({queued})</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {working && <Spinner size={16} />}
        <button onClick={handleSyncNow} disabled={!online || queued === 0 || working} className="px-2 py-1 rounded bg-white/10 text-white text-xs disabled:opacity-50">
          {online ? 'Sync now' : 'Retry when online'}
        </button>
      </div>
    </div>
  )
}

export default React.memo(OfflineBanner)
