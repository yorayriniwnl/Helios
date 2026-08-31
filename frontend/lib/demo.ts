import { emitLocalMessage } from './websocket'

let running = false
let interval: ReturnType<typeof setInterval> | null = null
let sequence = 0

const DEMO_METERS = [101, 204, 305, 412]

function demoReading() {
  const meterId = DEMO_METERS[sequence % DEMO_METERS.length]
  const reading = {
    id: 900_000 + sequence,
    meter_id: meterId,
    timestamp: new Date().toISOString(),
    voltage: 228 + (sequence % 5),
    current: 8 + (sequence % 4),
    power_consumption: 1800 + ((sequence * 137) % 900),
  }
  sequence += 1
  return reading
}

export function isDemoModeEnabled(): boolean {
  if (running) return true
  try {
    return window.localStorage.getItem('helios.demo') === '1'
      || new URLSearchParams(window.location.search).get('demo') === 'silent'
  } catch {
    return false
  }
}

export function isDemoRunning(): boolean {
  return isDemoModeEnabled()
}

export function startDemo(): void {
  if (running) return
  running = true
  sequence = 0
  emitLocalMessage({ type: 'reading', data: demoReading() })
  interval = setInterval(() => {
    if (!running) return
    emitLocalMessage({ type: 'reading', data: demoReading() })
  }, 2_500)
}

export function stopDemo(): void {
  running = false
  if (interval) clearInterval(interval)
  interval = null
}

export function triggerShockAlert() {
  const meterId = DEMO_METERS[sequence % DEMO_METERS.length]
  sequence += 1
  const alert = {
    id: 910_000 + sequence,
    meter_id: meterId,
    type: 'tamper_suspicion',
    severity: 'critical' as const,
    status: 'open' as const,
    score: 0.97,
    explanation: `Sustained under-reporting detected at M-${meterId}; inspect the meter and transformer path.`,
    created_at: new Date().toISOString(),
  }
  emitLocalMessage({ type: 'alert', data: alert })
  return alert
}
