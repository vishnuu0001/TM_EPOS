import axiosInstance from './api'

export type RequestStatus =
  | 'submitted'
  | 'assigned'
  | 'in_progress'
  | 'materials_required'
  | 'completed'
  | 'closed'
  | 'cancelled'

export interface MaintenanceRequest {
  id: string
  request_number: string
  resident_id: string
  quarter_number: string
  category: string
  sub_category?: string
  description: string
  priority: string
  status: RequestStatus
  assigned_vendor_id?: string
  assigned_technician_id?: string
  estimated_cost?: number
  actual_cost?: number
  rating?: number
  feedback?: string
  created_at: string
  updated_at: string
}

export interface CreateMaintenanceRequest {
  quarter_number: string
  category: string
  sub_category?: string
  description: string
  priority?: string
}

export interface UpdateMaintenanceRequest {
  category?: string
  sub_category?: string
  description?: string
  priority?: string
  status?: RequestStatus
  estimated_cost?: number
  actual_cost?: number
  resolution_notes?: string
}

export interface AssignmentPayload {
  assigned_vendor_id?: string
  assigned_technician_id?: string
  requires_approval?: boolean
  estimated_cost?: number
}

export interface StatusChangePayload {
  status: RequestStatus
  notes?: string
  actual_cost?: number
}

export interface StatusHistory {
  id: string
  status: RequestStatus
  notes?: string
  changed_by?: string
  changed_at: string
}

export interface Vendor {
  id: string
  name: string
  company_name?: string
  email?: string
  phone: string
  service_categories: string
  rating: number
  total_jobs: number
  is_active: boolean
  created_at: string
}

export interface VendorPayload {
  name: string
  company_name?: string
  email?: string
  phone: string
  service_categories: string
  is_active?: boolean
}

export interface Technician {
  id: string
  name: string
  phone?: string
  email?: string
  specialization?: string
  vendor_id?: string
  rating: number
  is_active: boolean
  created_at: string
}

export interface TechnicianPayload {
  name: string
  phone?: string
  email?: string
  specialization?: string
  vendor_id?: string
  is_active?: boolean
}

export interface Asset {
  id: string
  asset_number: string
  asset_type: string
  quarter_number: string
  make?: string
  model?: string
  serial_number?: string
  installation_date?: string
  warranty_expiry?: string
  amc_start_date?: string
  amc_end_date?: string
  amc_vendor?: string
  status: string
  created_at: string
}

export interface AssetPayload {
  asset_number: string
  asset_type: string
  quarter_number: string
  make?: string
  model?: string
  serial_number?: string
  installation_date?: string
  warranty_expiry?: string
  amc_start_date?: string
  amc_end_date?: string
  amc_vendor?: string
  status?: string
}

export interface ServiceCategory {
  id: string
  name: string
  description?: string
  sla_hours: number
  icon?: string
  is_active: boolean
  created_at: string
}

export interface ServiceCategoryPayload {
  name: string
  description?: string
  sla_hours?: number
  icon?: string
  is_active?: boolean
}

export interface RecurringMaintenance {
  id: string
  name: string
  description?: string
  category: string
  frequency: string
  next_schedule_date: string
  assigned_vendor_id?: string
  is_active: boolean
  created_at: string
}

export interface RecurringPayload {
  name: string
  description?: string
  category: string
  frequency: string
  next_schedule_date: string
  assigned_vendor_id?: string
  is_active?: boolean
}

export interface DashboardStats {
  total_requests: number
  pending_requests: number
  in_progress_requests: number
  completed_requests: number
  avg_resolution_time: number
  avg_rating: number
  overdue_requests: number
  active_recurring: number
  open_assignments: number
}

