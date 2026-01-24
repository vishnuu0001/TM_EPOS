import axiosInstance from './api'

const vigilanceService = {
  getDashboardStats: async () => {
    const res = await axiosInstance.get('/api/vigilance/dashboard/stats')
    return res.data
  },

  getRosters: async (params) => {
    const res = await axiosInstance.get('/api/vigilance/roster', { params })
    return res.data
  },

  createRoster: async (payload) => {
    const res = await axiosInstance.post('/api/vigilance/roster', payload)
    return res.data
  },

  updateRoster: async (id, payload) => {
    const res = await axiosInstance.put(`/api/vigilance/roster/${id}`, payload)
    return res.data
  },

  checkInRoster: async (id) => {
    const res = await axiosInstance.post(`/api/vigilance/roster/${id}/check-in`)
    return res.data
  },

  checkOutRoster: async (id) => {
    const res = await axiosInstance.post(`/api/vigilance/roster/${id}/check-out`)
    return res.data
  },

  getCheckpoints: async (params) => {
    const res = await axiosInstance.get('/api/vigilance/checkpoints', { params })
    return res.data
  },

  createCheckpoint: async (payload) => {
    const res = await axiosInstance.post('/api/vigilance/checkpoints', payload)
    return res.data
  },

  updateCheckpoint: async (id, payload) => {
    const res = await axiosInstance.put(`/api/vigilance/checkpoints/${id}`, payload)
    return res.data
  },

  getPatrolLogs: async (params) => {
    const res = await axiosInstance.get('/api/vigilance/patrol-log', { params })
    return res.data
  },

  createPatrolLog: async (payload) => {
    const res = await axiosInstance.post('/api/vigilance/patrol-log', payload)
    return res.data
  },

  getIncidents: async (params) => {
    const res = await axiosInstance.get('/api/vigilance/incidents', { params })
    return res.data
  },

  createIncident: async (payload) => {
    const res = await axiosInstance.post('/api/vigilance/incidents', payload)
    return res.data
  },

  updateIncident: async (id, payload) => {
    const res = await axiosInstance.put(`/api/vigilance/incidents/${id}`, payload)
    return res.data
  },

  acknowledgeIncident: async (id) => {
    const res = await axiosInstance.post(`/api/vigilance/incidents/${id}/acknowledge`)
    return res.data
  },

  resolveIncident: async (id, resolutionNotes) => {
    const res = await axiosInstance.post(`/api/vigilance/incidents/${id}/resolve`, null, { params: { resolution_notes: resolutionNotes } })
    return res.data
  },

  getSOSAlerts: async (params) => {
    const res = await axiosInstance.get('/api/vigilance/sos', { params })
    return res.data
  },

  createSOSAlert: async (payload) => {
    const res = await axiosInstance.post('/api/vigilance/sos', payload)
    return res.data
  },

  acknowledgeSOS: async (id) => {
    const res = await axiosInstance.post(`/api/vigilance/sos/${id}/acknowledge`)
    return res.data
  },

  resolveSOS: async (id, resolutionNotes, falseAlarm = false, falseAlarmReason) => {
    const res = await axiosInstance.post(`/api/vigilance/sos/${id}/resolve`, null, {
      params: { resolution_notes: resolutionNotes, false_alarm: falseAlarm, false_alarm_reason: falseAlarmReason },
    })
    return res.data
  },
}

export default vigilanceService
