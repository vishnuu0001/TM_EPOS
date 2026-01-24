import api from './api'

const canteenService = {
  // Dashboard
  getDashboardStats: async () => {
    const { data } = await api.get('/api/canteen/dashboard/stats')
    return data
  },

  // Workers
  getWorkers: async () => {
    const { data } = await api.get('/api/canteen/workers')
    return data
  },
  createWorker: async (payload) => {
    const { data } = await api.post('/api/canteen/workers', payload)
    return data
  },
  updateWorker: async (id, payload) => {
    const { data } = await api.put(`/api/canteen/workers/${id}`, payload)
    return data
  },

  // Menus
  getMenus: async () => {
    const { data } = await api.get('/api/canteen/menus')
    return data
  },
  createMenu: async (payload) => {
    const { data } = await api.post('/api/canteen/menus', payload)
    return data
  },
  updateMenu: async (id, payload) => {
    const { data } = await api.put(`/api/canteen/menus/${id}`, payload)
    return data
  },

  // Menu Items
  getMenuItems: async (menuId) => {
    const { data } = await api.get(`/api/canteen/menu-items/menu/${menuId}`)
    return data
  },
  createMenuItem: async (payload) => {
    const { data } = await api.post('/api/canteen/menu-items', payload)
    return data
  },
  updateMenuItem: async (id, payload) => {
    const { data } = await api.put(`/api/canteen/menu-items/${id}`, payload)
    return data
  },

  // Orders
  getOrders: async () => {
    const { data } = await api.get('/api/canteen/orders')
    return data
  },
  createOrder: async (payload) => {
    const { data } = await api.post('/api/canteen/orders', {
      ...payload,
      items: JSON.stringify(payload.items || []),
      subsidy_amount: payload.subsidy_amount ?? 0,
    })
    return data
  },
  updateOrderStatus: async (id, status) => {
    const { data } = await api.put(`/api/canteen/orders/${id}/status`, null, { params: { status } })
    return data
  },

  // Consumption
  getConsumptions: async () => {
    const { data } = await api.get('/api/canteen/consumptions')
    return data
  },
  recordConsumption: async (payload) => {
    const { data } = await api.post('/api/canteen/consumptions', payload)
    return data
  },

  // Inventory
  getInventory: async () => {
    const { data } = await api.get('/api/canteen/inventory')
    return data
  },
  createInventory: async (payload) => {
    const { data } = await api.post('/api/canteen/inventory', payload)
    return data
  },
  updateInventory: async (id, payload) => {
    const { data } = await api.put(`/api/canteen/inventory/${id}`, payload)
    return data
  },

  // Feedback
  getFeedback: async () => {
    const { data } = await api.get('/api/canteen/feedback')
    return data
  },
  submitFeedback: async (payload) => {
    const { data } = await api.post('/api/canteen/feedback', payload)
    return data
  },
}

export default canteenService
