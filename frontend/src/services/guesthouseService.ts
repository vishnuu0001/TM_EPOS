import api from './api';

export interface Room {
  id: string;
  room_number: string;
  room_type: string;
  floor: number;
  capacity: number;
  amenities?: string;
  rate_per_night: number;
  status: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Booking {
  id: string;
  booking_number: string;
  guest_name: string;
  guest_email?: string;
  guest_phone: string;
  guest_company?: string;
  guest_id_proof?: string;
  room_id: string;
  check_in_date: string;
  check_out_date: string;
  actual_checkin?: string;
  actual_checkout?: string;
  booked_by_user_id: string;
  cost_center?: string;
  status: string;
  total_amount: number;
  payment_status: string;
  meal_plan?: string;
  special_requests?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateBooking {
  guest_name: string;
  guest_email?: string;
  guest_phone: string;
  guest_company?: string;
  guest_id_proof?: string;
  room_id: string;
  check_in_date: string;
  check_out_date: string;
  cost_center?: string;
  meal_plan?: string;
  special_requests?: string;
  notes?: string;
  booked_by_user_id: string;
}

export interface DashboardStats {
  total_rooms: number;
  occupied_rooms: number;
  available_rooms: number;
  maintenance_rooms: number;
  total_bookings: number;
  pending_bookings: number;
  checked_in_guests: number;
  occupancy_rate: number;
  revenue_today: number;
  revenue_month: number;
}

export interface AvailabilityRequest {
  check_in_date: string;
  check_out_date: string;
  room_type?: string;
}

export interface AvailabilityResponse {
  available_rooms: Room[];
  total_available: number;
}

const guesthouseService = {
  // Rooms
  getRooms: async (status?: string): Promise<Room[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/guesthouse/rooms', { params });
    return response.data;
  },

  getRoom: async (id: string): Promise<Room> => {
    const response = await api.get(`/api/guesthouse/rooms/${id}`);
    return response.data;
  },

  // Bookings
  getBookings: async (status?: string): Promise<Booking[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/guesthouse/bookings', { params });
    return response.data;
  },

  getBooking: async (id: string): Promise<Booking> => {
    const response = await api.get(`/api/guesthouse/bookings/${id}`);
    return response.data;
  },

  createBooking: async (booking: CreateBooking): Promise<Booking> => {
    const response = await api.post('/api/guesthouse/bookings', booking);
    return response.data;
  },

  updateBooking: async (id: string, data: Partial<Booking>): Promise<Booking> => {
    const response = await api.put(`/api/guesthouse/bookings/${id}`, data);
    return response.data;
  },

  checkIn: async (bookingId: string, data: { booking_id: string; guest_id_proof: string; notes?: string }) => {
    const response = await api.post(`/api/guesthouse/bookings/${bookingId}/checkin`, data);
    return response.data;
  },

  checkOut: async (bookingId: string, data: { booking_id: string; feedback?: string }) => {
    const response = await api.post(`/api/guesthouse/bookings/${bookingId}/checkout`, data);
    return response.data;
  },

  // Availability
  checkAvailability: async (request: AvailabilityRequest): Promise<AvailabilityResponse> => {
    const response = await api.post('/api/guesthouse/availability', request);
    return response.data;
  },

  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/guesthouse/dashboard/stats');
    return response.data;
  },
};

export default guesthouseService;
