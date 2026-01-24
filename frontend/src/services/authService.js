import axiosInstance from './api'

export const authService = {
  login: async (credentials) => {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await axiosInstance.post(
      '/api/auth/login',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    )
    return response.data
  },

  getCurrentUser: async () => {
    const response = await axiosInstance.get('/api/auth/me')
    return response.data
  },

  logout: async () => {
    const response = await axiosInstance.post('/api/auth/logout')
    return response.data
  },
}
