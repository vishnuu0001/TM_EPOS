import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { toast } from 'react-toastify'

// Support both local and Vercel deployment
const isVercel = typeof window !== 'undefined' && window.location.origin.includes('vercel.app')
const API_BASE_URL = isVercel
  ? window.location.origin
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

// Create axios instance
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
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
            localStorage.removeItem('token')
            localStorage.removeItem('user')
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
            data.detail.forEach((err: any) => {
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
