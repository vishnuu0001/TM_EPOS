import api from './api'

const guesthouseService = {
  // Rooms
  getRooms: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/guesthouse/rooms', { params })
    return response.data
  },

  getRoom: async (id) => {
    const response = await api.get(`/api/guesthouse/rooms/${id}`)
    return response.data
  },

  // Bookings
  getBookings: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/guesthouse/bookings', { params })
    return response.data
  },

  getBooking: async (id) => {
    const response = await api.get(`/api/guesthouse/bookings/${id}`)
    return response.data
  },

  createBooking: async (booking) => {
    const response = await api.post('/api/guesthouse/bookings', booking)
    return response.data
  },

  updateBooking: async (id, data) => {
    const response = await api.put(`/api/guesthouse/bookings/${id}`, data)
    return response.data
  },

  checkIn: async (bookingId, data) => {
    const response = await api.post(`/api/guesthouse/bookings/${bookingId}/checkin`, data)
    return response.data
  },

  checkOut: async (bookingId, data) => {
    const response = await api.post(`/api/guesthouse/bookings/${bookingId}/checkout`, data)
    return response.data
  },

  // Availability
  checkAvailability: async (request) => {
    const response = await api.post('/api/guesthouse/availability', request)
    return response.data
  },

  // Dashboard
  getDashboardStats: async () => {
    const response = await api.get('/api/guesthouse/dashboard/stats')
    return response.data
  },
}

export default guesthouseService
