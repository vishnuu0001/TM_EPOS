import axiosInstance from './api'

export const colonyService = {
  getRequests: async (params) => {
    const response = await axiosInstance.get('/api/colony/requests', { params })
    return response.data
  },

  getRequest: async (id) => {
    const response = await axiosInstance.get(`/api/colony/requests/${id}`)
    return response.data
  },

  createRequest: async (data) => {
    const response = await axiosInstance.post('/api/colony/requests', data)
    return response.data
  },

  updateRequest: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/requests/${id}`, data)
    return response.data
  },

  assignRequest: async (id, data) => {
    const response = await axiosInstance.post(`/api/colony/requests/${id}/assign`, data)
    return response.data
  },

  changeStatus: async (id, data) => {
    const response = await axiosInstance.post(`/api/colony/requests/${id}/status`, data)
    return response.data
  },

  submitFeedback: async (requestId, data) => {
    const response = await axiosInstance.post(
      `/api/colony/requests/${requestId}/feedback`,
      { request_id: requestId, ...data }
    )
    return response.data
  },

  uploadAttachment: async (requestId, file) => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axiosInstance.post(
      `/api/colony/requests/${requestId}/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getVendors: async (params) => {
    const response = await axiosInstance.get('/api/colony/vendors', { params })
    return response.data
  },

  createVendor: async (data) => {
    const response = await axiosInstance.post('/api/colony/vendors', data)
    return response.data
  },

  updateVendor: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/vendors/${id}`, data)
    return response.data
  },

  getTechnicians: async (params) => {
    const response = await axiosInstance.get('/api/colony/technicians', { params })
    return response.data
  },

  createTechnician: async (data) => {
    const response = await axiosInstance.post('/api/colony/technicians', data)
    return response.data
  },

  updateTechnician: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/technicians/${id}`, data)
    return response.data
  },

  getAssets: async (params) => {
    const response = await axiosInstance.get('/api/colony/assets', { params })
    return response.data
  },

  createAsset: async (data) => {
    const response = await axiosInstance.post('/api/colony/assets', data)
    return response.data
  },

  updateAsset: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/assets/${id}`, data)
    return response.data
  },

  getCategories: async (params) => {
    const response = await axiosInstance.get('/api/colony/categories', { params })
    return response.data
  },

  createCategory: async (data) => {
    const response = await axiosInstance.post('/api/colony/categories', data)
    return response.data
  },

  updateCategory: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/categories/${id}`, data)
    return response.data
  },

  getRecurring: async (params) => {
    const response = await axiosInstance.get('/api/colony/recurring', { params })
    return response.data
  },

  createRecurring: async (data) => {
    const response = await axiosInstance.post('/api/colony/recurring', data)
    return response.data
  },

  updateRecurring: async (id, data) => {
    const response = await axiosInstance.put(`/api/colony/recurring/${id}`, data)
    return response.data
  },

  getDashboardStats: async () => {
    const response = await axiosInstance.get('/api/colony/dashboard/stats')
    return response.data
  },
}
