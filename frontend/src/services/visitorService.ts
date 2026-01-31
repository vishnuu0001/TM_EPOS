import api from './api';

export interface VisitorRequest {
  id: string;
  request_number: string;
  visitor_name: string;
  visitor_company?: string;
  visitor_phone: string;
  visitor_email?: string;
  visitor_type: string;
  sponsor_employee_id: string;
  sponsor_name: string;
  sponsor_department?: string;
  purpose_of_visit: string;
  visit_date: string;
  expected_duration?: number;
  areas_to_visit?: string;
  status: string;
  safety_required: boolean;
  medical_required: boolean;
  approved_by_sponsor: boolean;
  approved_by_safety: boolean;
  approved_by_security: boolean;
  final_approved_by?: string;
  final_approved_at?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateVisitorRequest {
  visitor_name: string;
  visitor_company?: string;
  visitor_phone: string;
  visitor_email?: string;
  visitor_type: string;
  sponsor_employee_id: string;
  sponsor_name: string;
  sponsor_department?: string;
  purpose_of_visit: string;
  visit_date: string;
  expected_duration?: number;
  areas_to_visit?: string;
  safety_required?: boolean;
  medical_required?: boolean;
  visit_time?: string;
}

export interface TrainingModule {
  id: string;
  title: string;
  description: string;
  video_url: string;
  duration_minutes: number;
  quiz_questions: QuizQuestion[];
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
}

export interface GatePass {
  id: string;
  pass_number: string;
  visitor_request_id: string;
  qr_code: string;
  valid_from: string;
  valid_to: string;
  entry_time?: string;
  exit_time?: string;
  created_at: string;
}

export interface DashboardStats {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  active_visitors: number;
  training_pending: number;
  medical_pending: number;
  visitors_today: number;
  visitors_onsite: number;
}

type RawDashboardStats = Partial<DashboardStats> & {
  pending_approvals?: number;
  today_entries?: number;
  today_exits?: number;
  completed_visits?: number;
  gate_passes_issued?: number;
};

const visitorService = {
  // Visitor Requests
  getRequests: async (status?: string): Promise<VisitorRequest[]> => {
    const params = status ? { status } : {};
    const response = await api.get('/api/visitor/requests', { params });
    return response.data;
  },

  getRequest: async (id: string): Promise<VisitorRequest> => {
    const response = await api.get(`/api/visitor/requests/${id}`);
    return response.data;
  },

  createRequest: async (request: CreateVisitorRequest): Promise<VisitorRequest> => {
    const response = await api.post('/api/visitor/requests', request);
    return response.data;
  },

  updateRequest: async (id: string, data: Partial<VisitorRequest>): Promise<VisitorRequest> => {
    const response = await api.put(`/api/visitor/requests/${id}`, data);
    return response.data;
  },

  approveRequest: async (id: string, level: 'sponsor' | 'safety' | 'security' | 'final' = 'final') => {
    const response = await api.post(`/api/visitor/requests/${id}/approve`, null, {
      params: { level },
    });
    return response.data;
  },

  rejectRequest: async (id: string, reason: string) => {
    const response = await api.post(`/api/visitor/requests/${id}/reject`, null, {
      params: { reason },
    });
    return response.data;
  },

  // Safety Training
  getTrainingModule: async (): Promise<TrainingModule> => {
    const response = await api.get('/api/visitor/training/module');
    return response.data;
  },

  completeTraining: async (requestId: string, quizScore: number) => {
    const response = await api.post('/api/visitor/training/complete', {
      request_id: requestId,
      quiz_score: quizScore,
    });
    return response.data;
  },

  // Medical Clearance
  uploadMedicalDocuments: async (requestId: string, files: File[]) => {
    const formData = new FormData();
    formData.append('request_id', requestId);
    files.forEach((file) => {
      formData.append('files', file);
    });
    const response = await api.post('/api/visitor/medical/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  verifyMedical: async (requestId: string) => {
    const response = await api.post(`/api/visitor/medical/${requestId}/verify`);
    return response.data;
  },

  // Gate Pass
  getGatePass: async (requestId: string): Promise<GatePass> => {
    const response = await api.get(`/api/visitor/gatepass/${requestId}`);
    return response.data;
  },

  checkIn: async (passNumber: string) => {
    const response = await api.post('/api/visitor/gatepass/checkin', { pass_number: passNumber });
    return response.data;
  },

  checkOut: async (passNumber: string) => {
    const response = await api.post('/api/visitor/gatepass/checkout', { pass_number: passNumber });
    return response.data;
  },

  // Dashboard
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/api/visitor/dashboard/stats');
    const data: RawDashboardStats = response.data || {};

    return {
      total_requests: data.total_requests ?? 0,
      pending_requests: data.pending_requests ?? data.pending_approvals ?? 0,
      approved_requests: data.approved_requests ?? 0,
      active_visitors: data.active_visitors ?? data.visitors_onsite ?? 0,
      training_pending: data.training_pending ?? 0,
      medical_pending: data.medical_pending ?? 0,
      visitors_today: data.visitors_today ?? data.today_entries ?? 0,
      visitors_onsite: data.visitors_onsite ?? data.active_visitors ?? 0,
    };
  },

  // Active Visitors
  getActiveVisitors: async () => {
    const response = await api.get('/api/visitor/active');
    return response.data;
  },
};

export default visitorService;
