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
  TablePagination,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import visitorService from '../../services/visitorService'
import { useSelector } from 'react-redux'

export default function Visitor() {
  const [requestsPage, setRequestsPage] = useState(0)
  const [requestsRowsPerPage, setRequestsRowsPerPage] = useState(10)
  const [activePage, setActivePage] = useState(0)
  const [activeRowsPerPage, setActiveRowsPerPage] = useState(10)
  const [activeTab, setActiveTab] = useState(0)
  const [openDialog, setOpenDialog] = useState(false)
  const [form, setForm] = useState({
    visitor_name: '',
    visitor_phone: '',
    visitor_email: '',
    visitor_company: '',
    purpose: '',
    sponsor_id: '',
    visit_date: '',
    visit_time: '',
    expected_duration: 1,
    num_visitors: 1,
  })

  const queryClient = useQueryClient()
  const user = useSelector((state) => state.auth.user)

  const { data: stats, error: statsError } = useQuery({
    queryKey: ['visitorStats'],
    queryFn: visitorService.getDashboardStats,
    enabled: !!user,
    retry: 1,
  })

  const { data: requests = [], error: requestsError } = useQuery({
    queryKey: ['visitorRequests'],
    queryFn: () => visitorService.getRequests(),
    enabled: !!user,
    retry: 1,
  })

  const { data: activeVisitors = [], error: activeError } = useQuery({
    queryKey: ['activeVisitors'],
    queryFn: visitorService.getActiveVisitors,
    enabled: !!user,
    retry: 1,
  })

  const createMutation = useMutation({
    mutationFn: visitorService.createRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitorRequests'] })
      queryClient.invalidateQueries({ queryKey: ['visitorStats'] })
      setOpenDialog(false)
      resetForm()
    },
  })

  const resetForm = () => {
    setForm({
      visitor_name: '',
      visitor_phone: '',
      visitor_email: '',
      visitor_company: '',
      purpose: '',
      sponsor_id: user?.id || '',
      visit_date: '',
      visit_time: '',
      expected_duration: 1,
      num_visitors: 1,
    })
  }

  const handleSubmit = () => {
    createMutation.mutate({
      ...form,
      sponsor_id: user?.id || '',
    })
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      approved: 'success',
      rejected: 'error',
      completed: 'info',
    }
    return colors[status] || 'default'
  }

  return (
    <Box>
      {(statsError || requestsError || activeError) && (
        <Box sx={{ mb: 2, p: 2, bgcolor: 'error.light', color: 'error.contrastText', borderRadius: 1 }}>
          Error loading data. Please check if the Visitor service is running on port 8006.
        </Box>
      )}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom fontWeight={600}>
          Visitor Gate Pass Management
        </Typography>
        <Button variant="contained" onClick={() => setOpenDialog(true)}>
          New Visitor Request
        </Button>
      </Box>

      {stats && (
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h4">{stats.total_requests || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Pending Approval
                </Typography>
                <Typography variant="h4">{stats.pending_requests || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Visitors Today
                </Typography>
                <Typography variant="h4">{stats.visitors_today || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Currently On-Site
                </Typography>
                <Typography variant="h4">{stats.visitors_onsite || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Requests" />
        <Tab label="Active Visitors" />
      </Tabs>

      {activeTab === 0 && (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Request #</TableCell>
                  <TableCell>Visitor Name</TableCell>
                  <TableCell>Company</TableCell>
                  <TableCell>Purpose</TableCell>
                  <TableCell>Visit Date</TableCell>
                  <TableCell>Training</TableCell>
                  <TableCell>Medical</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No visitor requests found. Use New Request to create one.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  requests
                    .slice(requestsPage * requestsRowsPerPage, requestsPage * requestsRowsPerPage + requestsRowsPerPage)
                    .map((req) => (
                      <TableRow key={req.id}>
                        <TableCell>{req.request_number}</TableCell>
                        <TableCell>{req.visitor_name}</TableCell>
                        <TableCell>{req.visitor_company}</TableCell>
                        <TableCell>{req.purpose}</TableCell>
                        <TableCell>{new Date(req.visit_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={req.training_completed ? 'Done' : 'Pending'}
                            color={req.training_completed ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={req.medical_verified ? 'Verified' : 'Pending'}
                            color={req.medical_verified ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip label={req.status} color={getStatusColor(req.status)} size="small" />
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={requests.length}
            page={requestsPage}
            onPageChange={(_, page) => setRequestsPage(page)}
            rowsPerPage={requestsRowsPerPage}
            onRowsPerPageChange={(e) => {
              setRequestsRowsPerPage(parseInt(e.target.value, 10))
              setRequestsPage(0)
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </>
      )}

      {activeTab === 1 && (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Gate Pass #</TableCell>
                  <TableCell>Visitor Name</TableCell>
                  <TableCell>Company</TableCell>
                  <TableCell>Purpose</TableCell>
                  <TableCell>Visit Date</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {activeVisitors.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No active visitors found.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  activeVisitors
                    .slice(activePage * activeRowsPerPage, activePage * activeRowsPerPage + activeRowsPerPage)
                    .map((visitor) => (
                      <TableRow key={visitor.id}>
                        <TableCell>{visitor.gate_pass_number}</TableCell>
                        <TableCell>{visitor.visitor_name}</TableCell>
                        <TableCell>{visitor.visitor_company}</TableCell>
                        <TableCell>{visitor.purpose}</TableCell>
                        <TableCell>{new Date(visitor.visit_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip label={visitor.status} color={getStatusColor(visitor.status)} size="small" />
                        </TableCell>
                      </TableRow>
                    ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={activeVisitors.length}
            page={activePage}
            onPageChange={(_, page) => setActivePage(page)}
            rowsPerPage={activeRowsPerPage}
            onRowsPerPageChange={(e) => {
              setActiveRowsPerPage(parseInt(e.target.value, 10))
              setActivePage(0)
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </>
      )}

      {/* Create Request Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Visitor Request</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} mt={1}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Visitor Name"
                value={form.visitor_name}
                onChange={(e) => setForm({ ...form, visitor_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Visitor Phone"
                value={form.visitor_phone}
                onChange={(e) => setForm({ ...form, visitor_phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Visitor Email"
                value={form.visitor_email}
                onChange={(e) => setForm({ ...form, visitor_email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Visitor Company"
                value={form.visitor_company}
                onChange={(e) => setForm({ ...form, visitor_company: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Purpose"
                value={form.purpose}
                onChange={(e) => setForm({ ...form, purpose: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Visit Date"
                InputLabelProps={{ shrink: true }}
                value={form.visit_date}
                onChange={(e) => setForm({ ...form, visit_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="time"
                label="Visit Time"
                InputLabelProps={{ shrink: true }}
                value={form.visit_time}
                onChange={(e) => setForm({ ...form, visit_time: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Expected Duration (hours)"
                value={form.expected_duration}
                onChange={(e) => setForm({ ...form, expected_duration: Number(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Number of Visitors"
                value={form.num_visitors}
                onChange={(e) => setForm({ ...form, num_visitors: Number(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            Submit Request
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
