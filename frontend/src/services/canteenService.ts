import api from './api'

export type WorkerType = 'permanent' | 'contract' | 'casual' | 'temporary'
export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snacks'
export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'ready' | 'served' | 'cancelled'
export type PaymentStatus = 'pending' | 'paid' | 'subsidized' | 'free'
export type InventoryStatus = 'in_stock' | 'low_stock' | 'out_of_stock'

export interface WorkerPayload {
  full_name: string
  employee_id: string
  phone?: string
  email?: string
  worker_type: WorkerType
  department?: string
  designation?: string
  contractor_name?: string
  meal_entitlement?: string
  subsidy_applicable?: boolean
}

export interface Worker extends WorkerPayload {
  id: string
  worker_number: string
  biometric_id?: string
  fingerprint_enrolled: boolean
  face_enrolled: boolean
  is_active: boolean
  canteen_access: boolean
  wallet_balance: number
  created_at: string
  updated_at: string
}

export interface MenuPayload {
  menu_date: string
  meal_type: MealType
  menu_name?: string
  description?: string
}

export interface Menu extends MenuPayload {
  id: string
  is_active: boolean
  is_published: boolean
  created_by?: string
  created_at: string
  updated_at: string
}

export interface MenuItemPayload {
  menu_id: string
  item_name: string
  item_name_hindi?: string
  description?: string
  category?: string
  base_price: number
  subsidized_price: number
  quantity_prepared?: number
  calories?: number
  is_vegetarian?: boolean
  is_vegan?: boolean
  contains_allergens?: string
  image_url?: string
  display_order?: number
}

export interface MenuItem extends MenuItemPayload {
  id: string
  is_available: boolean
  quantity_remaining: number
  created_at: string
  updated_at: string
}

export interface OrderItemInput {
  item_id: string
  quantity: number
  item_name?: string
  unit_price?: number
}

export interface OrderPayload {
  worker_id: string
  menu_id?: string
  meal_type: MealType
  items: OrderItemInput[]
  total_amount: number
  subsidy_amount?: number
  payable_amount: number
  payment_method?: string
  kiosk_id?: string
}

export interface Order extends OrderPayload {
  id: string
  order_number: string
  token_number: number
  order_date: string
  order_time: string
  items: string
  payment_status: PaymentStatus
  status: OrderStatus
  payment_time?: string
  confirmed_at?: string
  prepared_at?: string
  served_at?: string
  counter_number?: string
  cancelled_at?: string
  cancellation_reason?: string
  created_at: string
  updated_at: string
}

export interface ConsumptionPayload {
  order_id: string
  worker_id: string
  meal_type: MealType
  consumption_date: string
  items_ordered: string
  items_consumed?: string
  items_wasted?: string
  wastage_percentage?: number
  wastage_reason?: string
  meal_completed?: boolean
}

export interface Consumption extends ConsumptionPayload {
  id: string
  consumption_time: string
  created_at: string
}

export interface InventoryPayload {
  item_name: string
  item_name_hindi?: string
  category?: string
  unit: string
  current_stock?: number
  minimum_stock?: number
  maximum_stock?: number
  reorder_level?: number
  unit_price?: number
  supplier_name?: string
  supplier_contact?: string
  is_perishable?: boolean
  expiry_date?: string
}

export interface InventoryItem extends InventoryPayload {
  id: string
  item_code: string
  status: InventoryStatus
  total_value: number
  last_purchase_date?: string
  last_purchase_quantity?: number
  last_updated?: string
  created_at: string
  updated_at: string
}

export interface FeedbackPayload {
  worker_id: string
  meal_type: MealType
  food_quality_rating?: number
  taste_rating?: number
  quantity_rating?: number
  hygiene_rating?: number
  service_rating?: number
  overall_rating?: number
  comments?: string
  suggestions?: string
  complaint?: boolean
  complaint_category?: string
  complaint_description?: string
}

