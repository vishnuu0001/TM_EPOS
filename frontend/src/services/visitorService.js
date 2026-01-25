import api from './api'

const visitorService = {
  // Visitor Requests
  getRequests: async (status) => {
    const params = status ? { status } : {}
    const response = await api.get('/api/visitor/requests', { params })
    return response.data
  },

  getRequest: async (id) => {
    const response = await api.get(`/api/visitor/requests/${id}`)
    return response.data
  },

  createRequest: async (request) => {
    const response = await api.post('/api/visitor/requests', request)
    return response.data
  },

  updateRequest: async (id, data) => {
    const response = await api.put(`/api/visitor/requests/${id}`, data)
    return response.data
  },

  approveRequest: async (id, remarks) => {
    const response = await api.post(`/api/visitor/requests/${id}/approve`, { remarks })
    return response.data
  },

  rejectRequest: async (id, remarks) => {
    const response = await api.post(`/api/visitor/requests/${id}/reject`, { remarks })
    return response.data
  },

  // Safety Training
  getTrainingModule: async () => {
    const response = await api.get('/api/visitor/training/module')
    return response.data
  },

  completeTraining: async (requestId, quizScore) => {
    const response = await api.post('/api/visitor/training/complete', {
      request_id: requestId,
      quiz_score: quizScore,
    })
    return response.data
  },

  // Medical Clearance
  uploadMedicalDocuments: async (requestId, files) => {
    const formData = new FormData()
    formData.append('request_id', requestId)
    files.forEach((file) => {
      formData.append('files', file)
    })
    const response = await api.post('/api/visitor/medical/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  verifyMedical: async (requestId) => {
    const response = await api.post(`/api/visitor/medical/${requestId}/verify`)
    return response.data
  },

  // Gate Pass
  getGatePass: async (requestId) => {
    const response = await api.get(`/api/visitor/gatepass/${requestId}`)
    return response.data
  },

  checkIn: async (passNumber) => {
    const response = await api.post('/api/visitor/gatepass/checkin', { pass_number: passNumber })
    return response.data
  },

  checkOut: async (passNumber) => {
    const response = await api.post('/api/visitor/gatepass/checkout', { pass_number: passNumber })
    return response.data
  },

  // Dashboard
  getDashboardStats: async () => {
    const response = await api.get('/api/visitor/dashboard/stats')
    const data = response.data || {}

    return {
      total_requests: data.total_requests || 0,
      pending_requests: data.pending_requests ?? data.pending_approvals ?? 0,
      approved_requests: data.approved_requests || 0,
      active_visitors: data.active_visitors ?? data.visitors_onsite ?? 0,
      training_pending: data.training_pending || 0,
      medical_pending: data.medical_pending || 0,
      visitors_today: data.visitors_today ?? data.today_entries ?? 0,
      visitors_onsite: data.visitors_onsite ?? data.active_visitors ?? 0,
    }
  },

  // Active Visitors
  getActiveVisitors: async () => {
    const response = await api.get('/api/visitor/active')
    return response.data
  },
}

export default visitorService
