import axiosInstance from './api'

const equipmentService = {
  getDashboardStats: async () => {
    const res = await axiosInstance.get('/api/equipment/dashboard/stats')
    return res.data
  },

  getEquipment: async (params) => {
    const res = await axiosInstance.get('/api/equipment/equipment', { params })
    return res.data
  },

  createEquipment: async (payload) => {
    const res = await axiosInstance.post('/api/equipment/equipment', payload)
    return res.data
  },

  updateEquipment: async (id, payload) => {
    const res = await axiosInstance.put(`/api/equipment/equipment/${id}`, payload)
    return res.data
  },

  getBookings: async (params) => {
    const res = await axiosInstance.get('/api/equipment/bookings', { params })
    return res.data
  },

  createBooking: async (payload) => {
    const res = await axiosInstance.post('/api/equipment/bookings', payload)
    return res.data
  },

  updateBooking: async (id, payload) => {
    const res = await axiosInstance.put(`/api/equipment/bookings/${id}`, payload)
    return res.data
  },

  approveBooking: async (id) => {
    const res = await axiosInstance.post(`/api/equipment/bookings/${id}/approve`)
    return res.data
  },

  getMaintenance: async (params) => {
    const res = await axiosInstance.get('/api/equipment/maintenance', { params })
    return res.data
  },

  createMaintenance: async (payload) => {
    const res = await axiosInstance.post('/api/equipment/maintenance', payload)
    return res.data
  },

  updateMaintenance: async (id, payload) => {
    const res = await axiosInstance.put(`/api/equipment/maintenance/${id}`, payload)
    return res.data
  },

  getCertifications: async (params) => {
    const res = await axiosInstance.get('/api/equipment/certifications', { params })
    return res.data
  },

  createCertification: async (payload) => {
    const res = await axiosInstance.post('/api/equipment/certifications', payload)
    return res.data
  },

  verifyCertification: async (operatorId, equipmentType) => {
    const res = await axiosInstance.get(`/api/equipment/certifications/verify/${operatorId}/${equipmentType}`)
    return res.data
  },

  createUsageLog: async (payload) => {
    const res = await axiosInstance.post('/api/equipment/usage-logs', payload)
    return res.data
  },

  getUsageLog: async (bookingId) => {
    const res = await axiosInstance.get(`/api/equipment/usage-logs/${bookingId}`)
    return res.data
  },
}

export default equipmentService
