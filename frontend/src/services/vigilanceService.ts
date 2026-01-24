import axiosInstance from './api'

export type ShiftType = 'morning' | 'evening' | 'night'
export type DutyStatus = 'scheduled' | 'active' | 'completed' | 'cancelled' | 'absent'
export type PatrolStatus = 'not_started' | 'in_progress' | 'completed' | 'missed'
export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical'
export type IncidentStatus = 'reported' | 'acknowledged' | 'investigating' | 'resolved' | 'closed'
export type SOSStatus = 'active' | 'responding' | 'resolved' | 'false_alarm'

export interface DashboardStats {
  total_guards: number
  active_patrols: number
  completed_patrols: number
  total_checkpoints: number
  incidents_today: number
  incidents_open: number
  sos_alerts_active: number
  sos_alerts_today: number
  missed_patrols: number
  critical_incidents: number
}

export interface DutyRoster {
  id: string
  roster_number: string
  guard_id: string
  guard_name: string
  guard_phone?: string
  guard_employee_id?: string
  duty_date: string
  shift_type: ShiftType
  shift_start: string
  shift_end: string
  assigned_gate?: string
  assigned_sector?: string
  patrol_route?: string
  status: DutyStatus
  check_in_time?: string
  check_out_time?: string
  supervisor_id?: string
  supervisor_name?: string
  special_instructions?: string
  remarks?: string
  created_by?: string
  created_at: string
  updated_at: string
}

export interface DutyRosterPayload {
  guard_id: string
  guard_name: string
  guard_phone?: string
  guard_employee_id?: string
  duty_date: string
  shift_type: ShiftType
  shift_start: string
  shift_end: string
  assigned_gate?: string
  assigned_sector?: string
  patrol_route?: string
  supervisor_id?: string
  supervisor_name?: string
  special_instructions?: string
}

export interface Checkpoint {
  id: string
  checkpoint_number: string
  checkpoint_name: string
  location_description?: string
  sector?: string
  building?: string
  floor?: string
  gps_latitude?: number
  gps_longitude?: number
  rfid_tag_id?: string
  qr_code?: string
  is_active: boolean
  is_critical: boolean
  expected_scan_interval?: number
  patrol_sequence?: number
  created_at: string
  updated_at: string
}

export interface CheckpointPayload {
  checkpoint_name: string
  location_description?: string
  sector?: string
  building?: string
  floor?: string
  gps_latitude?: number
  gps_longitude?: number
  rfid_tag_id?: string
  is_critical?: boolean
  expected_scan_interval?: number
  patrol_sequence?: number
}

export interface PatrolLog {
  id: string
  log_number: string
  duty_roster_id: string
  checkpoint_id: string
  scan_time: string
  scan_method: string
  guard_id: string
  guard_name?: string
  status: PatrolStatus
  is_on_time: boolean
  delay_minutes: number
  gps_latitude?: number
  gps_longitude?: number
  location_verified: boolean
  observations?: string
  anomalies_found: boolean
  anomaly_description?: string
  photo_path?: string
  created_at: string
}

export interface PatrolLogPayload {
  duty_roster_id: string
  checkpoint_id: string
  scan_method?: string
  guard_id: string
  guard_name?: string
  gps_latitude?: number
  gps_longitude?: number
  observations?: string
  anomalies_found?: boolean
  anomaly_description?: string
  photo_path?: string
}

export interface Incident {
  id: string
  incident_number: string
  title: string
  description: string
  incident_type: string
  severity: IncidentSeverity
  location: string
  sector?: string
  building?: string
  floor?: string
  gps_latitude?: number
  gps_longitude?: number
  incident_time: string
  reported_time: string
  reported_by_guard_id: string
  reported_by_guard_name?: string
  duty_roster_id?: string
  status: IncidentStatus
  acknowledged_by?: string
  acknowledged_at?: string
  response_team?: string
  response_time?: string
  resolution_notes?: string
  resolved_by?: string
  resolved_at?: string
  actions_taken?: string
  police_informed: boolean
  fire_dept_informed: boolean
  medical_assistance: boolean
  witnesses?: string
  evidence_collected?: string
  created_at: string
  updated_at: string
}

export interface IncidentPayload {
  title: string
  description: string
  incident_type: string
  severity: IncidentSeverity
  location: string
  sector?: string
  building?: string
  floor?: string
  gps_latitude?: number
  gps_longitude?: number
  incident_time: string
  reported_by_guard_id: string
  reported_by_guard_name?: string
  duty_roster_id?: string
  witnesses?: string
}

export interface IncidentUpdatePayload {
  title?: string
  description?: string
  severity?: IncidentSeverity
  status?: IncidentStatus
  response_team?: string
  resolution_notes?: string
  actions_taken?: string
  police_informed?: boolean
  fire_dept_informed?: boolean
  medical_assistance?: boolean
  evidence_collected?: string
}

