import api from './api'

const vehicleService = {
  // Vehicles
  getVehicles: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/vehicle/vehicles', { params })
    return response.data
  },

  // Requisitions
  getRequisitions: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/vehicle/requisitions', { params })
    return response.data
  },

  getRequisition: async (id) => {
    const response = await api.get(`/api/vehicle/requisitions/${id}`)
    return response.data
  },

  createRequisition: async (requisition) => {
    const response = await api.post('/api/vehicle/requisitions', requisition)
    return response.data
  },

  updateRequisition: async (id, data) => {
    const response = await api.put(`/api/vehicle/requisitions/${id}`, data)
    return response.data
  },

  approveRequisition: async (id, vehicleId) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/approve`, null, {
      params: { vehicle_id: vehicleId },
    })
    return response.data
  },

  rejectRequisition: async (id, remarks) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/reject`, { remarks })
    return response.data
  },

  assignVehicle: async (id, vehicleId, driverId) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/assign`, {
      vehicle_id: vehicleId,
      driver_id: driverId,
    })
    return response.data
  },

  // Trips
  getTrips: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/vehicle/trips', { params })
    return response.data
  },

  startTrip: async (requisitionId, startKm) => {
    const response = await api.post('/api/vehicle/trips/start', {
      requisition_id: requisitionId,
      start_km: startKm,
    })
    return response.data
  },

  endTrip: async (tripId, data) => {
    const response = await api.post(`/api/vehicle/trips/${tripId}/end`, data)
    return response.data
  },

  submitFeedback: async (tripId, data) => {
    const response = await api.post(`/api/vehicle/trips/${tripId}/feedback`, data)
    return response.data
  },

  // Dashboard
  getDashboardStats: async () => {
    const response = await api.get('/api/vehicle/dashboard/stats')
    return response.data
  },
}

export default vehicleService
