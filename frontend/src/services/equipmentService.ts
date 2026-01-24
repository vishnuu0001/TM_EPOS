import axiosInstance from './api'

export type EquipmentType =
  | 'CRANE'
  | 'FORKLIFT'
  | 'EXCAVATOR'
  | 'LOADER'
  | 'TRUCK'
  | 'GENERATOR'
  | 'OTHER'

export type EquipmentStatus = 'AVAILABLE' | 'IN_USE' | 'MAINTENANCE' | 'OUT_OF_SERVICE'
export type BookingStatus = 'REQUESTED' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED'

export interface Equipment {
  id: string
  equipment_number: string
  name: string
  equipment_type: EquipmentType
  manufacturer?: string
  model?: string
  capacity?: string
  location?: string
  hourly_rate?: number
  requires_certification: boolean
  description?: string
  status: EquipmentStatus
  created_at: string
}

export interface EquipmentPayload {
  equipment_number: string
  name: string
  equipment_type: EquipmentType
  manufacturer?: string
  model?: string
  capacity?: string
  location?: string
  hourly_rate?: number
  requires_certification?: boolean
  description?: string
  status?: EquipmentStatus
}

export interface Booking {
  id: string
  booking_number: string
  equipment_id: string
  operator_id: string
  start_time: string
  end_time: string
  actual_start_time?: string
  actual_end_time?: string
  purpose: string
  location?: string
  cost_center?: string
  status: BookingStatus
  requested_by_id: string
  approved_by_id?: string
  safety_permit_id?: string
  notes?: string
  created_at: string
}

export interface BookingPayload {
  equipment_id: string
  operator_id: string
  start_time: string
  end_time: string
  purpose: string
  location?: string
  cost_center?: string
}

export interface BookingUpdatePayload {
  start_time?: string
  end_time?: string
  status?: BookingStatus
  notes?: string
}

export interface Maintenance {
  id: string
  equipment_id: string
  maintenance_type: string
  description?: string
  scheduled_date: string
  completed_date?: string
  next_service_hours?: number
  next_service_date?: string
  performed_by?: string
  cost?: number
  notes?: string
  created_at: string
}

export interface MaintenancePayload {
  equipment_id: string
  maintenance_type: string
  description?: string
  scheduled_date: string
  next_service_hours?: number
  next_service_date?: string
}

export interface MaintenanceUpdatePayload {
  completed_date?: string
  performed_by?: string
  cost?: number
  notes?: string
}

export interface Certification {
  id: string
  operator_id: string
  equipment_type: EquipmentType
  certification_number: string
  issued_date: string
  expiry_date: string
  issuing_authority?: string
  is_active: boolean
  created_at: string
}

export interface CertificationPayload {
  operator_id: string
  equipment_type: EquipmentType
  certification_number: string
  issued_date: string
  expiry_date: string
  issuing_authority?: string
}

export interface UsageLog {
  id: string
  booking_id: string
  actual_hours?: number
  fuel_consumed?: number
  fuel_type?: string
  start_reading?: number
  end_reading?: number
  issues_reported?: string
  operator_remarks?: string
  created_at: string
}

export interface UsageLogPayload {
  booking_id: string
  actual_hours?: number
  fuel_consumed?: number
  fuel_type?: string
  start_reading?: number
  end_reading?: number
  issues_reported?: string
  operator_remarks?: string
}

export interface DashboardStats {
  total_equipment: number
  available_equipment: number
  in_use_equipment: number
  maintenance_equipment: number
  total_bookings: number
  active_bookings: number
  pending_approvals: number
  utilization_rate: number
  pending_maintenance: number
  expired_certifications: number
}

const equipmentService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await axiosInstance.get('/api/equipment/dashboard/stats')
    return res.data
  },

  getEquipment: async (params?: {
    status?: EquipmentStatus
    equipment_type?: EquipmentType
    skip?: number
    limit?: number
  }): Promise<Equipment[]> => {
    const res = await axiosInstance.get('/api/equipment/equipment', { params })
    return res.data
  },

  createEquipment: async (payload: EquipmentPayload): Promise<Equipment> => {
    const res = await axiosInstance.post('/api/equipment/equipment', payload)
    return res.data
  },

  updateEquipment: async (id: string, payload: EquipmentPayload): Promise<Equipment> => {
    const res = await axiosInstance.put(`/api/equipment/equipment/${id}`, payload)
    return res.data
  },

  getBookings: async (params?: {
    status?: BookingStatus
    equipment_id?: string
    operator_id?: string
    from_date?: string
    skip?: number
    limit?: number
  }): Promise<Booking[]> => {
    const res = await axiosInstance.get('/api/equipment/bookings', { params })
    return res.data
  },

  createBooking: async (payload: BookingPayload): Promise<Booking> => {
    const res = await axiosInstance.post('/api/equipment/bookings', payload)
    return res.data
  },

  updateBooking: async (id: string, payload: BookingUpdatePayload): Promise<Booking> => {
    const res = await axiosInstance.put(`/api/equipment/bookings/${id}`, payload)
    return res.data
  },

  approveBooking: async (id: string) => {
    const res = await axiosInstance.post(`/api/equipment/bookings/${id}/approve`)
    return res.data
  },

  getMaintenance: async (params?: { equipment_id?: string; pending_only?: boolean }): Promise<Maintenance[]> => {
    const res = await axiosInstance.get('/api/equipment/maintenance', { params })
    return res.data
  },

  createMaintenance: async (payload: MaintenancePayload): Promise<Maintenance> => {
    const res = await axiosInstance.post('/api/equipment/maintenance', payload)
    return res.data
  },

  updateMaintenance: async (id: string, payload: MaintenanceUpdatePayload): Promise<Maintenance> => {
    const res = await axiosInstance.put(`/api/equipment/maintenance/${id}`, payload)
    return res.data
  },

  getCertifications: async (params?: {
    operator_id?: string
    equipment_type?: EquipmentType
    active_only?: boolean
  }): Promise<Certification[]> => {
    const res = await axiosInstance.get('/api/equipment/certifications', { params })
    return res.data
  },

  createCertification: async (payload: CertificationPayload): Promise<Certification> => {
    const res = await axiosInstance.post('/api/equipment/certifications', payload)
    return res.data
  },

  verifyCertification: async (operator_id: string, equipment_type: EquipmentType) => {
    const res = await axiosInstance.get(`/api/equipment/certifications/verify/${operator_id}/${equipment_type}`)
    return res.data as { is_certified: boolean; certification: Certification | null }
  },

  createUsageLog: async (payload: UsageLogPayload): Promise<UsageLog> => {
    const res = await axiosInstance.post('/api/equipment/usage-logs', payload)
    return res.data
  },

  getUsageLog: async (booking_id: string): Promise<UsageLog> => {
    const res = await axiosInstance.get(`/api/equipment/usage-logs/${booking_id}`)
    return res.data
  },
}

export default equipmentService