export const colonyService = {
  getRequests: async (params?: {
    status?: string
    category?: string
    skip?: number
    limit?: number
  }): Promise<MaintenanceRequest[]> => {
    const response = await axiosInstance.get('/api/colony/requests', { params })
    return response.data
  },

  getRequest: async (id: string): Promise<MaintenanceRequest> => {
    const response = await axiosInstance.get(`/api/colony/requests/${id}`)
    return response.data
  },

  createRequest: async (
    data: CreateMaintenanceRequest
  ): Promise<MaintenanceRequest> => {
    const response = await axiosInstance.post('/api/colony/requests', data)
    return response.data
  },

  updateRequest: async (
    id: string,
    data: UpdateMaintenanceRequest
  ): Promise<MaintenanceRequest> => {
    const response = await axiosInstance.put(`/api/colony/requests/${id}`, data)
    return response.data
  },

  assignRequest: async (
    id: string,
    data: AssignmentPayload
  ): Promise<MaintenanceRequest> => {
    const response = await axiosInstance.post(`/api/colony/requests/${id}/assign`, data)
    return response.data
  },

  changeStatus: async (
    id: string,
    data: StatusChangePayload
  ): Promise<StatusHistory> => {
    const response = await axiosInstance.post(`/api/colony/requests/${id}/status`, data)
    return response.data
  },

  submitFeedback: async (
    requestId: string,
    data: { rating: number; feedback?: string }
  ) => {
    const response = await axiosInstance.post(
      `/api/colony/requests/${requestId}/feedback`,
      { request_id: requestId, ...data }
    )
    return response.data
  },

  uploadAttachment: async (requestId: string, file: File) => {
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

  getVendors: async (params?: { is_active?: boolean }): Promise<Vendor[]> => {
    const response = await axiosInstance.get('/api/colony/vendors', { params })
    return response.data
  },

  createVendor: async (data: VendorPayload): Promise<Vendor> => {
    const response = await axiosInstance.post('/api/colony/vendors', data)
    return response.data
  },

  updateVendor: async (id: string, data: VendorPayload): Promise<Vendor> => {
    const response = await axiosInstance.put(`/api/colony/vendors/${id}` , data)
    return response.data
  },

  getTechnicians: async (params?: { vendor_id?: string; is_active?: boolean }): Promise<Technician[]> => {
    const response = await axiosInstance.get('/api/colony/technicians', { params })
    return response.data
  },

  createTechnician: async (data: TechnicianPayload): Promise<Technician> => {
    const response = await axiosInstance.post('/api/colony/technicians', data)
    return response.data
  },

  updateTechnician: async (
    id: string,
    data: TechnicianPayload
  ): Promise<Technician> => {
    const response = await axiosInstance.put(`/api/colony/technicians/${id}`, data)
    return response.data
  },

  getAssets: async (params?: { quarter_number?: string; asset_type?: string }): Promise<Asset[]> => {
    const response = await axiosInstance.get('/api/colony/assets', { params })
    return response.data
  },

  createAsset: async (data: AssetPayload): Promise<Asset> => {
    const response = await axiosInstance.post('/api/colony/assets', data)
    return response.data
  },

  updateAsset: async (id: string, data: AssetPayload): Promise<Asset> => {
    const response = await axiosInstance.put(`/api/colony/assets/${id}`, data)
    return response.data
  },

  getCategories: async (params?: { is_active?: boolean }): Promise<ServiceCategory[]> => {
    const response = await axiosInstance.get('/api/colony/categories', { params })
    return response.data
  },

  createCategory: async (data: ServiceCategoryPayload): Promise<ServiceCategory> => {
    const response = await axiosInstance.post('/api/colony/categories', data)
    return response.data
  },

  updateCategory: async (
    id: string,
    data: ServiceCategoryPayload
  ): Promise<ServiceCategory> => {
    const response = await axiosInstance.put(`/api/colony/categories/${id}`, data)
    return response.data
  },

  getRecurring: async (params?: { is_active?: boolean }): Promise<RecurringMaintenance[]> => {
    const response = await axiosInstance.get('/api/colony/recurring', { params })
    return response.data
  },

  createRecurring: async (data: RecurringPayload): Promise<RecurringMaintenance> => {
    const response = await axiosInstance.post('/api/colony/recurring', data)
    return response.data
  },

  updateRecurring: async (
    id: string,
    data: RecurringPayload
  ): Promise<RecurringMaintenance> => {
    const response = await axiosInstance.put(`/api/colony/recurring/${id}`, data)
    return response.data
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await axiosInstance.get('/api/colony/dashboard/stats')
    return response.data
  },
}
