import axiosInstance from './api'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    full_name: string
    employee_id: string
    department?: string
    designation?: string
    plant_location?: string
  }
}

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await axiosInstance.post<LoginResponse>(
      '/api/auth/login',
      formData
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
