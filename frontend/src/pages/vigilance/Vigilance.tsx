import { useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Button,
  Stack,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Paper,
  TableContainer,
  Chip,
  Switch,
  FormControlLabel,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import vigilanceService, {
  type DashboardStats,
  type DutyRoster,
  type DutyRosterPayload,
  type ShiftType,
  type Checkpoint,
  type CheckpointPayload,
  type PatrolLog,
  type PatrolLogPayload,
  type Incident,
  type IncidentPayload,
  type IncidentSeverity,
  type SOSAlert,
  type SOSPayload,
} from '../../services/vigilanceService'

const shiftTypes: ShiftType[] = ['morning', 'evening', 'night']
const incidentSeverities: IncidentSeverity[] = ['low', 'medium', 'high', 'critical']

const isoDate = (d: Date) => d.toISOString().slice(0, 10)
const isoDateTime = (d: Date) => d.toISOString().slice(0, 16)

export default function Vigilance() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState(0)

  const [rosterForm, setRosterForm] = useState<DutyRosterPayload>({
    guard_id: '',
    guard_name: '',
    guard_phone: '',
    guard_employee_id: '',
    duty_date: isoDate(new Date()),
    shift_type: 'night',
    shift_start: isoDateTime(new Date()),
    shift_end: isoDateTime(new Date(new Date().getTime() + 6 * 60 * 60 * 1000)),
    assigned_gate: '',
    assigned_sector: '',
    patrol_route: '',
    supervisor_id: '',
    supervisor_name: '',
    special_instructions: '',
  })

  const [checkpointForm, setCheckpointForm] = useState<CheckpointPayload>({
    checkpoint_name: '',
    location_description: '',
    sector: '',
    building: '',
    floor: '',
    gps_latitude: undefined,
    gps_longitude: undefined,
    rfid_tag_id: '',
    is_critical: false,
    expected_scan_interval: undefined,
    patrol_sequence: undefined,
  })

  const [patrolForm, setPatrolForm] = useState<PatrolLogPayload>({
    duty_roster_id: '',
    checkpoint_id: '',
    scan_method: 'manual',
    guard_id: '',
    guard_name: '',
    gps_latitude: undefined,
    gps_longitude: undefined,
    observations: '',
    anomalies_found: false,
    anomaly_description: '',
  })

  const [incidentForm, setIncidentForm] = useState<IncidentPayload>({
    title: '',
    description: '',
    incident_type: '',
    severity: 'medium',
    location: '',
    incident_time: isoDateTime(new Date()),
    reported_by_guard_id: '',
    reported_by_guard_name: '',
    sector: '',
    building: '',
    floor: '',
    witnesses: '',
  })

  const [sosForm, setSosForm] = useState<SOSPayload>({
    guard_id: '',
    guard_name: '',
    guard_phone: '',
    alert_type: 'emergency',
    location: '',
    sector: '',
  })

  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ['vigilanceDashboard'],
    queryFn: vigilanceService.getDashboardStats,
  })

  const { data: rosters = [] } = useQuery<DutyRoster[]>({
    queryKey: ['vigilanceRosters'],
    queryFn: () => vigilanceService.getRosters(),
  })

  const { data: checkpoints = [] } = useQuery<Checkpoint[]>({
    queryKey: ['vigilanceCheckpoints'],
    queryFn: () => vigilanceService.getCheckpoints(),
  })

  const { data: patrolLogs = [] } = useQuery<PatrolLog[]>({
    queryKey: ['vigilancePatrols'],
    queryFn: () => vigilanceService.getPatrolLogs(),
  })

  const { data: incidents = [] } = useQuery<Incident[]>({
    queryKey: ['vigilanceIncidents'],
    queryFn: () => vigilanceService.getIncidents(),
  })

  const { data: sosAlerts = [] } = useQuery<SOSAlert[]>({
    queryKey: ['vigilanceSOS'],
    queryFn: () => vigilanceService.getSOSAlerts(),
  })

  const rosterMutation = useMutation({
    mutationFn: vigilanceService.createRoster,
    onSuccess: () => {
      toast.success('Roster saved')
      queryClient.invalidateQueries({ queryKey: ['vigilanceRosters'] })
      setRosterForm((prev) => ({
        ...prev,
        guard_id: '',
        guard_name: '',
        guard_phone: '',
        guard_employee_id: '',
        patrol_route: '',
        assigned_gate: '',
        assigned_sector: '',
        supervisor_id: '',
        supervisor_name: '',
        special_instructions: '',
      }))
    },
  })

  const checkpointMutation = useMutation({
    mutationFn: vigilanceService.createCheckpoint,
    onSuccess: () => {
      toast.success('Checkpoint saved')
      queryClient.invalidateQueries({ queryKey: ['vigilanceCheckpoints'] })
      setCheckpointForm({
        checkpoint_name: '',
        location_description: '',
        sector: '',
        building: '',
        floor: '',
        gps_latitude: undefined,
        gps_longitude: undefined,
        rfid_tag_id: '',
        is_critical: false,
        expected_scan_interval: undefined,
        patrol_sequence: undefined,
      })
    },
  })

  const patrolMutation = useMutation({
    mutationFn: vigilanceService.createPatrolLog,
    onSuccess: () => {
      toast.success('Patrol log saved')
      queryClient.invalidateQueries({ queryKey: ['vigilancePatrols'] })
      setPatrolForm({
        duty_roster_id: '',
        checkpoint_id: '',
        scan_method: 'manual',
        guard_id: '',
        guard_name: '',
        gps_latitude: undefined,
        gps_longitude: undefined,
        observations: '',
        anomalies_found: false,
        anomaly_description: '',
      })
    },
  })

  const incidentMutation = useMutation({
    mutationFn: vigilanceService.createIncident,
    onSuccess: () => {
      toast.success('Incident reported')
      queryClient.invalidateQueries({ queryKey: ['vigilanceIncidents'] })
      setIncidentForm({
        title: '',
        description: '',
        incident_type: '',
        severity: 'medium',
        location: '',
        incident_time: isoDateTime(new Date()),
        reported_by_guard_id: '',
        reported_by_guard_name: '',
        sector: '',
        building: '',
        floor: '',
        witnesses: '',
      })
    },
  })

  const incidentAckMutation = useMutation({
    mutationFn: (id: string) => vigilanceService.acknowledgeIncident(id),
    onSuccess: () => {
      toast.success('Incident acknowledged')
      queryClient.invalidateQueries({ queryKey: ['vigilanceIncidents'] })
    },
  })

  const incidentResolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => vigilanceService.resolveIncident(id, notes),
    onSuccess: () => {
      toast.success('Incident resolved')
      queryClient.invalidateQueries({ queryKey: ['vigilanceIncidents'] })
    },
  })

  const sosMutation = useMutation({
    mutationFn: vigilanceService.createSOSAlert,
    onSuccess: () => {
      toast.success('SOS alert created')
      queryClient.invalidateQueries({ queryKey: ['vigilanceSOS'] })
      setSosForm({ guard_id: '', guard_name: '', guard_phone: '', alert_type: 'emergency', location: '', sector: '' })
    },
  })

  const sosAckMutation = useMutation({
    mutationFn: (id: string) => vigilanceService.acknowledgeSOS(id),
    onSuccess: () => {
      toast.success('SOS acknowledged')
      queryClient.invalidateQueries({ queryKey: ['vigilanceSOS'] })
    },
  })

  const sosResolveMutation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => vigilanceService.resolveSOS(id, notes, false),
    onSuccess: () => {
      toast.success('SOS resolved')
      queryClient.invalidateQueries({ queryKey: ['vigilanceSOS'] })
    },
  })

  const cards = [
    { label: 'Active Patrols', value: stats?.active_patrols ?? 0 },
    { label: 'Completed Patrols Today', value: stats?.completed_patrols ?? 0 },
    { label: 'Checkpoints', value: stats?.total_checkpoints ?? 0 },
    { label: 'Incidents Today', value: stats?.incidents_today ?? 0 },
    { label: 'Open Incidents', value: stats?.incidents_open ?? 0 },
    { label: 'Active SOS', value: stats?.sos_alerts_active ?? 0 },
    { label: 'SOS Today', value: stats?.sos_alerts_today ?? 0 },
    { label: 'Missed Patrols', value: stats?.missed_patrols ?? 0 },
    { label: 'Critical Incidents', value: stats?.critical_incidents ?? 0 },
  ]

  const refreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ['vigilanceDashboard'] })
    queryClient.invalidateQueries({ queryKey: ['vigilanceRosters'] })
    queryClient.invalidateQueries({ queryKey: ['vigilanceCheckpoints'] })
    queryClient.invalidateQueries({ queryKey: ['vigilancePatrols'] })
    queryClient.invalidateQueries({ queryKey: ['vigilanceIncidents'] })
    queryClient.invalidateQueries({ queryKey: ['vigilanceSOS'] })
  }

  const renderDashboard = () => (
    <Box>
      <Grid container spacing={2} mb={3}>
        {cards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.label}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  {card.label}
                </Typography>
                <Typography variant="h5">{card.value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h6" gutterBottom>Recent Incidents</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Incident</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {incidents.slice(0, 5).map((inc) => (
              <TableRow key={inc.id}>
                <TableCell>{inc.title}</TableCell>
                <TableCell>
                  <Chip label={inc.severity} color={inc.severity === 'high' || inc.severity === 'critical' ? 'error' : 'default'} size="small" />
                </TableCell>
                <TableCell><Chip label={inc.status} size="small" /></TableCell>
                <TableCell>{new Date(inc.incident_time).toLocaleString()}</TableCell>
              </TableRow>
            ))}
            {incidents.length === 0 && (
              <TableRow><TableCell colSpan={4} align="center">No incidents</TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )

  const renderRosters = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Assign Duty</Typography>
            <Stack spacing={2}>
              <TextField label="Guard ID" value={rosterForm.guard_id} onChange={(e) => setRosterForm((p) => ({ ...p, guard_id: e.target.value }))} />
              <TextField label="Guard Name" value={rosterForm.guard_name} onChange={(e) => setRosterForm((p) => ({ ...p, guard_name: e.target.value }))} />
              <TextField label="Phone" value={rosterForm.guard_phone} onChange={(e) => setRosterForm((p) => ({ ...p, guard_phone: e.target.value }))} />
              <TextField label="Employee ID" value={rosterForm.guard_employee_id} onChange={(e) => setRosterForm((p) => ({ ...p, guard_employee_id: e.target.value }))} />
              <TextField
                label="Duty Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={rosterForm.duty_date}
                onChange={(e) => setRosterForm((p) => ({ ...p, duty_date: e.target.value }))}
              />
              <FormControl fullWidth>
                <InputLabel>Shift</InputLabel>
                <Select
                  label="Shift"
                  value={rosterForm.shift_type}
                  onChange={(e) => setRosterForm((p) => ({ ...p, shift_type: e.target.value as ShiftType }))}
                >
                  {shiftTypes.map((s) => (
                    <MenuItem key={s} value={s}>{s}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                label="Shift Start"
                type="datetime-local"
                InputLabelProps={{ shrink: true }}
                value={rosterForm.shift_start}
                onChange={(e) => setRosterForm((p) => ({ ...p, shift_start: e.target.value }))}
              />
              <TextField
                label="Shift End"
                type="datetime-local"
                InputLabelProps={{ shrink: true }}
                value={rosterForm.shift_end}
                onChange={(e) => setRosterForm((p) => ({ ...p, shift_end: e.target.value }))}
              />
              <TextField label="Gate" value={rosterForm.assigned_gate} onChange={(e) => setRosterForm((p) => ({ ...p, assigned_gate: e.target.value }))} />
              <TextField label="Sector" value={rosterForm.assigned_sector} onChange={(e) => setRosterForm((p) => ({ ...p, assigned_sector: e.target.value }))} />
              <TextField label="Patrol Route (IDs)" value={rosterForm.patrol_route} onChange={(e) => setRosterForm((p) => ({ ...p, patrol_route: e.target.value }))} />
              <TextField label="Supervisor" value={rosterForm.supervisor_name} onChange={(e) => setRosterForm((p) => ({ ...p, supervisor_name: e.target.value }))} />
              <TextField label="Instructions" multiline minRows={2} value={rosterForm.special_instructions} onChange={(e) => setRosterForm((p) => ({ ...p, special_instructions: e.target.value }))} />
              <Button variant="contained" onClick={() => rosterMutation.mutate(rosterForm)} disabled={rosterMutation.isPending}>Save Roster</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Duty Rosters</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Roster #</TableCell>
                    <TableCell>Guard</TableCell>
                    <TableCell>Shift</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rosters.map((r) => (
                    <TableRow key={r.id}>
                      <TableCell>{r.roster_number}</TableCell>
                      <TableCell>{r.guard_name}</TableCell>
                      <TableCell>{r.shift_type}</TableCell>
                      <TableCell><Chip label={r.status} size="small" /></TableCell>
                      <TableCell>{new Date(r.duty_date).toLocaleDateString()}</TableCell>
                    </TableRow>
                  ))}
                  {rosters.length === 0 && (
                    <TableRow><TableCell colSpan={5} align="center">No rosters</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderCheckpoints = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>New Checkpoint</Typography>
            <Stack spacing={2}>
              <TextField label="Name" value={checkpointForm.checkpoint_name} onChange={(e) => setCheckpointForm((p) => ({ ...p, checkpoint_name: e.target.value }))} />
              <TextField label="Location" value={checkpointForm.location_description} onChange={(e) => setCheckpointForm((p) => ({ ...p, location_description: e.target.value }))} />
              <TextField label="Sector" value={checkpointForm.sector} onChange={(e) => setCheckpointForm((p) => ({ ...p, sector: e.target.value }))} />
              <TextField label="Building" value={checkpointForm.building} onChange={(e) => setCheckpointForm((p) => ({ ...p, building: e.target.value }))} />
              <TextField label="Floor" value={checkpointForm.floor} onChange={(e) => setCheckpointForm((p) => ({ ...p, floor: e.target.value }))} />
              <TextField label="RFID" value={checkpointForm.rfid_tag_id} onChange={(e) => setCheckpointForm((p) => ({ ...p, rfid_tag_id: e.target.value }))} />
              <TextField label="Expected Interval (min)" type="number" value={checkpointForm.expected_scan_interval ?? ''} onChange={(e) => setCheckpointForm((p) => ({ ...p, expected_scan_interval: e.target.value ? Number(e.target.value) : undefined }))} />
              <TextField label="Patrol Sequence" type="number" value={checkpointForm.patrol_sequence ?? ''} onChange={(e) => setCheckpointForm((p) => ({ ...p, patrol_sequence: e.target.value ? Number(e.target.value) : undefined }))} />
              <FormControlLabel
                control={<Switch checked={checkpointForm.is_critical || false} onChange={(e) => setCheckpointForm((p) => ({ ...p, is_critical: e.target.checked }))} />}
                label="Critical"
              />
              <Button variant="contained" onClick={() => checkpointMutation.mutate(checkpointForm)} disabled={checkpointMutation.isPending}>Save Checkpoint</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Checkpoints</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Sector</TableCell>
                    <TableCell>Critical</TableCell>
                    <TableCell>QR</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {checkpoints.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.checkpoint_number}</TableCell>
                      <TableCell>{c.checkpoint_name}</TableCell>
                      <TableCell>{c.sector || '-'}</TableCell>
                      <TableCell><Chip label={c.is_critical ? 'Yes' : 'No'} color={c.is_critical ? 'warning' : 'default'} size="small" /></TableCell>
                      <TableCell>{c.qr_code ? 'QR Ready' : '-'}</TableCell>
                    </TableRow>
                  ))}
                  {checkpoints.length === 0 && (
                    <TableRow><TableCell colSpan={5} align="center">No checkpoints</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderPatrols = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Log Patrol</Typography>
            <Stack spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Roster</InputLabel>
                <Select
                  label="Roster"
                  value={patrolForm.duty_roster_id}
                  onChange={(e) => setPatrolForm((p) => ({ ...p, duty_roster_id: e.target.value }))}
                >
                  {rosters.map((r) => (
                    <MenuItem key={r.id} value={r.id}>{r.roster_number}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Checkpoint</InputLabel>
                <Select
                  label="Checkpoint"
                  value={patrolForm.checkpoint_id}
                  onChange={(e) => setPatrolForm((p) => ({ ...p, checkpoint_id: e.target.value }))}
                >
                  {checkpoints.map((c) => (
                    <MenuItem key={c.id} value={c.id}>{c.checkpoint_name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField label="Guard ID" value={patrolForm.guard_id} onChange={(e) => setPatrolForm((p) => ({ ...p, guard_id: e.target.value }))} />
              <TextField label="Guard Name" value={patrolForm.guard_name} onChange={(e) => setPatrolForm((p) => ({ ...p, guard_name: e.target.value }))} />
              <TextField label="Scan Method" value={patrolForm.scan_method} onChange={(e) => setPatrolForm((p) => ({ ...p, scan_method: e.target.value }))} />
              <TextField label="Observations" value={patrolForm.observations} onChange={(e) => setPatrolForm((p) => ({ ...p, observations: e.target.value }))} />
              <FormControlLabel
                control={<Switch checked={patrolForm.anomalies_found || false} onChange={(e) => setPatrolForm((p) => ({ ...p, anomalies_found: e.target.checked }))} />}
                label="Anomaly"
              />
              <TextField label="Anomaly Description" value={patrolForm.anomaly_description} onChange={(e) => setPatrolForm((p) => ({ ...p, anomaly_description: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                if (!patrolForm.duty_roster_id || !patrolForm.checkpoint_id || !patrolForm.guard_id) {
                  toast.error('Roster, checkpoint, and guard are required')
                  return
                }
                patrolMutation.mutate(patrolForm)
              }} disabled={patrolMutation.isPending}>Save Log</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Patrol Logs</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Log #</TableCell>
                    <TableCell>Roster</TableCell>
                    <TableCell>Checkpoint</TableCell>
                    <TableCell>Guard</TableCell>
                    <TableCell>Time</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {patrolLogs.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell>{p.log_number}</TableCell>
                      <TableCell>{p.duty_roster_id}</TableCell>
                      <TableCell>{p.checkpoint_id}</TableCell>
                      <TableCell>{p.guard_name || p.guard_id}</TableCell>
                      <TableCell>{new Date(p.scan_time).toLocaleString()}</TableCell>
                      <TableCell><Chip label={p.status} size="small" /></TableCell>
                    </TableRow>
                  ))}
                  {patrolLogs.length === 0 && (
                    <TableRow><TableCell colSpan={6} align="center">No patrol logs</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderIncidents = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Report Incident</Typography>
            <Stack spacing={2}>
              <TextField label="Title" value={incidentForm.title} onChange={(e) => setIncidentForm((p) => ({ ...p, title: e.target.value }))} />
              <TextField label="Type" value={incidentForm.incident_type} onChange={(e) => setIncidentForm((p) => ({ ...p, incident_type: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  label="Severity"
                  value={incidentForm.severity}
                  onChange={(e) => setIncidentForm((p) => ({ ...p, severity: e.target.value as IncidentSeverity }))}
                >
                  {incidentSeverities.map((s) => (
                    <MenuItem key={s} value={s}>{s}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField label="Location" value={incidentForm.location} onChange={(e) => setIncidentForm((p) => ({ ...p, location: e.target.value }))} />
              <TextField label="Sector" value={incidentForm.sector} onChange={(e) => setIncidentForm((p) => ({ ...p, sector: e.target.value }))} />
              <TextField label="Building" value={incidentForm.building} onChange={(e) => setIncidentForm((p) => ({ ...p, building: e.target.value }))} />
              <TextField label="Floor" value={incidentForm.floor} onChange={(e) => setIncidentForm((p) => ({ ...p, floor: e.target.value }))} />
              <TextField
                label="Incident Time"
                type="datetime-local"
                InputLabelProps={{ shrink: true }}
                value={incidentForm.incident_time}
                onChange={(e) => setIncidentForm((p) => ({ ...p, incident_time: e.target.value }))}
              />
              <TextField label="Guard ID" value={incidentForm.reported_by_guard_id} onChange={(e) => setIncidentForm((p) => ({ ...p, reported_by_guard_id: e.target.value }))} />
              <TextField label="Guard Name" value={incidentForm.reported_by_guard_name} onChange={(e) => setIncidentForm((p) => ({ ...p, reported_by_guard_name: e.target.value }))} />
              <TextField label="Description" multiline minRows={3} value={incidentForm.description} onChange={(e) => setIncidentForm((p) => ({ ...p, description: e.target.value }))} />
              <TextField label="Witnesses" value={incidentForm.witnesses} onChange={(e) => setIncidentForm((p) => ({ ...p, witnesses: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                if (!incidentForm.title || !incidentForm.incident_type || !incidentForm.location || !incidentForm.reported_by_guard_id) {
                  toast.error('Title, type, location, and guard are required')
                  return
                }
                incidentMutation.mutate(incidentForm)
              }} disabled={incidentMutation.isPending}>Submit Incident</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Incidents</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Time</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {incidents.map((i) => (
                    <TableRow key={i.id}>
                      <TableCell>{i.incident_number}</TableCell>
                      <TableCell>{i.title}</TableCell>
                      <TableCell><Chip label={i.severity} color={i.severity === 'high' || i.severity === 'critical' ? 'error' : 'default'} size="small" /></TableCell>
                      <TableCell><Chip label={i.status} size="small" /></TableCell>
                      <TableCell>{new Date(i.incident_time).toLocaleString()}</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          {i.status === 'reported' && (
                            <Button size="small" onClick={() => incidentAckMutation.mutate(i.id)}>Acknowledge</Button>
                          )}
                          {i.status !== 'resolved' && i.status !== 'closed' && (
                            <Button size="small" onClick={() => incidentResolveMutation.mutate({ id: i.id, notes: 'Resolved via console' })}>Resolve</Button>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                  {incidents.length === 0 && (
                    <TableRow><TableCell colSpan={6} align="center">No incidents</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderSOS = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>SOS Alert</Typography>
            <Stack spacing={2}>
              <TextField label="Guard ID" value={sosForm.guard_id} onChange={(e) => setSosForm((p) => ({ ...p, guard_id: e.target.value }))} />
              <TextField label="Guard Name" value={sosForm.guard_name} onChange={(e) => setSosForm((p) => ({ ...p, guard_name: e.target.value }))} />
              <TextField label="Phone" value={sosForm.guard_phone} onChange={(e) => setSosForm((p) => ({ ...p, guard_phone: e.target.value }))} />
              <TextField label="Alert Type" value={sosForm.alert_type} onChange={(e) => setSosForm((p) => ({ ...p, alert_type: e.target.value }))} />
              <TextField label="Location" value={sosForm.location} onChange={(e) => setSosForm((p) => ({ ...p, location: e.target.value }))} />
              <TextField label="Sector" value={sosForm.sector} onChange={(e) => setSosForm((p) => ({ ...p, sector: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                if (!sosForm.guard_id || !sosForm.guard_name) {
                  toast.error('Guard ID and name are required')
                  return
                }
                sosMutation.mutate(sosForm)
              }} disabled={sosMutation.isPending}>Send SOS</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>SOS Alerts</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Guard</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Time</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sosAlerts.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>{s.alert_number}</TableCell>
                      <TableCell>{s.guard_name}</TableCell>
                      <TableCell>{s.alert_type}</TableCell>
                      <TableCell><Chip label={s.status} size="small" color={s.status === 'active' ? 'error' : s.status === 'responding' ? 'warning' : 'default'} /></TableCell>
                      <TableCell>{new Date(s.alert_time).toLocaleString()}</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          {s.status === 'active' && (
                            <Button size="small" onClick={() => sosAckMutation.mutate(s.id)}>Acknowledge</Button>
                          )}
                          {s.status !== 'resolved' && s.status !== 'false_alarm' && (
                            <Button size="small" onClick={() => sosResolveMutation.mutate({ id: s.id, notes: 'Resolved' })}>Resolve</Button>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                  {sosAlerts.length === 0 && (
                    <TableRow><TableCell colSpan={6} align="center">No SOS alerts</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight={600}>Night Vigilance Reporting</Typography>
          <Typography variant="body1" color="text.secondary">Security patrol tracking, incidents, and SOS response</Typography>
        </Box>
        <Button variant="outlined" onClick={refreshAll}>Refresh</Button>
      </Box>

      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Dashboard" />
        <Tab label="Duty Rosters" />
        <Tab label="Checkpoints" />
        <Tab label="Patrol Logs" />
        <Tab label="Incidents" />
        <Tab label="SOS Alerts" />
      </Tabs>

      {activeTab === 0 && renderDashboard()}
      {activeTab === 1 && renderRosters()}
      {activeTab === 2 && renderCheckpoints()}
      {activeTab === 3 && renderPatrols()}
      {activeTab === 4 && renderIncidents()}
      {activeTab === 5 && renderSOS()}
    </Box>
  )
}
