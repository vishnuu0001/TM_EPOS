import { useEffect, useState } from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Stack,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper,
  TableContainer,
  Chip,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import equipmentService from '../../services/equipmentService'

const equipmentTypes = [
  'CRANE',
  'FORKLIFT',
  'EXCAVATOR',
  'LOADER',
  'TRUCK',
  'GENERATOR',
  'OTHER',
]

const manufacturerOptions = ['AutoGen', 'Caterpillar', 'Toyota', 'Volvo', 'Komatsu', 'Other']
const modelOptions = ['Model-10', 'Model-20', 'Model-30', 'Model-40', 'Model-50', 'Other']
const capacityOptions = ['5 Ton', '10 Ton', '20 Ton', '50 Ton', '100 Ton', 'Other']
const locationOptions = ['Plant Yard', 'Bay 1', 'Bay 2', 'Warehouse', 'Workshop', 'Site A', 'Site B', 'Other']
const costCenterOptions = ['CC-Plant', 'CC-Yard', 'CC-Warehouse', 'CC-Workshop', 'CC-SiteA', 'CC-SiteB']

const bookingStatuses = [
  'REQUESTED',
  'APPROVED',
  'ACTIVE',
  'COMPLETED',
  'CANCELLED',
]

export default function Equipment() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState(0)
  const [equipmentPage, setEquipmentPage] = useState(0)
  const [equipmentRowsPerPage, setEquipmentRowsPerPage] = useState(10)
  const [bookingListPage, setBookingListPage] = useState(0)
  const [bookingListRowsPerPage, setBookingListRowsPerPage] = useState(10)
  const [maintenancePage, setMaintenancePage] = useState(0)
  const [maintenanceRowsPerPage, setMaintenanceRowsPerPage] = useState(10)
  const [certsPage, setCertsPage] = useState(0)
  const [certsRowsPerPage, setCertsRowsPerPage] = useState(10)

  const [equipmentForm, setEquipmentForm] = useState({
    equipment_number: '',
    name: '',
    equipment_type: 'CRANE',
    manufacturer: '',
    model: '',
    capacity: '',
    location: '',
    hourly_rate: undefined,
    requires_certification: true,
    description: '',
  })

  const [bookingForm, setBookingForm] = useState({
    equipment_id: '',
    operator_id: '',
    start_time: '',
    end_time: '',
    purpose: '',
    location: '',
    cost_center: '',
  })

  const [maintenanceForm, setMaintenanceForm] = useState({
    equipment_id: '',
    maintenance_type: '',
    description: '',
    scheduled_date: '',
    next_service_hours: undefined,
    next_service_date: '',
  })

  const [maintenanceCompleteOpen, setMaintenanceCompleteOpen] = useState(false)
  const [maintenanceCompleteId, setMaintenanceCompleteId] = useState(null)
  const [maintenanceCompleteForm, setMaintenanceCompleteForm] = useState({
    completed_date: '',
    performed_by: '',
    cost: undefined,
    notes: '',
  })

  const [certForm, setCertForm] = useState({
    operator_id: '',
    equipment_type: 'CRANE',
    certification_number: '',
    issued_date: '',
    expiry_date: '',
    issuing_authority: '',
  })

  const { data: stats } = useQuery({
    queryKey: ['equipmentDashboard'],
    queryFn: equipmentService.getDashboardStats,
  })

  const { data: equipment = [] } = useQuery({
    queryKey: ['equipmentList'],
    queryFn: async () => {
      const data = await equipmentService.getEquipment({ limit: 2000 })
      return data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    },
  })

  const { data: bookings = [] } = useQuery({
    queryKey: ['equipmentBookings'],
    queryFn: () => equipmentService.getBookings(),
  })

  const { data: maintenance = [] } = useQuery({
    queryKey: ['equipmentMaintenance'],
    queryFn: () => equipmentService.getMaintenance(),
  })

  const { data: certifications = [] } = useQuery({
    queryKey: ['equipmentCertifications'],
    queryFn: () => equipmentService.getCertifications(),
  })

  const getCertifiedOperators = (equipmentId) => {
    const selectedEquipment = equipment.find((e) => e.id === equipmentId)
    if (!selectedEquipment || !selectedEquipment.requires_certification) {
      return []
    }
    return certifications
      .filter((c) => c.is_active && c.equipment_type === selectedEquipment.equipment_type)
      .map((c) => c.operator_id)
  }

  useEffect(() => {
    if (!bookingForm.equipment_id) {
      if (bookingForm.operator_id) {
        setBookingForm((p) => ({ ...p, operator_id: '' }))
      }
      return
    }
    const operators = getCertifiedOperators(bookingForm.equipment_id)
    if (operators.length === 0 || !operators.includes(bookingForm.operator_id)) {
      setBookingForm((p) => ({ ...p, operator_id: '' }))
    }
  }, [bookingForm.equipment_id, certifications])

  useEffect(() => {
    if (bookingForm.cost_center && !costCenterOptions.includes(bookingForm.cost_center)) {
      setBookingForm((p) => ({ ...p, cost_center: '' }))
    }
  }, [bookingForm.cost_center])

  const createEquipmentMutation = useMutation({
    mutationFn: equipmentService.createEquipment,
    onSuccess: (created) => {
      toast.success('Equipment saved')
      queryClient.setQueryData(['equipmentList'], (prev) => {
        if (!prev) return [created]
        return [created, ...prev]
      })
      queryClient.invalidateQueries({ queryKey: ['equipmentList'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
      setEquipmentPage(0)
      setEquipmentForm({
        equipment_number: '',
        name: '',
        equipment_type: 'CRANE',
        manufacturer: '',
        model: '',
        capacity: '',
        location: '',
        hourly_rate: undefined,
        requires_certification: true,
        description: '',
      })
    },
  })

  const createBookingMutation = useMutation({
    mutationFn: equipmentService.createBooking,
    onSuccess: (created) => {
      toast.success('Booking created')
      queryClient.setQueryData(['equipmentBookings'], (prev) => {
        if (!prev) return [created]
        return [created, ...prev]
      })
      queryClient.invalidateQueries({ queryKey: ['equipmentBookings'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
      setBookingsPage(0)
      setBookingForm({
        equipment_id: '',
        operator_id: '',
        start_time: '',
        end_time: '',
        purpose: '',
        location: '',
        cost_center: '',
      })
    },
  })

  const approveBookingMutation = useMutation({
    mutationFn: (id) => equipmentService.approveBooking(id),
    onSuccess: () => {
      toast.success('Booking approved')
      queryClient.invalidateQueries({ queryKey: ['equipmentBookings'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
    },
  })

  const updateBookingStatusMutation = useMutation({
    mutationFn: ({ id, status }) => equipmentService.updateBooking(id, { status }),
    onSuccess: () => {
      toast.success('Booking updated')
      queryClient.invalidateQueries({ queryKey: ['equipmentBookings'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentList'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
    },
  })

  const createMaintenanceMutation = useMutation({
    mutationFn: equipmentService.createMaintenance,
    onSuccess: () => {
      toast.success('Maintenance added')
      queryClient.invalidateQueries({ queryKey: ['equipmentMaintenance'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentList'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
      setMaintenanceForm({
        equipment_id: '',
        maintenance_type: '',
        description: '',
        scheduled_date: '',
        next_service_hours: undefined,
        next_service_date: '',
      })
    },
  })

  const updateMaintenanceMutation = useMutation({
    mutationFn: ({ id, payload }) => equipmentService.updateMaintenance(id, payload),
    onSuccess: () => {
      toast.success('Maintenance updated')
      queryClient.invalidateQueries({ queryKey: ['equipmentMaintenance'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentList'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
      setMaintenanceCompleteOpen(false)
      setMaintenanceCompleteId(null)
      setMaintenanceCompleteForm({ completed_date: '', performed_by: '', cost: undefined, notes: '' })
    },
  })

  const createCertificationMutation = useMutation({
    mutationFn: equipmentService.createCertification,
    onSuccess: () => {
      toast.success('Certification saved')
      queryClient.invalidateQueries({ queryKey: ['equipmentCertifications'] })
      queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
      setCertForm({
        operator_id: '',
        equipment_type: 'CRANE',
        certification_number: '',
        issued_date: '',
        expiry_date: '',
        issuing_authority: '',
      })
    },
  })

  const handleCreateEquipment = () => {
    if (!equipmentForm.equipment_number || !equipmentForm.name) {
      toast.error('Equipment number and name are required')
      return
    }
    createEquipmentMutation.mutate(equipmentForm)
  }

  const handleCreateBooking = () => {
    if (!bookingForm.equipment_id || !bookingForm.operator_id || !bookingForm.start_time || !bookingForm.end_time || !bookingForm.purpose) {
      toast.error('Equipment, operator, start/end, and purpose are required')
      return
    }
    const selectedEquipment = equipment.find((e) => e.id === bookingForm.equipment_id)
    if (selectedEquipment?.requires_certification) {
      const hasCert = certifications.some(
        (c) => c.operator_id === bookingForm.operator_id && c.equipment_type === selectedEquipment.equipment_type && c.is_active,
      )
      if (!hasCert) {
        toast.error('Operator is not certified for the selected equipment')
        return
      }
    }
    createBookingMutation.mutate(bookingForm)
  }

  const openCompleteMaintenance = (maintenanceId) => {
    setMaintenanceCompleteId(maintenanceId)
    setMaintenanceCompleteForm({
      completed_date: new Date().toISOString().slice(0, 10),
      performed_by: '',
      cost: undefined,
      notes: '',
    })
    setMaintenanceCompleteOpen(true)
  }

  const handleCompleteMaintenance = () => {
    if (!maintenanceCompleteId || !maintenanceCompleteForm.completed_date) return
    updateMaintenanceMutation.mutate({
      id: maintenanceCompleteId,
      payload: {
        completed_date: maintenanceCompleteForm.completed_date,
        performed_by: maintenanceCompleteForm.performed_by || undefined,
        cost: maintenanceCompleteForm.cost,
        notes: maintenanceCompleteForm.notes?.trim() ? maintenanceCompleteForm.notes.trim() : undefined,
      },
    })
  }

  const handleCreateMaintenance = () => {
    if (!maintenanceForm.equipment_id || !maintenanceForm.maintenance_type || !maintenanceForm.scheduled_date) {
      toast.error('Equipment, maintenance type, and date are required')
      return
    }
    createMaintenanceMutation.mutate(maintenanceForm)
  }

  const handleCreateCertification = () => {
    if (!certForm.operator_id || !certForm.certification_number || !certForm.issued_date || !certForm.expiry_date) {
      toast.error('Operator, certification number, issued and expiry dates are required')
      return
    }
    createCertificationMutation.mutate(certForm)
  }

  const renderDashboard = () => {
    const cards = [
      { label: 'Total Equipment', value: stats?.total_equipment ?? 0 },
      { label: 'Available', value: stats?.available_equipment ?? 0 },
      { label: 'In Use', value: stats?.in_use_equipment ?? 0 },
      { label: 'Maintenance', value: stats?.maintenance_equipment ?? 0 },
      { label: 'Bookings', value: stats?.total_bookings ?? 0 },
      { label: 'Active Bookings', value: stats?.active_bookings ?? 0 },
      { label: 'Pending Approvals', value: stats?.pending_approvals ?? 0 },
      { label: 'Utilization %', value: (stats?.utilization_rate ?? 0).toFixed(1) },
      { label: 'Pending Maintenance', value: stats?.pending_maintenance ?? 0 },
      { label: 'Expired Certs', value: stats?.expired_certifications ?? 0 },
    ]

    return (
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

        <Typography variant="h6" gutterBottom>Recent Bookings</Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Booking #</TableCell>
                <TableCell>Equipment</TableCell>
                <TableCell>Operator</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Start</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bookings.slice(0, 5).map((b) => (
                <TableRow key={b.id}>
                  <TableCell>{b.booking_number}</TableCell>
                  <TableCell>{equipment.find((e) => e.id === b.equipment_id)?.name || 'N/A'}</TableCell>
                  <TableCell>{b.operator_id}</TableCell>
                  <TableCell>
                    <Chip label={b.status} color={b.status === 'APPROVED' || b.status === 'ACTIVE' ? 'success' : 'default'} size="small" />
                  </TableCell>
                  <TableCell>{new Date(b.start_time).toLocaleString()}</TableCell>
                </TableRow>
              ))}
              {bookings.length === 0 && (
                <TableRow><TableCell colSpan={5} align="center">No bookings</TableCell></TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    )
  }

  const renderEquipmentTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>New Equipment</Typography>
            <Stack spacing={2}>
              <TextField label="Equipment Number" value={equipmentForm.equipment_number} onChange={(e) => setEquipmentForm((p) => ({ ...p, equipment_number: e.target.value }))} />
              <TextField label="Name" value={equipmentForm.name} onChange={(e) => setEquipmentForm((p) => ({ ...p, name: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  label="Type"
                  value={equipmentForm.equipment_type}
                  onChange={(e) => setEquipmentForm((p) => ({ ...p, equipment_type: e.target.value }))}
                >
                  {equipmentTypes.map((t) => (
                    <MenuItem key={t} value={t}>{t}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                select
                label="Manufacturer"
                value={equipmentForm.manufacturer}
                onChange={(e) => setEquipmentForm((p) => ({ ...p, manufacturer: e.target.value }))}
              >
                {manufacturerOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Model"
                value={equipmentForm.model}
                onChange={(e) => setEquipmentForm((p) => ({ ...p, model: e.target.value }))}
              >
                {modelOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Capacity"
                value={equipmentForm.capacity}
                onChange={(e) => setEquipmentForm((p) => ({ ...p, capacity: e.target.value }))}
              >
                {capacityOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Location"
                value={equipmentForm.location}
                onChange={(e) => setEquipmentForm((p) => ({ ...p, location: e.target.value }))}
              >
                {locationOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
              <TextField label="Hourly Rate" type="number" value={equipmentForm.hourly_rate ?? ''} onChange={(e) => setEquipmentForm((p) => ({ ...p, hourly_rate: e.target.value ? Number(e.target.value) : undefined }))} />
              <TextField label="Description" multiline minRows={2} value={equipmentForm.description} onChange={(e) => setEquipmentForm((p) => ({ ...p, description: e.target.value }))} />
              <Button variant="contained" onClick={handleCreateEquipment} disabled={createEquipmentMutation.isPending}>Save Equipment</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Fleet</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Location</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {equipment
                    .slice(equipmentPage * equipmentRowsPerPage, equipmentPage * equipmentRowsPerPage + equipmentRowsPerPage)
                    .map((e) => (
                    <TableRow key={e.id}>
                      <TableCell>{e.equipment_number}</TableCell>
                      <TableCell>{e.name}</TableCell>
                      <TableCell>{e.equipment_type}</TableCell>
                      <TableCell>
                        <Chip label={e.status} color={e.status === 'AVAILABLE' ? 'success' : e.status === 'IN_USE' ? 'warning' : 'default'} size="small" />
                      </TableCell>
                      <TableCell>{e.location || '-'}</TableCell>
                    </TableRow>
                  ))}
                  {equipment.length === 0 && (
                    <TableRow><TableCell colSpan={5} align="center">No equipment</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={equipment.length}
              page={equipmentPage}
              onPageChange={(_, page) => setEquipmentPage(page)}
              rowsPerPage={equipmentRowsPerPage}
              onRowsPerPageChange={(e) => {
                setEquipmentRowsPerPage(parseInt(e.target.value, 10))
                setEquipmentPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderBookingsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>New Booking</Typography>
            <Stack spacing={2}>
              {(() => {
                const operators = getCertifiedOperators(bookingForm.equipment_id)
                const selectedOperator = operators.includes(bookingForm.operator_id)
                  ? bookingForm.operator_id
                  : ''
                return (
                  <>
              <FormControl fullWidth>
                <InputLabel>Equipment</InputLabel>
                <Select
                  label="Equipment"
                  value={bookingForm.equipment_id}
                  onChange={(e) => {
                    const equipmentId = e.target.value
                    const certifiedOperators = getCertifiedOperators(equipmentId)
                    setBookingForm((p) => ({
                      ...p,
                      equipment_id: equipmentId,
                      operator_id: certifiedOperators.includes(p.operator_id) ? p.operator_id : '',
                    }))
                  }}
                >
                  {equipment.map((e) => (
                    <MenuItem key={e.id} value={e.id}>{e.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Operator</InputLabel>
                <Select
                  label="Operator"
                  value={selectedOperator}
                  onChange={(e) => setBookingForm((p) => ({ ...p, operator_id: e.target.value }))}
                  disabled={!bookingForm.equipment_id}
                >
                  <MenuItem value="">
                    {operators.length === 0 ? 'No certified operators' : 'Select operator'}
                  </MenuItem>
                  {operators.map((operatorId) => (
                    <MenuItem key={operatorId} value={operatorId}>{operatorId}</MenuItem>
                  ))}
                </Select>
              </FormControl>
                  </>
                )
              })()}
              <TextField
                label="Start"
                type="datetime-local"
                InputLabelProps={{ shrink: true }}
                value={bookingForm.start_time}
                onChange={(e) => setBookingForm((p) => ({ ...p, start_time: e.target.value }))}
              />
              <TextField
                label="End"
                type="datetime-local"
                InputLabelProps={{ shrink: true }}
                value={bookingForm.end_time}
                onChange={(e) => setBookingForm((p) => ({ ...p, end_time: e.target.value }))}
              />
              <TextField label="Purpose" value={bookingForm.purpose} onChange={(e) => setBookingForm((p) => ({ ...p, purpose: e.target.value }))} />
              <TextField label="Location" value={bookingForm.location} onChange={(e) => setBookingForm((p) => ({ ...p, location: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Cost Center</InputLabel>
                <Select
                  label="Cost Center"
                  value={costCenterOptions.includes(bookingForm.cost_center || '') ? bookingForm.cost_center : ''}
                  onChange={(e) => setBookingForm((p) => ({ ...p, cost_center: e.target.value }))}
                >
                  <MenuItem value="">Select cost center</MenuItem>
                  {costCenterOptions.map((option) => (
                    <MenuItem key={option} value={option}>{option}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button variant="contained" onClick={handleCreateBooking} disabled={createBookingMutation.isPending}>Create Booking</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Bookings</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Equipment</TableCell>
                    <TableCell>Operator</TableCell>
                    <TableCell>Compliance</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Start</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bookings
                    .slice(bookingListPage * bookingListRowsPerPage, bookingListPage * bookingListRowsPerPage + bookingListRowsPerPage)
                    .map((b) => (
                    <TableRow key={b.id}>
                      <TableCell>{b.booking_number}</TableCell>
                      <TableCell>{equipment.find((e) => e.id === b.equipment_id)?.name || 'N/A'}</TableCell>
                      <TableCell>{b.operator_id}</TableCell>
                      <TableCell>
                        {(() => {
                          const bookedEquipment = equipment.find((e) => e.id === b.equipment_id)
                          if (!bookedEquipment?.requires_certification) {
                            return <Chip label="Not required" size="small" />
                          }
                          const certified = certifications.some(
                            (c) => c.operator_id === b.operator_id && c.equipment_type === bookedEquipment.equipment_type && c.is_active,
                          )
                          return (
                            <Chip label={certified ? 'Certified' : 'Not certified'} color={certified ? 'success' : 'error'} size="small" />
                          )
                        })()}
                      </TableCell>
                      <TableCell>
                        <Chip label={b.status} size="small" color={b.status === 'ACTIVE' ? 'warning' : b.status === 'COMPLETED' ? 'success' : 'default'} />
                      </TableCell>
                      <TableCell>{new Date(b.start_time).toLocaleString()}</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          {b.status === 'REQUESTED' && (
                            <Button size="small" onClick={() => approveBookingMutation.mutate(b.id)}>Approve</Button>
                          )}
                          {b.status === 'REQUESTED' && (
                            <Button size="small" color="error" onClick={() => updateBookingStatusMutation.mutate({ id: b.id, status: 'CANCELLED' })}>
                              Reject
                            </Button>
                          )}
                          {b.status === 'APPROVED' && (
                            <Button size="small" onClick={() => updateBookingStatusMutation.mutate({ id: b.id, status: 'ACTIVE' })}>
                              Start
                            </Button>
                          )}
                          {b.status === 'ACTIVE' && (
                            <Button size="small" onClick={() => updateBookingStatusMutation.mutate({ id: b.id, status: 'COMPLETED' })}>
                              Complete
                            </Button>
                          )}
                          {b.status !== 'COMPLETED' && b.status !== 'CANCELLED' && (
                            <FormControl size="small" sx={{ minWidth: 140 }}>
                              <Select
                                value={b.status}
                                onChange={(e) => updateBookingStatusMutation.mutate({ id: b.id, status: e.target.value })}
                              >
                                {bookingStatuses.map((s) => (
                                  <MenuItem key={s} value={s}>{s}</MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                  {bookings.length === 0 && (
                    <TableRow><TableCell colSpan={7} align="center">No bookings</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={bookings.length}
              page={bookingListPage}
              onPageChange={(_, page) => setBookingListPage(page)}
              rowsPerPage={bookingListRowsPerPage}
              onRowsPerPageChange={(e) => {
                setBookingListRowsPerPage(parseInt(e.target.value, 10))
                setBookingListPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderMaintenanceTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Schedule Maintenance</Typography>
            <Stack spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Equipment</InputLabel>
                <Select
                  label="Equipment"
                  value={maintenanceForm.equipment_id}
                  onChange={(e) => setMaintenanceForm((p) => ({ ...p, equipment_id: e.target.value }))}
                >
                  {equipment.map((e) => (
                    <MenuItem key={e.id} value={e.id}>{e.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField label="Type" value={maintenanceForm.maintenance_type} onChange={(e) => setMaintenanceForm((p) => ({ ...p, maintenance_type: e.target.value }))} />
              <TextField label="Description" multiline minRows={2} value={maintenanceForm.description} onChange={(e) => setMaintenanceForm((p) => ({ ...p, description: e.target.value }))} />
              <TextField
                label="Scheduled Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={maintenanceForm.scheduled_date}
                onChange={(e) => setMaintenanceForm((p) => ({ ...p, scheduled_date: e.target.value }))}
              />
              <TextField label="Next Service Hours" type="number" value={maintenanceForm.next_service_hours ?? ''} onChange={(e) => setMaintenanceForm((p) => ({ ...p, next_service_hours: e.target.value ? Number(e.target.value) : undefined }))} />
              <TextField
                label="Next Service Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={maintenanceForm.next_service_date || ''}
                onChange={(e) => setMaintenanceForm((p) => ({ ...p, next_service_date: e.target.value }))}
              />
              <Button variant="contained" onClick={handleCreateMaintenance} disabled={createMaintenanceMutation.isPending}>Schedule</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Maintenance</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Equipment</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Scheduled</TableCell>
                    <TableCell>Completed</TableCell>
                    <TableCell>Cost</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {maintenance
                    .slice(maintenancePage * maintenanceRowsPerPage, maintenancePage * maintenanceRowsPerPage + maintenanceRowsPerPage)
                    .map((m) => (
                    <TableRow key={m.id}>
                      <TableCell>{equipment.find((e) => e.id === m.equipment_id)?.name || 'N/A'}</TableCell>
                      <TableCell>{m.maintenance_type}</TableCell>
                      <TableCell>{new Date(m.scheduled_date).toLocaleDateString()}</TableCell>
                      <TableCell>{m.completed_date ? new Date(m.completed_date).toLocaleDateString() : '-'}</TableCell>
                      <TableCell>{m.cost ? `₹${m.cost}` : '-'}</TableCell>
                      <TableCell>
                        {m.completed_date ? '-' : (
                          <Button size="small" onClick={() => openCompleteMaintenance(m.id)}>Mark Complete</Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {maintenance.length === 0 && (
                    <TableRow><TableCell colSpan={6} align="center">No maintenance records</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={maintenance.length}
              page={maintenancePage}
              onPageChange={(_, page) => setMaintenancePage(page)}
              rowsPerPage={maintenanceRowsPerPage}
              onRowsPerPageChange={(e) => {
                setMaintenanceRowsPerPage(parseInt(e.target.value, 10))
                setMaintenancePage(0)
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderCertificationsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Operator Certification</Typography>
            <Stack spacing={2}>
              <TextField label="Operator ID" value={certForm.operator_id} onChange={(e) => setCertForm((p) => ({ ...p, operator_id: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Equipment Type</InputLabel>
                <Select
                  label="Equipment Type"
                  value={certForm.equipment_type}
                  onChange={(e) => setCertForm((p) => ({ ...p, equipment_type: e.target.value }))}
                >
                  {equipmentTypes.map((t) => (
                    <MenuItem key={t} value={t}>{t}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField label="Certification #" value={certForm.certification_number} onChange={(e) => setCertForm((p) => ({ ...p, certification_number: e.target.value }))} />
              <TextField
                label="Issued Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={certForm.issued_date}
                onChange={(e) => setCertForm((p) => ({ ...p, issued_date: e.target.value }))}
              />
              <TextField
                label="Expiry Date"
                type="date"
                InputLabelProps={{ shrink: true }}
                value={certForm.expiry_date}
                onChange={(e) => setCertForm((p) => ({ ...p, expiry_date: e.target.value }))}
              />
              <TextField label="Issuing Authority" value={certForm.issuing_authority} onChange={(e) => setCertForm((p) => ({ ...p, issuing_authority: e.target.value }))} />
              <Button variant="contained" onClick={handleCreateCertification} disabled={createCertificationMutation.isPending}>Save Certification</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Certifications</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Operator</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Cert #</TableCell>
                    <TableCell>Expiry</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {certifications
                    .slice(certsPage * certsRowsPerPage, certsPage * certsRowsPerPage + certsRowsPerPage)
                    .map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.operator_id}</TableCell>
                      <TableCell>{c.equipment_type}</TableCell>
                      <TableCell>{c.certification_number}</TableCell>
                      <TableCell>{new Date(c.expiry_date).toLocaleDateString()}</TableCell>
                      <TableCell>
                        <Chip label={c.is_active ? 'Active' : 'Expired'} color={c.is_active ? 'success' : 'error'} size="small" />
                      </TableCell>
                    </TableRow>
                  ))}
                  {certifications.length === 0 && (
                    <TableRow><TableCell colSpan={5} align="center">No certifications</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={certifications.length}
              page={certsPage}
              onPageChange={(_, page) => setCertsPage(page)}
              rowsPerPage={certsRowsPerPage}
              onRowsPerPageChange={(e) => {
                setCertsRowsPerPage(parseInt(e.target.value, 10))
                setCertsPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25, 50]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight={600}>Heavy Equipment Management</Typography>
          <Typography variant="body1" color="text.secondary">
            Equipment allocation, booking approvals, maintenance, and operator compliance
          </Typography>
        </Box>
        <Button
          variant="outlined"
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['equipmentDashboard'] })
            queryClient.invalidateQueries({ queryKey: ['equipmentList'] })
            queryClient.invalidateQueries({ queryKey: ['equipmentBookings'] })
            queryClient.invalidateQueries({ queryKey: ['equipmentMaintenance'] })
            queryClient.invalidateQueries({ queryKey: ['equipmentCertifications'] })
          }}
        >
          Refresh
        </Button>
      </Box>

      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Dashboard" />
        <Tab label="Equipment" />
        <Tab label="Bookings" />
        <Tab label="Maintenance" />
        <Tab label="Certifications" />
      </Tabs>

      {activeTab === 0 && renderDashboard()}
      {activeTab === 1 && renderEquipmentTab()}
      {activeTab === 2 && renderBookingsTab()}
      {activeTab === 3 && renderMaintenanceTab()}
      {activeTab === 4 && renderCertificationsTab()}

      <Dialog open={maintenanceCompleteOpen} onClose={() => setMaintenanceCompleteOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Complete Maintenance</DialogTitle>
        <DialogContent sx={{ pt: 1 }}>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Completed Date"
              type="date"
              InputLabelProps={{ shrink: true }}
              value={maintenanceCompleteForm.completed_date}
              onChange={(e) => setMaintenanceCompleteForm((p) => ({ ...p, completed_date: e.target.value }))}
            />
            <TextField
              label="Performed By"
              value={maintenanceCompleteForm.performed_by}
              onChange={(e) => setMaintenanceCompleteForm((p) => ({ ...p, performed_by: e.target.value }))}
            />
            <TextField
              label="Cost"
              type="number"
              value={maintenanceCompleteForm.cost ?? ''}
              onChange={(e) => setMaintenanceCompleteForm((p) => ({ ...p, cost: e.target.value ? Number(e.target.value) : undefined }))}
            />
            <TextField
              label="Notes"
              multiline
              minRows={2}
              value={maintenanceCompleteForm.notes}
              onChange={(e) => setMaintenanceCompleteForm((p) => ({ ...p, notes: e.target.value }))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMaintenanceCompleteOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCompleteMaintenance}
            disabled={updateMaintenanceMutation.isPending || !maintenanceCompleteForm.completed_date}
          >
            {updateMaintenanceMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
