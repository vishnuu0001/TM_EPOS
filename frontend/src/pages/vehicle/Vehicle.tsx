import { useState } from 'react';
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
  Autocomplete,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  MenuItem,
  TablePagination,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import vehicleService, { type CreateRequisition, type Requisition } from '../../services/vehicleService';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

export default function Vehicle() {
  const departmentOptions = ['Operations', 'Maintenance', 'Logistics', 'Security', 'Administration', 'HR', 'Finance', 'IT', 'Procurement'];
  const purposeOptions = ['Site Visit', 'Material Transport', 'Staff Pickup', 'Client Meeting', 'Emergency', 'Inspection', 'Training', 'Other'];
  const [activeTab, setActiveTab] = useState(0);
  const [requisitionsPage, setRequisitionsPage] = useState(0);
  const [requisitionsRowsPerPage, setRequisitionsRowsPerPage] = useState(10);
  const [vehiclesPage, setVehiclesPage] = useState(0);
  const [vehiclesRowsPerPage, setVehiclesRowsPerPage] = useState(10);
  const [openDialog, setOpenDialog] = useState(false);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [selectedRequisition, setSelectedRequisition] = useState<Requisition | null>(null);
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [form, setForm] = useState<CreateRequisition>({
    department: '',
    purpose: '',
    destination: '',
    pickup_location: '',
    requested_date: '',
    requested_time: '',
    number_of_passengers: 1,
    vehicle_type: '',
    requester_id: '',
  });

  const queryClient = useQueryClient();
  const user = useSelector((state: RootState) => state.auth.user);

  const { data: stats, error: statsError } = useQuery({
    queryKey: ['vehicleStats'],
    queryFn: vehicleService.getDashboardStats,
    enabled: !!user,
    retry: 1,
  });

  const { data: vehicles = [], error: vehiclesError } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehicleService.getVehicles(),
    enabled: !!user,
    retry: 1,
  });

  const { data: requisitions = [], error: requisitionsError } = useQuery({
    queryKey: ['requisitions'],
    queryFn: () => vehicleService.getRequisitions(),
    enabled: !!user,
    retry: 1,
  });

  const createMutation = useMutation({
    mutationFn: vehicleService.createRequisition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['requisitions'] });
      queryClient.invalidateQueries({ queryKey: ['vehicleStats'] });
      setOpenDialog(false);
      resetForm();
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({ requisitionId, vehicleId }: { requisitionId: string; vehicleId: string }) =>
      vehicleService.approveRequisition(requisitionId, vehicleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['requisitions'] });
      queryClient.invalidateQueries({ queryKey: ['vehicleStats'] });
      setApproveDialogOpen(false);
      setSelectedRequisition(null);
      setSelectedVehicleId('');
    },
  });

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
    });
  };

  const handleSubmit = () => {
    const departureDateTime = form.requested_date
      ? `${form.requested_date}T${form.requested_time || '00:00'}`
      : '';

    createMutation.mutate({
      purpose: form.purpose,
      destination: form.destination,
      departure_date: departureDateTime,
      number_of_passengers: form.number_of_passengers,
      cost_center: form.department || undefined,
      notes: form.pickup_location || undefined,
      requester_id: user?.id || '',
      department: form.department,
      pickup_location: form.pickup_location,
      vehicle_type: form.vehicle_type || undefined,
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      assigned: 'info',
      completed: 'success',
      available: 'success',
      in_use: 'warning',
    };
    return colors[status] || 'default';
  };

  const availableVehicles = vehicles.filter((vehicle) => vehicle.status === 'AVAILABLE');

  const openApproveDialog = (requisition: Requisition) => {
    setSelectedRequisition(requisition);
    setSelectedVehicleId('');
    setApproveDialogOpen(true);
  };

  const handleApprove = () => {
    if (!selectedRequisition || !selectedVehicleId) return;
    approveMutation.mutate({ requisitionId: selectedRequisition.id, vehicleId: selectedVehicleId });
  };

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
                <Typography variant="h4">{stats.pending_requisitions ?? stats.pending_approvals ?? 0}</Typography>
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
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requisitions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No requisitions found. Use New Requisition to create one.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                requisitions
                  .slice(requisitionsPage * requisitionsRowsPerPage, requisitionsPage * requisitionsRowsPerPage + requisitionsRowsPerPage)
                  .map((req) => (
                  <TableRow key={req.id}>
                    <TableCell>{req.requisition_number}</TableCell>
                    <TableCell>{req.department}</TableCell>
                    <TableCell>{req.purpose}</TableCell>
                    <TableCell>{req.destination}</TableCell>
                    <TableCell>{req.departure_date ? new Date(req.departure_date).toLocaleDateString() : '-'}</TableCell>
                    <TableCell>{req.number_of_passengers}</TableCell>
                    <TableCell>
                      <Chip label={req.status} color={getStatusColor(req.status)} size="small" />
                    </TableCell>
                    <TableCell>
                      {req.status === 'REQUESTED' ? (
                        <Button size="small" variant="outlined" onClick={() => openApproveDialog(req)}>
                          Approve
                        </Button>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={requisitions.length}
          page={requisitionsPage}
          onPageChange={(_, page) => setRequisitionsPage(page)}
          rowsPerPage={requisitionsRowsPerPage}
          onRowsPerPageChange={(e) => {
            setRequisitionsRowsPerPage(parseInt(e.target.value, 10));
            setRequisitionsPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      )}
              ) : (
                vehicles
                  .slice(vehiclesPage * vehiclesRowsPerPage, vehiclesPage * vehiclesRowsPerPage + vehiclesRowsPerPage)
                  .map((vehicle) => (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Registration</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Model</TableCell>
                <TableCell>Capacity</TableCell>
                <TableCell>Fuel</TableCell>
                <TableCell>Current KM</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
        <TablePagination
          component="div"
          count={vehicles.length}
          page={vehiclesPage}
          onPageChange={(_, page) => setVehiclesPage(page)}
          rowsPerPage={vehiclesRowsPerPage}
          onRowsPerPageChange={(e) => {
            setVehiclesRowsPerPage(parseInt(e.target.value, 10));
            setVehiclesPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
              {vehicles.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No vehicles found in the system.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                vehicles.map((vehicle) => (
                  <TableRow key={vehicle.id}>
                    <TableCell>{vehicle.registration_number}</TableCell>
                    <TableCell>{vehicle.vehicle_type}</TableCell>
                    <TableCell>{vehicle.make_model}</TableCell>
                    <TableCell>{vehicle.capacity}</TableCell>
                    <TableCell>{vehicle.fuel_type}</TableCell>
                    <TableCell>{vehicle.current_km}</TableCell>
                    <TableCell>
                      <Chip label={vehicle.status} color={getStatusColor(vehicle.status)} size="small" />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Vehicle Requisition</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <Autocomplete
                freeSolo
                options={departmentOptions}
                value={form.department}
                inputValue={form.department}
                onChange={(_, newValue) => setForm({ ...form, department: newValue || '' })}
                onInputChange={(_, newInputValue) => setForm({ ...form, department: newInputValue })}
                renderInput={(params) => (
                  <TextField {...params} fullWidth label="Department" />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Vehicle Type"
                value={form.vehicle_type}
                onChange={(e) => setForm({ ...form, vehicle_type: e.target.value })}
              >
                <MenuItem value="car">Car</MenuItem>
                <MenuItem value="bus">Bus</MenuItem>
                <MenuItem value="truck">Truck</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <Autocomplete
                freeSolo
                options={purposeOptions}
                value={form.purpose}
                inputValue={form.purpose}
                onChange={(_, newValue) => setForm({ ...form, purpose: newValue || '' })}
                onInputChange={(_, newInputValue) => setForm({ ...form, purpose: newInputValue })}
                renderInput={(params) => (
                  <TextField {...params} fullWidth label="Purpose" />
                )}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Pickup Location"
                value={form.pickup_location}
                onChange={(e) => setForm({ ...form, pickup_location: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Destination"
                value={form.destination}
                onChange={(e) => setForm({ ...form, destination: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Requested Date"
                InputLabelProps={{ shrink: true }}
                value={form.requested_date}
                onChange={(e) => setForm({ ...form, requested_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="time"
                label="Requested Time"
                InputLabelProps={{ shrink: true }}
                value={form.requested_time}
                onChange={(e) => setForm({ ...form, requested_time: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Passengers"
                value={form.number_of_passengers}
                onChange={(e) => setForm({ ...form, number_of_passengers: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Submitting...' : 'Submit Requisition'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={approveDialogOpen} onClose={() => setApproveDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Approve Requisition</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            select
            label="Assign Vehicle"
            value={selectedVehicleId}
            onChange={(e) => setSelectedVehicleId(e.target.value)}
            sx={{ mt: 1 }}
            helperText={availableVehicles.length === 0 ? 'No available vehicles' : ''}
          >
            {availableVehicles.map((vehicle) => (
              <MenuItem key={vehicle.id} value={vehicle.id}>
                {vehicle.registration_number} • {vehicle.vehicle_type}
              </MenuItem>
            ))}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApproveDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleApprove}
            variant="contained"
            disabled={!selectedVehicleId || approveMutation.isPending}
          >
            {approveMutation.isPending ? 'Approving...' : 'Approve'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
