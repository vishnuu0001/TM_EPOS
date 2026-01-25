import axios from 'axios'
import { toast } from 'react-toastify'
import { API_BASE_URL, readToken, clearAuth } from './storage'

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = readToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401: {
          const isLoginPage = window.location.pathname === '/login'
          const isLoginRequest = error.config?.url?.includes('/auth/login')

          if (!isLoginPage && !isLoginRequest) {
            clearAuth()
            window.location.href = '/login'
            toast.error('Session expired. Please login again.')
          } else if (isLoginRequest) {
            toast.error('Invalid credentials. Please try again.')
          }
          break
        }
        case 403:
          toast.error('You do not have permission to perform this action.')
          break
        case 404:
          toast.error('Resource not found.')
          break
        case 422:
          if (data.detail && Array.isArray(data.detail)) {
            data.detail.forEach((err) => {
              toast.error(`${err.loc.join('.')}: ${err.msg}`)
            })
          } else {
            toast.error('Validation error occurred.')
          }
          break
        case 500:
          toast.error('Internal server error. Please try again later.')
          break
        default:
          toast.error(data.detail || 'An error occurred.')
      }
    } else if (error.request) {
      toast.error('Network error. Please check your connection.')
    } else {
      toast.error('An unexpected error occurred.')
    }

    return Promise.reject(error)
  }
)

export default axiosInstance
