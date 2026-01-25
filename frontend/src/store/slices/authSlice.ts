import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { readToken, readUser, writeAuth, clearAuth } from '../../services/storage'

interface User {
  id: string
  email: string
  full_name: string
  employee_id: string
  department?: string
  designation?: string
  plant_location?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}

const initialState: AuthState = {
  user: readUser<User>(),
  token: readToken(),
  isAuthenticated: !!readToken(),
  loading: false,
}

console.log('Auth initial state:', initialState)
console.log('LocalStorage token:', readToken()?.substring(0, 20))
console.log('LocalStorage user:', readUser<User>())
console.log('Computed isAuthenticated:', !!readToken())

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ user: User; token: string }>
    ) => {
      console.log('setCredentials called with:', action.payload)
      state.user = action.payload.user
      state.token = action.payload.token
      state.isAuthenticated = true
      writeAuth(action.payload.user, action.payload.token)
      console.log('Auth state updated:', {
        hasUser: !!state.user,
        hasToken: !!state.token,
        isAuthenticated: state.isAuthenticated
      })
    },
    logout: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      clearAuth()
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
  },
})

export const { setCredentials, logout, setLoading } = authSlice.actions
export default authSlice.reducer
