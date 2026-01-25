const isVercel = typeof window !== 'undefined' && window.location.origin.includes('vercel.app')
const isDev = typeof import.meta !== 'undefined' && import.meta.env?.MODE === 'development'
export const API_BASE_URL = isVercel
  ? window.location.origin
  : (import.meta.env.VITE_API_URL || (isDev ? 'http://localhost:8000' : window.location.origin))

const STORAGE_PREFIX = `epos:${API_BASE_URL}`
export const TOKEN_KEY = `${STORAGE_PREFIX}:token`
export const USER_KEY = `${STORAGE_PREFIX}:user`

export const readToken = () => localStorage.getItem(TOKEN_KEY)

export const readUser = () => {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch (e) {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

export const writeAuth = (user, token) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
