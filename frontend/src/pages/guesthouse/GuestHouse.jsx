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
  MenuItem,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  TablePagination,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import guesthouseService from '../../services/guesthouseService'
import { useSelector } from 'react-redux'

export default function GuestHouse() {
  const costCenterOptions = ['Operations', 'Maintenance', 'HR', 'Admin', 'Security', 'Canteen', 'Guest House']
  const [bookingsPage, setBookingsPage] = useState(0)
  const [bookingsRowsPerPage, setBookingsRowsPerPage] = useState(10)
  const [roomsPage, setRoomsPage] = useState(0)
  const [roomsRowsPerPage, setRoomsRowsPerPage] = useState(10)
  const [activeTab, setActiveTab] = useState(0)
  const [openBookingDialog, setOpenBookingDialog] = useState(false)
  const [bookingForm, setBookingForm] = useState({
    guest_name: '',
    guest_phone: '',
    guest_email: '',
    guest_company: '',
    room_id: '',
    check_in_date: '',
    check_out_date: '',
    cost_center: '',
    meal_plan: '',
    special_requests: '',
    booked_by_user_id: '',
  })

  const queryClient = useQueryClient()
  const user = useSelector((state) => state.auth.user)

  const { data: stats, error: statsError, isLoading: statsLoading } = useQuery({
    queryKey: ['guesthouseStats'],
    queryFn: guesthouseService.getDashboardStats,
    enabled: !!user,
    retry: 1,
  })

  const { data: rooms = [], error: roomsError, isLoading: roomsLoading } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => guesthouseService.getRooms(),
    enabled: !!user,
    retry: 1,
  })

  const { data: bookings = [], error: bookingsError, isLoading: bookingsLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: () => guesthouseService.getBookings(),
    enabled: !!user,
    retry: 1,
  })

  const createBookingMutation = useMutation({
    mutationFn: guesthouseService.createBooking,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bookings'] })
      queryClient.invalidateQueries({ queryKey: ['guesthouseStats'] })
      setOpenBookingDialog(false)
      resetForm()
    },
  })

  const resetForm = () => {
    setBookingForm({
      guest_name: '',
      guest_phone: '',
      guest_email: '',
      guest_company: '',
      room_id: '',
      check_in_date: '',
      check_out_date: '',
      cost_center: '',
      meal_plan: '',
      special_requests: '',
      booked_by_user_id: user?.id || '',
    })
  }

  const handleSubmitBooking = () => {
    createBookingMutation.mutate({
      ...bookingForm,
      booked_by_user_id: user?.id || '',
    })
  }

  const getStatusColor = (status) => {
    const colors = {
      available: 'success',
      occupied: 'error',
      confirmed: 'info',
      checked_in: 'warning',
      checked_out: 'success',
      cancelled: 'error',
    }
    return colors[status] || 'default'
  }

  const getRoomLabel = (roomId) => {
    const room = rooms.find((r) => r.id === roomId)
    return room ? `${room.room_number} - ${room.room_type}` : roomId
  }

  return (
    <Box>
      {(statsError || roomsError || bookingsError) && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'error.light', color: 'error.contrastText', borderRadius: 1 }}>
          Error loading data. Please check if the Guest House service is running on port 8002.
          {statsError && <div>Stats Error: {String(statsError)}</div>}
          {roomsError && <div>Rooms Error: {String(roomsError)}</div>}
          {bookingsError && <div>Bookings Error: {String(bookingsError)}</div>}
        </Box>
      )}
      {(statsLoading || roomsLoading || bookingsLoading) && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'info.light', color: 'info.contrastText', borderRadius: 1 }}>
          Loading data...
        </Box>
      )}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom fontWeight={600}>
          Guest House Management
        </Typography>
        <Button variant="contained" onClick={() => setOpenBookingDialog(true)}>
          New Booking
        </Button>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Rooms
                </Typography>
                <Typography variant="h4">{stats.total_rooms || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Occupied
                </Typography>
                <Typography variant="h4">{stats.occupied_rooms || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Occupancy Rate
                </Typography>
                <Typography variant="h4">{stats.occupancy_rate || 0}%</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Revenue (Month)
                </Typography>
                <Typography variant="h4">₹{(stats.revenue_month || 0).toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Bookings" />
        <Tab label="Rooms" />
      </Tabs>

      {/* Bookings Tab */}
      {activeTab === 0 && (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Booking #</TableCell>
                  <TableCell>Guest Name</TableCell>
                  <TableCell>Room</TableCell>
                  <TableCell>Check In</TableCell>
                  <TableCell>Check Out</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bookings.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No bookings found. Use New Booking to create one.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  bookings
                    .slice(bookingsPage * bookingsRowsPerPage, bookingsPage * bookingsRowsPerPage + bookingsRowsPerPage)
                    .map((booking) => (
                      <TableRow key={booking.id}>
                        <TableCell>{booking.booking_number}</TableCell>
                        <TableCell>{booking.guest_name}</TableCell>
                        <TableCell>{getRoomLabel(booking.room_id)}</TableCell>
                        <TableCell>{new Date(booking.check_in_date).toLocaleDateString()}</TableCell>
                        <TableCell>{new Date(booking.check_out_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip label={booking.status} color={getStatusColor(booking.status)} size="small" />
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={bookings.length}
            page={bookingsPage}
            onPageChange={(_, page) => setBookingsPage(page)}
            rowsPerPage={bookingsRowsPerPage}
            onRowsPerPageChange={(e) => {
              setBookingsRowsPerPage(parseInt(e.target.value, 10))
              setBookingsPage(0)
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </>
      )}

      {/* Rooms Tab */}
      {activeTab === 1 && (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Room #</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Capacity</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Rate</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rooms.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No rooms found.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  rooms
                    .slice(roomsPage * roomsRowsPerPage, roomsPage * roomsRowsPerPage + roomsRowsPerPage)
                    .map((room) => (
                      <TableRow key={room.id}>
                        <TableCell>{room.room_number}</TableCell>
                        <TableCell>{room.room_type}</TableCell>
                        <TableCell>{room.capacity}</TableCell>
                        <TableCell>
                          <Chip label={room.status} color={getStatusColor(room.status)} size="small" />
                        </TableCell>
                        <TableCell>₹{room.rate_per_night}</TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={rooms.length}
            page={roomsPage}
            onPageChange={(_, page) => setRoomsPage(page)}
            rowsPerPage={roomsRowsPerPage}
            onRowsPerPageChange={(e) => {
              setRoomsRowsPerPage(parseInt(e.target.value, 10))
              setRoomsPage(0)
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </>
      )}

      {/* New Booking Dialog */}
      <Dialog open={openBookingDialog} onClose={() => setOpenBookingDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Booking</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Guest Name"
                value={bookingForm.guest_name}
                onChange={(e) => setBookingForm({ ...bookingForm, guest_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Guest Phone"
                value={bookingForm.guest_phone}
                placeholder="+91 98765 43210"
                helperText="Format: +91 98765 43210"
                onChange={(e) => setBookingForm({ ...bookingForm, guest_phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Guest Email"
                value={bookingForm.guest_email}
                onChange={(e) => setBookingForm({ ...bookingForm, guest_email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Guest Company"
                value={bookingForm.guest_company}
                onChange={(e) => setBookingForm({ ...bookingForm, guest_company: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Room"
                id="guesthouse-room"
                value={bookingForm.room_id}
                onChange={(e) => setBookingForm({ ...bookingForm, room_id: e.target.value })}
              >
                {rooms.map((room) => (
                  <MenuItem key={room.id} value={room.id}>
                    {room.room_number} - {room.room_type}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Cost Center"
                id="guesthouse-cost-center"
                value={bookingForm.cost_center}
                onChange={(e) => setBookingForm({ ...bookingForm, cost_center: e.target.value })}
              >
                {costCenterOptions.map((center) => (
                  <MenuItem key={center} value={center}>
                    {center}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Check In"
                InputLabelProps={{ shrink: true }}
                value={bookingForm.check_in_date}
                onChange={(e) => setBookingForm({ ...bookingForm, check_in_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Check Out"
                InputLabelProps={{ shrink: true }}
                value={bookingForm.check_out_date}
                onChange={(e) => setBookingForm({ ...bookingForm, check_out_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                select
                label="Meal Plan"
                id="guesthouse-meal-plan"
                value={bookingForm.meal_plan}
                onChange={(e) => setBookingForm({ ...bookingForm, meal_plan: e.target.value })}
              >
                <MenuItem value="veg">Veg</MenuItem>
                <MenuItem value="non_veg">Non-Veg</MenuItem>
                <MenuItem value="eggetarian">Eggetarian</MenuItem>
                <MenuItem value="jain">Jain</MenuItem>
                <MenuItem value="vegan">Vegan</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Special Requests"
                value={bookingForm.special_requests}
                onChange={(e) => setBookingForm({ ...bookingForm, special_requests: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBookingDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmitBooking}>
            Create Booking
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
