import { createSlice } from '@reduxjs/toolkit'

const storedUser = localStorage.getItem('user')

const initialState = {
  user: storedUser ? JSON.parse(storedUser) : null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
}

console.log('Auth initial state:', initialState)
console.log('LocalStorage token:', localStorage.getItem('token')?.substring(0, 20))
console.log('LocalStorage user:', localStorage.getItem('user'))
console.log('Computed isAuthenticated:', !!localStorage.getItem('token'))

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      console.log('setCredentials called with:', action.payload)
      state.user = action.payload.user
      state.token = action.payload.token
      state.isAuthenticated = true
      localStorage.setItem('token', action.payload.token)
      localStorage.setItem('user', JSON.stringify(action.payload.user))
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
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
  },
})

export const { setCredentials, logout, setLoading } = authSlice.actions
export default authSlice.reducer