export interface Feedback extends FeedbackPayload {
  id: string
  feedback_date: string
  responded: boolean
  response_by?: string
  response_text?: string
  response_date?: string
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_workers: number
  today_orders: number
  today_consumption: number
  pending_orders: number
  low_stock_items: number
  average_rating: number
  today_revenue: number
}

const canteenService = {
  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const { data } = await api.get('/api/canteen/dashboard/stats')
    return data
  },

  // Workers
  getWorkers: async (): Promise<Worker[]> => {
    const { data } = await api.get('/api/canteen/workers')
    return data
  },
  createWorker: async (payload: WorkerPayload): Promise<Worker> => {
    const { data } = await api.post('/api/canteen/workers', payload)
    return data
  },
  updateWorker: async (id: string, payload: Partial<WorkerPayload>): Promise<Worker> => {
    const { data } = await api.put(`/api/canteen/workers/${id}`, payload)
    return data
  },

  // Menus
  getMenus: async (): Promise<Menu[]> => {
    const { data } = await api.get('/api/canteen/menus')
    return data
  },
  createMenu: async (payload: MenuPayload): Promise<Menu> => {
    const { data } = await api.post('/api/canteen/menus', payload)
    return data
  },
  updateMenu: async (id: string, payload: Partial<MenuPayload> & { is_active?: boolean; is_published?: boolean }): Promise<Menu> => {
    const { data } = await api.put(`/api/canteen/menus/${id}`, payload)
    return data
  },

  // Menu Items
  getMenuItems: async (menuId: string): Promise<MenuItem[]> => {
    const { data } = await api.get(`/api/canteen/menu-items/menu/${menuId}`)
    return data
  },
  createMenuItem: async (payload: MenuItemPayload): Promise<MenuItem> => {
    const { data } = await api.post('/api/canteen/menu-items', payload)
    return data
  },
  updateMenuItem: async (id: string, payload: Partial<MenuItemPayload> & { is_available?: boolean; quantity_remaining?: number }): Promise<MenuItem> => {
    const { data } = await api.put(`/api/canteen/menu-items/${id}`, payload)
    return data
  },

  // Orders
  getOrders: async (): Promise<Order[]> => {
    const { data } = await api.get('/api/canteen/orders')
    return data
  },
  createOrder: async (payload: OrderPayload): Promise<Order> => {
    const { data } = await api.post('/api/canteen/orders', {
      ...payload,
      items: JSON.stringify(payload.items || []),
      subsidy_amount: payload.subsidy_amount ?? 0,
    })
    return data
  },
  updateOrderStatus: async (id: string, status: OrderStatus): Promise<Order> => {
    const { data } = await api.put(`/api/canteen/orders/${id}/status`, null, { params: { status } })
    return data
  },

  // Consumption
  getConsumptions: async (): Promise<Consumption[]> => {
    const { data } = await api.get('/api/canteen/consumptions')
    return data
  },
  recordConsumption: async (payload: ConsumptionPayload): Promise<Consumption> => {
    const { data } = await api.post('/api/canteen/consumptions', payload)
    return data
  },

  // Inventory
  getInventory: async (): Promise<InventoryItem[]> => {
    const { data } = await api.get('/api/canteen/inventory')
    return data
  },
  createInventory: async (payload: InventoryPayload): Promise<InventoryItem> => {
    const { data } = await api.post('/api/canteen/inventory', payload)
    return data
  },
  updateInventory: async (id: string, payload: Partial<InventoryPayload> & { status?: InventoryStatus; total_value?: number }): Promise<InventoryItem> => {
    const { data } = await api.put(`/api/canteen/inventory/${id}`, payload)
    return data
  },

  // Feedback
  getFeedback: async (): Promise<Feedback[]> => {
    const { data } = await api.get('/api/canteen/feedback')
    return data
  },
  submitFeedback: async (payload: FeedbackPayload): Promise<Feedback> => {
    const { data } = await api.post('/api/canteen/feedback', payload)
    return data
  },
}

export default canteenService
