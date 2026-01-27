const hasWindow = typeof window !== 'undefined'
const hasStorage = hasWindow && typeof window.localStorage !== 'undefined'
const origin = hasWindow ? window.location.origin : ''
const isVercel = hasWindow && origin.includes('vercel.app')
const isDev = typeof import.meta !== 'undefined' && import.meta.env?.MODE === 'development'
export const API_BASE_URL = isVercel
  ? origin
  : (import.meta.env.VITE_API_URL || (isDev ? 'http://localhost:8000' : origin))

const STORAGE_PREFIX = `epos:${API_BASE_URL}`
export const TOKEN_KEY = `${STORAGE_PREFIX}:token`
export const USER_KEY = `${STORAGE_PREFIX}:user`

export const readToken = () => {
  if (!hasStorage) return null
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

const parseJwt = (token: string) => {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    if (!hasWindow || typeof window.atob !== 'function') return null
    const padLength = (4 - (normalized.length % 4)) % 4
    const padded = normalized + '='.repeat(padLength)
    const decoded = window.atob(padded)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

export const isTokenExpired = (token: string | null) => {
  if (!token) return true
  const payload = parseJwt(token)
  const exp = payload?.exp
  const iat = payload?.iat
  if (!exp || typeof exp !== 'number') return true
  const maxSessionSeconds = 8 * 60
  if (typeof iat === 'number' && exp - iat > maxSessionSeconds) return true
  return Date.now() >= exp * 1000
}

export const readUser = <T>() => {
  if (!hasStorage) return null
  let raw: string | null = null
  try {
    raw = localStorage.getItem(USER_KEY)
  } catch {
    return null
  }
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    try {
      localStorage.removeItem(USER_KEY)
    } catch {
      // ignore
    }
    return null
  }
}

export const writeAuth = (user: unknown, token: string) => {
  if (!hasStorage) return
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  } catch {
    // ignore
  }
}

export const clearAuth = () => {
  if (!hasStorage) return
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {
    // ignore
  }
}
