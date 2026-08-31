/**
 * Small, typed HTTP boundary for the Helios frontend.
 *
 * The backend exposes JSON directly under /api/v1. Keeping URL construction,
 * auth headers, errors, and short-lived GET caching here makes every hook use
 * the same contract and keeps demo/local deployments interchangeable.
 */

export type QueryValue = string | number | boolean | null | undefined

export interface RequestOptions {
  cacheMs?: number
  signal?: AbortSignal
}

export interface GetOptions {
  params?: Record<string, QueryValue>
}

export class ApiError extends Error {
  readonly status: number
  readonly body: unknown

  constructor(message: string, status: number, body: unknown = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.body = body
  }
}

const ACCESS_TOKEN_KEY = 'helios.access_token'
const DEFAULT_API_ORIGIN = 'http://localhost:8000'
const responseCache = new Map<string, { expiresAt: number; value: unknown }>()
let memoryToken: string | undefined

function configuredApiOrigin(): string {
  const configured = typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_API_URL : undefined
  return (configured?.trim() || DEFAULT_API_ORIGIN).replace(/\/$/, '')
}

export function buildApiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  const origin = configuredApiOrigin()
  if (origin.endsWith('/api/v1')) return `${origin}${normalizedPath}`
  if (origin.endsWith('/api')) return `${origin}/v1${normalizedPath}`
  return `${origin}/api/v1${normalizedPath}`
}

export function getAuthToken(): string | undefined {
  if (memoryToken) return memoryToken
  try {
    const stored = window.localStorage.getItem(ACCESS_TOKEN_KEY)
    if (stored) memoryToken = stored
  } catch {
    // Restricted storage should not prevent public/demo rendering.
  }
  return memoryToken
}

export function setAuthToken(token?: string): void {
  memoryToken = token || undefined
  try {
    if (memoryToken) window.localStorage.setItem(ACCESS_TOKEN_KEY, memoryToken)
    else window.localStorage.removeItem(ACCESS_TOKEN_KEY)
  } catch {
    // Auth can still be held in memory when storage is unavailable.
  }
}

function withQuery(path: string, params?: Record<string, QueryValue>): string {
  if (!params) return path
  const query = Object.entries(params)
    .filter(([, value]) => value !== undefined && value !== null && value !== '')
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&')
  return query ? `${path}${path.includes('?') ? '&' : '?'}${query}` : path
}

function errorMessage(body: unknown, fallback: string): string {
  if (typeof body === 'string' && body.trim()) return body
  if (body && typeof body === 'object') {
    const candidate = body as { detail?: unknown; message?: unknown }
    if (typeof candidate.detail === 'string' && candidate.detail.trim()) return candidate.detail
    if (typeof candidate.message === 'string' && candidate.message.trim()) return candidate.message
  }
  return fallback
}

async function request<T>(method: string, path: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
  const url = buildApiUrl(path)
  const headers: Record<string, string> = { Accept: 'application/json' }
  const token = getAuthToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const response = await fetch(url, {
    method,
    headers,
    credentials: 'include',
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    ...(options.signal ? { signal: options.signal } : {}),
  })

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(errorMessage(payload, `${method} ${path} failed (${response.status})`), response.status, payload)
  }
  return payload as T
}

export async function get<T>(path: string, options?: GetOptions, requestOptions: RequestOptions = {}): Promise<T> {
  const cacheKey = withQuery(path, options?.params)
  const now = Date.now()
  const cached = responseCache.get(cacheKey)
  if (cached && cached.expiresAt > now) return cached.value as T

  const value = await request<T>('GET', cacheKey, undefined, requestOptions)
  if ((requestOptions.cacheMs ?? 0) > 0) {
    responseCache.set(cacheKey, { expiresAt: now + requestOptions.cacheMs!, value })
  }
  return value
}

export function post<T>(path: string, body?: unknown, requestOptions: RequestOptions = {}): Promise<T> {
  return request<T>('POST', path, body, requestOptions)
}

export function patch<T>(path: string, body?: unknown, requestOptions: RequestOptions = {}): Promise<T> {
  return request<T>('PATCH', path, body, requestOptions)
}

export function clearResponseCache(): void {
  responseCache.clear()
}
