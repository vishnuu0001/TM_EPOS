import api from './api';

export interface Vehicle {
  id: string;
  registration_number: string;
  vehicle_type: string;
  make_model: string;
  capacity: number;
  fuel_type: string;
  status: string;
  current_km: number;
  created_at: string;
}

export interface Requisition {
  id: string;
  requisition_number: string;
  requester_id: string;
  department: string;
  cost_center?: string;
  purpose: string;
  destination: string;
  pickup_location: string;
  requested_date: string;
  requested_time: string;
  estimated_return?: string;
  number_of_passengers: number;
  vehicle_type?: string;
  special_requirements?: string;
  status: string;
  approver_id?: string;
  approval_date?: string;
  approval_remarks?: string;
  vehicle_id?: string;
  driver_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateRequisition {
  department: string;
  cost_center?: string;
  purpose: string;
  destination: string;
  pickup_location: string;
  requested_date: string;
  requested_time: string;
  estimated_return?: string;
  number_of_passengers: number;
  vehicle_type?: string;
  special_requirements?: string;
  requester_id: string;
}

export interface Trip {
  id: string;
  requisition_id: string;
  vehicle_id: string;
  driver_id: string;
  start_time?: string;
  end_time?: string;
  start_km: number;
  end_km?: number;
  distance_km?: number;
  fuel_added_liters?: number;
  fuel_cost?: number;
  status: string;
  driver_rating?: number;
  vehicle_rating?: number;
  feedback?: string;
  created_at: string;
}

export interface DashboardStats {
  total_vehicles: number;
  available_vehicles: number;
  in_use_vehicles: number;
  maintenance_vehicles: number;
  total_requisitions: number;
  pending_requisitions: number;
  approved_requisitions: number;
  active_trips: number;
  total_km_today: number;
  fuel_cost_today: number;
}

const vehicleService = {
  // Vehicles
  getVehicles: async (status?: string): Promise<Vehicle[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/vehicle/vehicles', { params });
    return response.data;
  },

  // Requisitions
  getRequisitions: async (status?: string): Promise<Requisition[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/vehicle/requisitions', { params });
    return response.data;
  },

  getRequisition: async (id: string): Promise<Requisition> => {
    const response = await api.get(`/api/vehicle/requisitions/${id}`);
    return response.data;
  },

  createRequisition: async (requisition: CreateRequisition): Promise<Requisition> => {
    const response = await api.post('/api/vehicle/requisitions', requisition);
    return response.data;
  },

  updateRequisition: async (id: string, data: Partial<Requisition>): Promise<Requisition> => {
    const response = await api.put(`/api/vehicle/requisitions/${id}`, data);
    return response.data;
  },

  approveRequisition: async (id: string, remarks?: string) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/approve`, { remarks });
    return response.data;
  },

  rejectRequisition: async (id: string, remarks: string) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/reject`, { remarks });
    return response.data;
  },

  assignVehicle: async (id: string, vehicleId: string, driverId: string) => {
    const response = await api.post(`/api/vehicle/requisitions/${id}/assign`, {
      vehicle_id: vehicleId,
      driver_id: driverId,
    });
    return response.data;
  },

  // Trips
  getTrips: async (status?: string): Promise<Trip[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/vehicle/trips', { params });
    return response.data;
  },

  startTrip: async (requisitionId: string, startKm: number) => {
    const response = await api.post('/api/vehicle/trips/start', {
      requisition_id: requisitionId,
      start_km: startKm,
    });
    return response.data;
  },

  endTrip: async (tripId: string, data: { end_km: number; fuel_added_liters?: number; fuel_cost?: number }) => {
    const response = await api.post(`/api/vehicle/trips/${tripId}/end`, data);
    return response.data;
  },

  submitFeedback: async (tripId: string, data: { driver_rating: number; vehicle_rating: number; feedback?: string }) => {
    const response = await api.post(`/api/vehicle/trips/${tripId}/feedback`, data);
    return response.data;
  },

  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/vehicle/dashboard/stats');
    return response.data;
  },
};

export default vehicleService;
