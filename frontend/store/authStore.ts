import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { setAuthToken, post, get } from '../lib/api'

/**
 * Minimal user shape for the auth store. Extend as needed.
 */
export type AuthUser = {
  id?: number | string
  name?: string
  email?: string
} | null

interface AuthState {
  user: AuthUser
  token: string | null
  refreshToken: string | null
  login: (email: string, password: string) => Promise<void>
  setToken: (token: string | null, refreshToken?: string | null, user?: AuthUser) => void
  logout: () => void
}


function decodeJwt(token: string): any | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    let b64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    while (b64.length % 4) b64 += '='
    let json = ''
    if (typeof window !== 'undefined' && typeof window.atob === 'function') {
      json = window.atob(b64)
    } else {
      // Node / SSR fallback
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const buf = Buffer.from(b64, 'base64')
      json = buf.toString('utf-8')
    }
    return JSON.parse(json)
  } catch (e) {
    return null
  }
}


export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      setToken: (token: string | null, refreshToken: string | null = null, user: AuthUser = null) => {
        set({ token, refreshToken, user })
        try {
          if (token) setAuthToken(token)
          else setAuthToken(undefined)
        } catch (e) {
          // best-effort
        }
      },
      login: async (email: string, password: string) => {
        // Call backend /auth/login
        const data = await post<{ access_token: string }>('/auth/login', { email, password })
        const token = data?.access_token
        if (!token) throw new Error('No access token received')

        // Attach token to API client
        try {
          setAuthToken(token)
        } catch (e) {
          // ignore
        }

        // Try to decode token to get user id and fetch user profile
        let user: AuthUser = null
        const decoded = decodeJwt(token)
        if (decoded && decoded.user_id) {
          try {
            user = await get(`/users/${decoded.user_id}`)
          } catch (e) {
            // ignore profile fetch errors
          }
        }

        set({ token, refreshToken: null, user })
      },
      logout: () => {
        set({ token: null, refreshToken: null, user: null })
        try {
          setAuthToken(undefined)
        } catch (e) {
          // ignore
        }
      },
    }),
    {
      name: 'helios.auth', // localStorage key
      partialize: (state) => ({ token: state.token, refreshToken: state.refreshToken, user: state.user }),
      onRehydrateStorage: () => (state) => {
        // when rehydrated, ensure api client has the token set
        if (state && state.token) {
          try {
            setAuthToken(state.token)
          } catch (e) {
            // ignore
          }
        }
      },
    }
  )
)

export default useAuthStore
