import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  MenuItem,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import vehicleService from '../../services/vehicleService'
import { useSelector } from 'react-redux'

export default function Vehicle() {
  const [activeTab, setActiveTab] = useState(0)
  const [openDialog, setOpenDialog] = useState(false)
  const [form, setForm] = useState({
    department: '',
    purpose: '',
    destination: '',
    pickup_location: '',
    requested_date: '',
    requested_time: '',
    number_of_passengers: 1,
    vehicle_type: '',
    requester_id: '',
  })

  const queryClient = useQueryClient()
  const user = useSelector((state) => state.auth.user)

  const { data: stats, error: statsError } = useQuery({
    queryKey: ['vehicleStats'],
    queryFn: vehicleService.getDashboardStats,
    enabled: !!user,
    retry: 1,
  })

  const { data: vehicles = [], error: vehiclesError } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehicleService.getVehicles(),
    enabled: !!user,
    retry: 1,
  })

  const { data: requisitions = [], error: requisitionsError } = useQuery({
    queryKey: ['requisitions'],
    queryFn: () => vehicleService.getRequisitions(),
    enabled: !!user,
    retry: 1,
  })

  const createMutation = useMutation({
    mutationFn: vehicleService.createRequisition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['requisitions'] })
      queryClient.invalidateQueries({ queryKey: ['vehicleStats'] })
      setOpenDialog(false)
      resetForm()
    },
  })

  const resetForm = () => {
    setForm({
      department: '',
      purpose: '',
      destination: '',
      pickup_location: '',
      requested_date: '',
      requested_time: '',
      number_of_passengers: 1,
      vehicle_type: '',
      requester_id: user?.id || '',
    })
  }

  const handleSubmit = () => {
    createMutation.mutate({
      ...form,
      requester_id: user?.id || '',
    })
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      assigned: 'info',
      completed: 'success',
      available: 'success',
      in_use: 'warning',
    }
    return colors[status] || 'default'
  }

  return (
    <Box>
      {(statsError || vehiclesError || requisitionsError) && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'error.light', color: 'error.contrastText', borderRadius: 1 }}>
          Error loading data. Please check if the Vehicle service is running on port 8005.
        </Box>
      )}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom fontWeight={600}>
          Vehicle Requisition System
        </Typography>
        <Button variant="contained" onClick={() => setOpenDialog(true)}>
          New Requisition
        </Button>
      </Box>

      {stats && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Vehicles
                </Typography>
                <Typography variant="h4">{stats.total_vehicles || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Available
                </Typography>
                <Typography variant="h4">{stats.available_vehicles || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Pending Requests
                </Typography>
                <Typography variant="h4">{stats.pending_requisitions || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Active Trips
                </Typography>
                <Typography variant="h4">{stats.active_trips || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Requisitions" />
        <Tab label="Vehicles" />
      </Tabs>

      {activeTab === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Req #</TableCell>
                <TableCell>Department</TableCell>
                <TableCell>Purpose</TableCell>
                <TableCell>Destination</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Passengers</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requisitions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No requisitions found. Use New Requisition to create one.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                requisitions.map((req) => (
                  <TableRow key={req.id}>
                    <TableCell>{req.requisition_number}</TableCell>
                    <TableCell>{req.department}</TableCell>
                    <TableCell>{req.purpose}</TableCell>
                    <TableCell>{req.destination}</TableCell>
                    <TableCell>{new Date(req.requested_date).toLocaleDateString()}</TableCell>
                    <TableCell>{req.number_of_passengers}</TableCell>
                    <TableCell>
                      <Chip label={req.status} color={getStatusColor(req.status)} size="small" />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Registration</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Make/Model</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Capacity</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {vehicles.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No vehicles found.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                vehicles.map((vehicle) => (
                  <TableRow key={vehicle.id}>
                    <TableCell>{vehicle.registration_number}</TableCell>
                    <TableCell>{vehicle.vehicle_type}</TableCell>
                    <TableCell>{vehicle.make_model}</TableCell>
                    <TableCell>
                      <Chip label={vehicle.status} color={getStatusColor(vehicle.status)} size="small" />
                    </TableCell>
                    <TableCell>{vehicle.capacity}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Requisition Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Vehicle Requisition</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                value={form.department}
                onChange={(e) => setForm({ ...form, department: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Purpose"
                value={form.purpose}
                onChange={(e) => setForm({ ...form, purpose: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Destination"
                value={form.destination}
                onChange={(e) => setForm({ ...form, destination: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Pickup Location"
                value={form.pickup_location}
                onChange={(e) => setForm({ ...form, pickup_location: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Requested Date"
                InputLabelProps={{ shrink: true }}
                value={form.requested_date}
                onChange={(e) => setForm({ ...form, requested_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="time"
                label="Requested Time"
                InputLabelProps={{ shrink: true }}
                value={form.requested_time}
                onChange={(e) => setForm({ ...form, requested_time: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Passengers"
                value={form.number_of_passengers}
                onChange={(e) => setForm({ ...form, number_of_passengers: Number(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Vehicle Type"
                value={form.vehicle_type}
                onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
              >
                <MenuItem value="">Any</MenuItem>
                <MenuItem value="Sedan">Sedan</MenuItem>
                <MenuItem value="SUV">SUV</MenuItem>
                <MenuItem value="Truck">Truck</MenuItem>
                <MenuItem value="Bus">Bus</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
