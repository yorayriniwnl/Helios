import type { WsMessage } from '../types/api'

type Listener = (message: string | WsMessage) => void

const listeners = new Set<Listener>()
let socket: WebSocket | null = null
let socketUrl: string | null = null

function defaultWebSocketUrl(): string {
  const configured = (typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_API_URL : undefined)?.trim()
  const origin = (configured || 'http://localhost:8000').replace(/\/$/, '')
  if (/^https?:\/\//i.test(origin)) return `${origin.replace(/^http/i, 'ws')}/ws/live`
  return `ws://${origin}/ws/live`
}

function dispatch(message: string | WsMessage): void {
  listeners.forEach((listener) => {
    try {
      listener(message)
    } catch {
      // One consumer must not break the shared event fan-out.
    }
  })
}

export function addWebSocketListener(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function removeWebSocketListener(listener: Listener): void {
  listeners.delete(listener)
}

export function connectWebSocket(url = defaultWebSocketUrl()): WebSocket | null {
  if (typeof window === 'undefined' || typeof WebSocket === 'undefined') return null
  if (socket && socketUrl === url && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return socket

  disconnectWebSocket()
  socketUrl = url
  socket = new WebSocket(url)
  socket.onmessage = (event) => dispatch(event.data as string)
  socket.onerror = () => {
    // Consumers receive close/error through the WebSocket instance itself.
  }
  socket.onclose = () => {
    socket = null
  }
  return socket
}

export function disconnectWebSocket(): void {
  if (socket) {
    try { socket.close() } catch { /* already closed */ }
  }
  socket = null
  socketUrl = null
}

export function emitLocalMessage(message: WsMessage): void {
  dispatch(message)
}

export default connectWebSocket
