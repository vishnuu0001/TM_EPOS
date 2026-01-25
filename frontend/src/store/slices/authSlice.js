import { createSlice } from '@reduxjs/toolkit'
import { readToken, readUser, writeAuth, clearAuth } from '../../services/storage'

const storedUser = readUser()

const initialState = {
  user: storedUser || null,
  token: readToken(),
  isAuthenticated: !!readToken(),
  loading: false,
}

console.log('Auth initial state:', initialState)
console.log('LocalStorage token:', readToken()?.substring(0, 20))
console.log('LocalStorage user:', storedUser)
console.log('Computed isAuthenticated:', !!readToken())

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      console.log('setCredentials called with:', action.payload)
      state.user = action.payload.user
      state.token = action.payload.token
      state.isAuthenticated = true
      writeAuth(action.payload.user, action.payload.token)
      console.log('Auth state updated:', {
        hasUser: !!state.user,
        hasToken: !!state.token,
        isAuthenticated: state.isAuthenticated,
      })
    },
    logout: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      clearAuth()
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
  },
})

export const { setCredentials, logout, setLoading } = authSlice.actions
export default authSlice.reducer