export interface SOSAlert {
  id: string
  alert_number: string
  alert_time: string
  alert_type: string
  guard_id: string
  guard_name: string
  guard_phone?: string
  location?: string
  sector?: string
  gps_latitude?: number
  gps_longitude?: number
  status: SOSStatus
  acknowledged_by?: string
  acknowledged_at?: string
  response_team?: string
  response_time?: string
  responders_arrived_at?: string
  resolved_at?: string
  resolution_notes?: string
  false_alarm: boolean
  false_alarm_reason?: string
  incident_id?: string
  created_at: string
  updated_at: string
}

export interface SOSPayload {
  guard_id: string
  guard_name: string
  guard_phone?: string
  alert_type?: string
  location?: string
  sector?: string
  gps_latitude?: number
  gps_longitude?: number
}

const vigilanceService = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await axiosInstance.get('/api/vigilance/dashboard/stats')
    return res.data
  },

  getRosters: async (params?: { status?: DutyStatus; shift_type?: ShiftType; guard_id?: string; date?: string }): Promise<DutyRoster[]> => {
    const res = await axiosInstance.get('/api/vigilance/roster', { params })
    return res.data
  },

  createRoster: async (payload: DutyRosterPayload): Promise<DutyRoster> => {
    const res = await axiosInstance.post('/api/vigilance/roster', payload)
    return res.data
  },

  updateRoster: async (id: string, payload: Partial<DutyRosterPayload>): Promise<DutyRoster> => {
    const res = await axiosInstance.put(`/api/vigilance/roster/${id}`, payload)
    return res.data
  },

  checkInRoster: async (id: string) => {
    const res = await axiosInstance.post(`/api/vigilance/roster/${id}/check-in`)
    return res.data
  },

  checkOutRoster: async (id: string) => {
    const res = await axiosInstance.post(`/api/vigilance/roster/${id}/check-out`)
    return res.data
  },

  getCheckpoints: async (params?: { is_active?: boolean; sector?: string }): Promise<Checkpoint[]> => {
    const res = await axiosInstance.get('/api/vigilance/checkpoints', { params })
    return res.data
  },

  createCheckpoint: async (payload: CheckpointPayload): Promise<Checkpoint> => {
    const res = await axiosInstance.post('/api/vigilance/checkpoints', payload)
    return res.data
  },

  updateCheckpoint: async (id: string, payload: CheckpointPayload): Promise<Checkpoint> => {
    const res = await axiosInstance.put(`/api/vigilance/checkpoints/${id}`, payload)
    return res.data
  },

  getPatrolLogs: async (params?: { duty_roster_id?: string; checkpoint_id?: string; guard_id?: string }): Promise<PatrolLog[]> => {
    const res = await axiosInstance.get('/api/vigilance/patrol-log', { params })
    return res.data
  },

  createPatrolLog: async (payload: PatrolLogPayload): Promise<PatrolLog> => {
    const res = await axiosInstance.post('/api/vigilance/patrol-log', payload)
    return res.data
  },

  getIncidents: async (params?: { status?: IncidentStatus; severity?: IncidentSeverity; incident_type?: string }): Promise<Incident[]> => {
    const res = await axiosInstance.get('/api/vigilance/incidents', { params })
    return res.data
  },

  createIncident: async (payload: IncidentPayload): Promise<Incident> => {
    const res = await axiosInstance.post('/api/vigilance/incidents', payload)
    return res.data
  },

  updateIncident: async (id: string, payload: IncidentUpdatePayload): Promise<Incident> => {
    const res = await axiosInstance.put(`/api/vigilance/incidents/${id}`, payload)
    return res.data
  },

  acknowledgeIncident: async (id: string) => {
    const res = await axiosInstance.post(`/api/vigilance/incidents/${id}/acknowledge`)
    return res.data
  },

  resolveIncident: async (id: string, resolution_notes: string) => {
    const res = await axiosInstance.post(`/api/vigilance/incidents/${id}/resolve`, null, { params: { resolution_notes } })
    return res.data
  },

  getSOSAlerts: async (params?: { status?: SOSStatus }): Promise<SOSAlert[]> => {
    const res = await axiosInstance.get('/api/vigilance/sos', { params })
    return res.data
  },

  createSOSAlert: async (payload: SOSPayload): Promise<SOSAlert> => {
    const res = await axiosInstance.post('/api/vigilance/sos', payload)
    return res.data
  },

  acknowledgeSOS: async (id: string) => {
    const res = await axiosInstance.post(`/api/vigilance/sos/${id}/acknowledge`)
    return res.data
  },

  resolveSOS: async (id: string, resolution_notes: string, false_alarm = false, false_alarm_reason?: string) => {
    const res = await axiosInstance.post(`/api/vigilance/sos/${id}/resolve`, null, {
      params: { resolution_notes, false_alarm, false_alarm_reason },
    })
    return res.data
  },
}

export default vigilanceService
