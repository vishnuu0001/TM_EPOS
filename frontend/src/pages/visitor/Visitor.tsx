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
  MenuItem,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  TablePagination,
} from '@mui/material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import visitorService, { type CreateVisitorRequest, type VisitorRequest } from '../../services/visitorService';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';

export default function Visitor() {
  const [requestsPage, setRequestsPage] = useState(0);
  const [requestsRowsPerPage, setRequestsRowsPerPage] = useState(10);
  const [activePage, setActivePage] = useState(0);
  const [activeRowsPerPage, setActiveRowsPerPage] = useState(10);
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<VisitorRequest | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [form, setForm] = useState<CreateVisitorRequest>({
    visitor_name: '',
    visitor_phone: '',
    visitor_email: '',
    visitor_company: '',
    visitor_type: 'guest',
    sponsor_employee_id: '',
    sponsor_name: '',
    sponsor_department: '',
    purpose_of_visit: '',
    visit_date: '',
    visit_time: '',
    expected_duration: 1,
    areas_to_visit: '',
    safety_required: true,
    medical_required: true,
  });

  const queryClient = useQueryClient();
  const user = useSelector((state: RootState) => state.auth.user);

  const { data: stats, error: statsError } = useQuery({
    queryKey: ['visitorStats'],
    queryFn: visitorService.getDashboardStats,
    enabled: !!user,
    retry: 1,
  });

  const { data: requests = [], error: requestsError } = useQuery({
    queryKey: ['visitorRequests'],
    queryFn: () => visitorService.getRequests(),
    enabled: !!user,
    retry: 1,
  });

  const { data: activeVisitors = [], error: activeError } = useQuery({
    queryKey: ['activeVisitors'],
    queryFn: visitorService.getActiveVisitors,
    enabled: !!user,
    retry: 1,
  });

  const createMutation = useMutation({
    mutationFn: visitorService.createRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitorRequests'] });
      queryClient.invalidateQueries({ queryKey: ['visitorStats'] });
      setOpenDialog(false);
      resetForm();
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: string) => visitorService.approveRequest(id, 'final'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitorRequests'] });
      queryClient.invalidateQueries({ queryKey: ['visitorStats'] });
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => visitorService.rejectRequest(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visitorRequests'] });
      queryClient.invalidateQueries({ queryKey: ['visitorStats'] });
      setRejectDialogOpen(false);
      setSelectedRequest(null);
      setRejectReason('');
    },
  });

  const resetForm = () => {
    setForm({
      visitor_name: '',
      visitor_phone: '',
      visitor_email: '',
      visitor_company: '',
      visitor_type: 'guest',
      sponsor_employee_id: user?.employee_id || user?.id || '',
      sponsor_name: user?.full_name || '',
      sponsor_department: user?.department || '',
      purpose_of_visit: '',
      visit_date: '',
      visit_time: '',
      expected_duration: 1,
      areas_to_visit: '',
      safety_required: true,
      medical_required: true,
    });
  };

  const handleSubmit = () => {
    const visitDateTime = form.visit_date
      ? `${form.visit_date}T${form.visit_time || '00:00'}`
      : '';
    createMutation.mutate({
      visitor_name: form.visitor_name,
      visitor_phone: form.visitor_phone,
      visitor_email: form.visitor_email || undefined,
      visitor_company: form.visitor_company || undefined,
      visitor_type: form.visitor_type,
      sponsor_employee_id: form.sponsor_employee_id || user?.employee_id || user?.id || '',
      sponsor_name: form.sponsor_name || user?.full_name || '',
      sponsor_department: form.sponsor_department || user?.department || undefined,
      purpose_of_visit: form.purpose_of_visit,
      visit_date: visitDateTime,
      expected_duration: form.expected_duration || undefined,
      areas_to_visit: form.areas_to_visit || undefined,
      safety_required: form.safety_required,
      medical_required: form.medical_required,
    });
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
      submitted: 'warning',
      training_pending: 'warning',
      training_completed: 'info',
      medical_pending: 'warning',
      medical_uploaded: 'info',
      pending_approval: 'warning',
      approved: 'success',
      rejected: 'error',
      gate_pass_issued: 'info',
      expired: 'default',
    };
    return colors[status] || 'default';
  };

  const isTrainingDone = (status: string) => [
    'training_completed',
    'medical_pending',
    'medical_uploaded',
    'pending_approval',
    'approved',
    'gate_pass_issued',
    'expired',
  ].includes(status);

  const isMedicalVerified = (status: string) => [
    'pending_approval',
    'approved',
    'gate_pass_issued',
    'expired',
  ].includes(status);

  const canDecide = (status: string) => [
    'submitted',
    'training_pending',
    'training_completed',
    'medical_pending',
    'medical_uploaded',
    'pending_approval',
  ].includes(status);

  const openRejectDialog = (request: VisitorRequest) => {
    setSelectedRequest(request);
    setRejectReason('');
    setRejectDialogOpen(true);
  };

  const handleReject = () => {
    if (!selectedRequest || !rejectReason.trim()) return;
    rejectMutation.mutate({ id: selectedRequest.id, reason: rejectReason.trim() });
  };

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
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
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
                    <TableCell>{req.purpose_of_visit}</TableCell>
                    <TableCell>{new Date(req.visit_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={isTrainingDone(req.status) ? 'Done' : 'Pending'}
                        color={isTrainingDone(req.status) ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={isMedicalVerified(req.status) ? 'Verified' : 'Pending'}
                        color={isMedicalVerified(req.status) ? 'success' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={req.status} color={getStatusColor(req.status)} size="small" />
                    </TableCell>
                    <TableCell>
                      {canDecide(req.status) ? (
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => approveMutation.mutate(req.id)}
                            disabled={approveMutation.isPending}
                          >
                            Approve
                          </Button>
                          <Button
                            size="small"
                            color="error"
                            variant="outlined"
                            onClick={() => openRejectDialog(req)}
                          >
                            Deny
                          </Button>
                        </Box>
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
          count={requests.length}
          page={requestsPage}
          onPageChange={(_, page) => setRequestsPage(page)}
          rowsPerPage={requestsRowsPerPage}
          onRowsPerPageChange={(e) => {
            setRequestsRowsPerPage(parseInt(e.target.value, 10));
            setRequestsPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      )}

      {activeTab === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Request #</TableCell>
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
                    <Typography color="text.secondary">No active visitors today.</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                activeVisitors
                  .slice(activePage * activeRowsPerPage, activePage * activeRowsPerPage + activeRowsPerPage)
                  .map((visitor) => (
                  <TableRow key={visitor.id}>
                    <TableCell>{visitor.request_number}</TableCell>
                    <TableCell>{visitor.visitor_name}</TableCell>
                    <TableCell>{visitor.visitor_company}</TableCell>
                    <TableCell>{visitor.purpose_of_visit}</TableCell>
                    <TableCell>{new Date(visitor.visit_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip label={visitor.status} color={getStatusColor(visitor.status)} size="small" />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
        <TablePagination
          component="div"
          count={activeVisitors.length}
          page={activePage}
          onPageChange={(_, page) => setActivePage(page)}
          rowsPerPage={activeRowsPerPage}
          onRowsPerPageChange={(e) => {
            setActiveRowsPerPage(parseInt(e.target.value, 10));
            setActivePage(0);
          }}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
          </Table>
        </TableContainer>
      )}

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Visitor Request</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Visitor Name"
                value={form.visitor_name}
                onChange={(e) => setForm({ ...form, visitor_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={form.visitor_phone}
                onChange={(e) => setForm({ ...form, visitor_phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Visitor Type"
                value={form.visitor_type}
                onChange={(e) => setForm({ ...form, visitor_type: e.target.value })}
              >
                <MenuItem value="contractor">Contractor</MenuItem>
                <MenuItem value="vendor">Vendor</MenuItem>
                <MenuItem value="consultant">Consultant</MenuItem>
                <MenuItem value="guest">Guest</MenuItem>
                <MenuItem value="official">Official</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={form.visitor_email}
                onChange={(e) => setForm({ ...form, visitor_email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Company"
                value={form.visitor_company}
                onChange={(e) => setForm({ ...form, visitor_company: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Purpose of Visit"
                value={form.purpose_of_visit}
                onChange={(e) => setForm({ ...form, purpose_of_visit: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Sponsor Name"
                value={form.sponsor_name}
                onChange={(e) => setForm({ ...form, sponsor_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Sponsor Employee ID"
                value={form.sponsor_employee_id}
                onChange={(e) => setForm({ ...form, sponsor_employee_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Sponsor Department"
                value={form.sponsor_department}
                onChange={(e) => setForm({ ...form, sponsor_department: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Areas to Visit"
                value={form.areas_to_visit}
                onChange={(e) => setForm({ ...form, areas_to_visit: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Visit Date"
                InputLabelProps={{ shrink: true }}
                value={form.visit_date}
                onChange={(e) => setForm({ ...form, visit_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="time"
                label="Visit Time"
                InputLabelProps={{ shrink: true }}
                value={form.visit_time}
                onChange={(e) => setForm({ ...form, visit_time: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Expected Duration (hours)"
                value={form.expected_duration}
                onChange={(e) => setForm({ ...form, expected_duration: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Safety Required"
                value={form.safety_required ? 'yes' : 'no'}
                onChange={(e) => setForm({ ...form, safety_required: e.target.value === 'yes' })}
              >
                <MenuItem value="yes">Yes</MenuItem>
                <MenuItem value="no">No</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Medical Required"
                value={form.medical_required ? 'yes' : 'no'}
                onChange={(e) => setForm({ ...form, medical_required: e.target.value === 'yes' })}
              >
                <MenuItem value="yes">Yes</MenuItem>
                <MenuItem value="no">No</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Submitting...' : 'Submit Request'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Deny Visitor Request</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Rejection Reason"
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            multiline
            rows={3}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleReject}
            variant="contained"
            color="error"
            disabled={!rejectReason.trim() || rejectMutation.isPending}
          >
            {rejectMutation.isPending ? 'Denying...' : 'Deny'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
