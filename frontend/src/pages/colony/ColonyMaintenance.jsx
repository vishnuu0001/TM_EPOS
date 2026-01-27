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
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Drawer,
  FormControlLabel,
  Switch,
  TablePagination,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import { useSelector } from 'react-redux'
import { colonyService } from '../../services/colonyService'

const statusLabels = {
  submitted: 'Submitted',
  assigned: 'Assigned',
  in_progress: 'In Progress',
  materials_required: 'Materials Required',
  completed: 'Completed',
  closed: 'Closed',
  cancelled: 'Cancelled',
}

const statusColors = {
  submitted: 'default',
  assigned: 'info',
  in_progress: 'warning',
  materials_required: 'warning',
  completed: 'success',
  closed: 'success',
  cancelled: 'error',
}

const priorities = ['low', 'medium', 'high', 'urgent']
const frequencies = ['monthly', 'quarterly', 'annual']
const subCategoryOptions = {
  Plumbing: ['Leakage', 'Clogging', 'Fixture Repair', 'Water Pressure', 'Other'],
  Electrical: ['Power Outage', 'Wiring', 'Lighting', 'Appliance', 'Other'],
  Carpentry: ['Door/Window', 'Furniture', 'Cabinet', 'Repair', 'Other'],
  Painting: ['Interior', 'Exterior', 'Touch-up', 'Waterproofing', 'Other'],
}

const isoDate = (date) => date.toISOString().slice(0, 10)

export default function ColonyMaintenance() {
  const queryClient = useQueryClient()
  const user = useSelector((state) => state.auth.user)

  const [requestsPage, setRequestsPage] = useState(0)
  const [requestsRowsPerPage, setRequestsRowsPerPage] = useState(10)
  const [vendorsPage, setVendorsPage] = useState(0)
  const [vendorsRowsPerPage, setVendorsRowsPerPage] = useState(10)
  const [techniciansPage, setTechniciansPage] = useState(0)
  const [techniciansRowsPerPage, setTechniciansRowsPerPage] = useState(10)
  const [assetsPage, setAssetsPage] = useState(0)
  const [assetsRowsPerPage, setAssetsRowsPerPage] = useState(10)
  const [categoriesPage, setCategoriesPage] = useState(0)
  const [categoriesRowsPerPage, setCategoriesRowsPerPage] = useState(10)
  const [recurringPage, setRecurringPage] = useState(0)
  const [recurringRowsPerPage, setRecurringRowsPerPage] = useState(10)

  const [activeTab, setActiveTab] = useState(0)
  const [createOpen, setCreateOpen] = useState(false)
  const [selectedRequestId, setSelectedRequestId] = useState(null)
  const [requestFilter, setRequestFilter] = useState({})

  const [requestForm, setRequestForm] = useState({
    quarter_number: '',
    category: '',
    sub_category: '',
    description: '',
    priority: 'medium',
  })

  const [assignForm, setAssignForm] = useState({
    assigned_vendor_id: '',
    assigned_technician_id: '',
    estimated_cost: undefined,
    requires_approval: false,
  })

  const [statusForm, setStatusForm] = useState({
    status: 'submitted',
    notes: '',
    actual_cost: undefined,
  })

  const [attachmentFile, setAttachmentFile] = useState(null)

  const [vendorForm, setVendorForm] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    service_categories: '',
  })

  const [technicianForm, setTechnicianForm] = useState({
    name: '',
    phone: '',
    email: '',
    specialization: '',
    vendor_id: '',
  })

  const [assetForm, setAssetForm] = useState({
    asset_number: '',
    asset_type: '',
    quarter_number: '',
    make: '',
    model: '',
    serial_number: '',
    installation_date: '',
    status: 'active',
  })

  const [categoryForm, setCategoryForm] = useState({
    name: '',
    description: '',
    sla_hours: 24,
    icon: '',
    is_active: true,
  })

  const [recurringForm, setRecurringForm] = useState({
    name: '',
    description: '',
    category: '',
    frequency: 'monthly',
    next_schedule_date: isoDate(new Date()),
    assigned_vendor_id: '',
    is_active: true,
  })

  const { data: stats } = useQuery({
    queryKey: ['colonyDashboard'],
    queryFn: colonyService.getDashboardStats,
    enabled: !!user,
  })

  const { data: categories = [] } = useQuery({
    queryKey: ['colonyCategories'],
    queryFn: () => colonyService.getCategories(),
    enabled: !!user,
  })

  const { data: vendors = [] } = useQuery({
    queryKey: ['colonyVendors'],
    queryFn: () => colonyService.getVendors(),
    enabled: !!user,
  })

  const { data: technicians = [] } = useQuery({
    queryKey: ['colonyTechnicians'],
    queryFn: () => colonyService.getTechnicians(),
    enabled: !!user,
  })

  const { data: assets = [] } = useQuery({
    queryKey: ['colonyAssets'],
    queryFn: () => colonyService.getAssets(),
    enabled: !!user,
  })

  const { data: recurring = [] } = useQuery({
    queryKey: ['colonyRecurring'],
    queryFn: () => colonyService.getRecurring(),
    enabled: !!user,
  })

  const { data: requests = [] } = useQuery({
    queryKey: ['colonyRequests', requestFilter],
    queryFn: () => colonyService.getRequests(requestFilter),
    enabled: !!user,
  })

  const { data: selectedRequest } = useQuery({
    queryKey: ['colonyRequest', selectedRequestId],
    queryFn: () => colonyService.getRequest(selectedRequestId || ''),
    enabled: !!selectedRequestId,
  })

  const createRequestMutation = useMutation({
    mutationFn: colonyService.createRequest,
    onSuccess: () => {
      toast.success('Maintenance request created')
      queryClient.invalidateQueries({ queryKey: ['colonyRequests'] })
      queryClient.invalidateQueries({ queryKey: ['colonyDashboard'] })
      setCreateOpen(false)
      setRequestForm({
        quarter_number: '',
        category: '',
        sub_category: '',
        description: '',
        priority: 'medium',
      })
    },
  })

  const assignMutation = useMutation({
    mutationFn: ({ id, payload }) => colonyService.assignRequest(id, payload),
    onSuccess: () => {
      toast.success('Request assigned')
      queryClient.invalidateQueries({ queryKey: ['colonyRequests'] })
      queryClient.invalidateQueries({ queryKey: ['colonyRequest', selectedRequestId] })
      queryClient.invalidateQueries({ queryKey: ['colonyDashboard'] })
    },
  })

  const statusMutation = useMutation({
    mutationFn: ({ id, payload }) => colonyService.changeStatus(id, payload),
    onSuccess: () => {
      toast.success('Status updated')
      queryClient.invalidateQueries({ queryKey: ['colonyRequests'] })
      queryClient.invalidateQueries({ queryKey: ['colonyRequest', selectedRequestId] })
      queryClient.invalidateQueries({ queryKey: ['colonyDashboard'] })
    },
  })

  const uploadMutation = useMutation({
    mutationFn: ({ id, file }) => colonyService.uploadAttachment(id, file),
    onSuccess: () => {
      toast.success('Attachment uploaded')
    },
  })

  const vendorMutation = useMutation({
    mutationFn: colonyService.createVendor,
    onSuccess: () => {
      toast.success('Vendor saved')
      queryClient.invalidateQueries({ queryKey: ['colonyVendors'] })
      setVendorForm({ name: '', company_name: '', email: '', phone: '', service_categories: '' })
    },
  })

  const technicianMutation = useMutation({
    mutationFn: colonyService.createTechnician,
    onSuccess: () => {
      toast.success('Technician saved')
      queryClient.invalidateQueries({ queryKey: ['colonyTechnicians'] })
      setTechnicianForm({ name: '', phone: '', email: '', specialization: '', vendor_id: '' })
    },
  })

  const assetMutation = useMutation({
    mutationFn: colonyService.createAsset,
    onSuccess: () => {
      toast.success('Asset saved')
      queryClient.invalidateQueries({ queryKey: ['colonyAssets'] })
      setAssetForm({
        asset_number: '',
        asset_type: '',
        quarter_number: '',
        make: '',
        model: '',
        serial_number: '',
        installation_date: '',
        status: 'active',
      })
    },
  })

  const categoryMutation = useMutation({
    mutationFn: colonyService.createCategory,
    onSuccess: () => {
      toast.success('Category saved')
      queryClient.invalidateQueries({ queryKey: ['colonyCategories'] })
      setCategoryForm({ name: '', description: '', sla_hours: 24, icon: '', is_active: true })
    },
  })

  const recurringMutation = useMutation({
    mutationFn: colonyService.createRecurring,
    onSuccess: () => {
      toast.success('Recurring task saved')
      queryClient.invalidateQueries({ queryKey: ['colonyRecurring'] })
      setRecurringForm({
        name: '',
        description: '',
        category: '',
        frequency: 'monthly',
        next_schedule_date: isoDate(new Date()),
        assigned_vendor_id: '',
        is_active: true,
      })
    },
  })

  const handleCreateRequest = () => {
    if (!requestForm.quarter_number || !requestForm.category || !requestForm.description) {
      toast.error('Quarter, category, and description are required')
      return
    }
    createRequestMutation.mutate(requestForm)
  }

  const handleAssign = () => {
    if (!selectedRequestId) return
    assignMutation.mutate({ id: selectedRequestId, payload: assignForm })
  }

  const handleStatusChange = () => {
    if (!selectedRequestId) return
    statusMutation.mutate({ id: selectedRequestId, payload: statusForm })
  }

  const handleUpload = () => {
    if (!selectedRequestId || !attachmentFile) return
    uploadMutation.mutate({ id: selectedRequestId, file: attachmentFile })
    setAttachmentFile(null)
  }

  const cards = [
    { label: 'Total Requests', value: stats?.total_requests ?? 0 },
    { label: 'Pending', value: stats?.pending_requests ?? 0 },
    { label: 'In Progress', value: stats?.in_progress_requests ?? 0 },
    { label: 'Completed', value: stats?.completed_requests ?? 0 },
    { label: 'Overdue', value: stats?.overdue_requests ?? 0 },
    { label: 'Open Assignments', value: stats?.open_assignments ?? 0 },
    { label: 'Active Recurring', value: stats?.active_recurring ?? 0 },
    { label: 'Avg Rating', value: (stats?.avg_rating ?? 0).toFixed(1) },
  ]

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight={600}>Colony Maintenance</Typography>
        <Box display="flex" gap={1}>
          <Button variant="outlined" onClick={() => queryClient.invalidateQueries({ queryKey: ['colonyRequests'] })}>
            Refresh
          </Button>
          <Button variant="contained" onClick={() => setCreateOpen(true)}>
            New Request
          </Button>
        </Box>
      </Box>

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

      <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Requests" />
        <Tab label="Vendors & Technicians" />
        <Tab label="Assets" />
        <Tab label="Categories" />
        <Tab label="Recurring" />
      </Tabs>

      {activeTab === 0 && (
        <Box>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} mb={2} alignItems={{ md: 'center' }}>
            <FormControl sx={{ minWidth: 180 }} size="small">
              <InputLabel>Status</InputLabel>
              <Select
                label="Status"
                value={requestFilter.status || ''}
                onChange={(e) => setRequestFilter((prev) => ({ ...prev, status: e.target.value || undefined }))}
              >
                <MenuItem value="">All</MenuItem>
                {Object.keys(statusLabels).map((key) => (
                  <MenuItem key={key} value={key}>
                    {statusLabels[key]}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 180 }} size="small">
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={requestFilter.category || ''}
                onChange={(e) => setRequestFilter((prev) => ({ ...prev, category: e.target.value || undefined }))}
              >
                <MenuItem value="">All</MenuItem>
                {categories.map((c) => (
                  <MenuItem key={c.id} value={c.name}>{c.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Request #</TableCell>
                  <TableCell>Quarter</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {requests.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No maintenance requests yet.</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  requests
                    .slice(requestsPage * requestsRowsPerPage, requestsPage * requestsRowsPerPage + requestsRowsPerPage)
                    .map((req) => (
                    <TableRow
                      key={req.id}
                      hover
                      onClick={() => setSelectedRequestId(req.id)}
                      sx={{ cursor: 'pointer' }}
                    >
                      <TableCell>{req.request_number}</TableCell>
                      <TableCell>{req.quarter_number}</TableCell>
                      <TableCell>{req.category}</TableCell>
                      <TableCell>{req.priority}</TableCell>
                      <TableCell>
                        <Chip
                          label={statusLabels[req.status]}
                          color={statusColors[req.status]}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{new Date(req.created_at).toLocaleString()}</TableCell>
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

          <Drawer
            anchor="right"
            open={!!selectedRequestId}
            onClose={() => setSelectedRequestId(null)}
            PaperProps={{ sx: { width: { xs: '100%', md: 480 }, p: 3 } }}
          >
            {selectedRequest ? (
              <Box>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6">Request {selectedRequest.request_number}</Typography>
                  <Chip label={statusLabels[selectedRequest.status]} color={statusColors[selectedRequest.status]} />
                </Stack>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {selectedRequest.description}
                </Typography>
                <Stack direction="row" spacing={2} mb={3}>
                  <Chip label={`Quarter ${selectedRequest.quarter_number}`} />
                  <Chip label={`Priority: ${selectedRequest.priority}`} />
                  <Chip label={`Category: ${selectedRequest.category}`} />
                </Stack>

                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" gutterBottom>Assign</Typography>
                <Stack spacing={2} mb={2}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Vendor</InputLabel>
                    <Select
                      label="Vendor"
                      value={assignForm.assigned_vendor_id || ''}
                      onChange={(e) => setAssignForm((prev) => ({ ...prev, assigned_vendor_id: e.target.value }))}
                    >
                      <MenuItem value="">None</MenuItem>
                      {vendors.map((v) => (
                        <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth size="small">
                    <InputLabel>Technician</InputLabel>
                    <Select
                      label="Technician"
                      value={assignForm.assigned_technician_id || ''}
                      onChange={(e) => setAssignForm((prev) => ({ ...prev, assigned_technician_id: e.target.value }))}
                    >
                      <MenuItem value="">None</MenuItem>
                      {technicians.map((t) => (
                        <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    label="Estimated Cost"
                    type="number"
                    size="small"
                    value={assignForm.estimated_cost ?? ''}
                    onChange={(e) => setAssignForm((prev) => ({ ...prev, estimated_cost: e.target.value ? Number(e.target.value) : undefined }))}
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={assignForm.requires_approval || false}
                        onChange={(e) => setAssignForm((prev) => ({ ...prev, requires_approval: e.target.checked }))}
                      />
                    }
                    label="Requires Approval"
                  />
                  <Button variant="contained" onClick={handleAssign} disabled={assignMutation.isPending}>
                    Assign
                  </Button>
                </Stack>

                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" gutterBottom>Status</Typography>
                <Stack spacing={2} mb={2}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      label="Status"
                      value={statusForm.status}
                      onChange={(e) => setStatusForm((prev) => ({ ...prev, status: e.target.value }))}
                    >
                      {Object.keys(statusLabels).map((key) => (
                        <MenuItem key={key} value={key}>{statusLabels[key]}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    label="Notes"
                    multiline
                    minRows={2}
                    value={statusForm.notes || ''}
                    onChange={(e) => setStatusForm((prev) => ({ ...prev, notes: e.target.value }))}
                  />
                  <TextField
                    label="Actual Cost"
                    type="number"
                    size="small"
                    value={statusForm.actual_cost ?? ''}
                    onChange={(e) => setStatusForm((prev) => ({ ...prev, actual_cost: e.target.value ? Number(e.target.value) : undefined }))}
                  />
                  <Button variant="contained" onClick={handleStatusChange} disabled={statusMutation.isPending}>
                    Update Status
                  </Button>
                </Stack>

                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" gutterBottom>Attachments</Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Button variant="outlined" component="label">
                    Choose File
                    <input type="file" hidden onChange={(e) => setAttachmentFile(e.target.files?.[0] || null)} />
                  </Button>
                  <Typography variant="body2" color="text.secondary">
                    {attachmentFile ? attachmentFile.name : 'No file selected'}
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={handleUpload}
                    disabled={!attachmentFile || uploadMutation.isPending}
                  >
                    Upload
                  </Button>
                </Stack>
              </Box>
            ) : (
              <Typography>Loading...</Typography>
            )}
          </Drawer>
        </Box>
      )}

      {activeTab === 1 && (
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Vendors</Typography>
                <Stack spacing={2} mb={2}>
                  <TextField label="Name" value={vendorForm.name} onChange={(e) => setVendorForm((p) => ({ ...p, name: e.target.value }))} />
                  <TextField label="Company" value={vendorForm.company_name} onChange={(e) => setVendorForm((p) => ({ ...p, company_name: e.target.value }))} />
                  <TextField label="Email" value={vendorForm.email} onChange={(e) => setVendorForm((p) => ({ ...p, email: e.target.value }))} />
                  <TextField label="Phone" value={vendorForm.phone} onChange={(e) => setVendorForm((p) => ({ ...p, phone: e.target.value }))} />
                  <TextField label="Service Categories" placeholder="Comma separated" value={vendorForm.service_categories} onChange={(e) => setVendorForm((p) => ({ ...p, service_categories: e.target.value }))} />
                  <Button variant="contained" onClick={() => vendorMutation.mutate(vendorForm)}>Save Vendor</Button>
                </Stack>
                <Divider sx={{ my: 2 }} />
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell>Categories</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {vendors
                      .slice(vendorsPage * vendorsRowsPerPage, vendorsPage * vendorsRowsPerPage + vendorsRowsPerPage)
                      .map((v) => (
                      <TableRow key={v.id}>
                        <TableCell>{v.name}</TableCell>
                        <TableCell>{v.phone}</TableCell>
                        <TableCell>{v.service_categories}</TableCell>
                        <TableCell>
                          <Chip label={v.is_active ? 'Active' : 'Inactive'} color={v.is_active ? 'success' : 'default'} size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {vendors.length === 0 && (
                      <TableRow><TableCell colSpan={4}>No vendors</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={vendors.length}
                  page={vendorsPage}
                  onPageChange={(_, page) => setVendorsPage(page)}
                  rowsPerPage={vendorsRowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setVendorsRowsPerPage(parseInt(e.target.value, 10))
                    setVendorsPage(0)
                  }}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Technicians</Typography>
                <Stack spacing={2} mb={2}>
                  <TextField label="Name" value={technicianForm.name} onChange={(e) => setTechnicianForm((p) => ({ ...p, name: e.target.value }))} />
                  <TextField label="Phone" value={technicianForm.phone} onChange={(e) => setTechnicianForm((p) => ({ ...p, phone: e.target.value }))} />
                  <TextField label="Email" value={technicianForm.email} onChange={(e) => setTechnicianForm((p) => ({ ...p, email: e.target.value }))} />
                  <TextField label="Specialization" value={technicianForm.specialization} onChange={(e) => setTechnicianForm((p) => ({ ...p, specialization: e.target.value }))} />
                  <FormControl fullWidth size="small">
                    <InputLabel>Vendor</InputLabel>
                    <Select
                      label="Vendor"
                      value={technicianForm.vendor_id || ''}
                      onChange={(e) => setTechnicianForm((p) => ({ ...p, vendor_id: e.target.value }))}
                    >
                      <MenuItem value="">None</MenuItem>
                      {vendors.map((v) => (
                        <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <Button variant="contained" onClick={() => technicianMutation.mutate(technicianForm)}>Save Technician</Button>
                </Stack>
                <Divider sx={{ my: 2 }} />
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Specialization</TableCell>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {technicians
                      .slice(techniciansPage * techniciansRowsPerPage, techniciansPage * techniciansRowsPerPage + techniciansRowsPerPage)
                      .map((t) => (
                      <TableRow key={t.id}>
                        <TableCell>{t.name}</TableCell>
                        <TableCell>{t.specialization || '-'}</TableCell>
                        <TableCell>{vendors.find((v) => v.id === t.vendor_id)?.name || '-'}</TableCell>
                        <TableCell>
                          <Chip label={t.is_active ? 'Active' : 'Inactive'} color={t.is_active ? 'success' : 'default'} size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {technicians.length === 0 && (
                      <TableRow><TableCell colSpan={4}>No technicians</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={technicians.length}
                  page={techniciansPage}
                  onPageChange={(_, page) => setTechniciansPage(page)}
                  rowsPerPage={techniciansRowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setTechniciansRowsPerPage(parseInt(e.target.value, 10))
                    setTechniciansPage(0)
                  }}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Assets</Typography>
            <Grid container spacing={2} mb={2}>
              <Grid item xs={12} md={4}>
                <Stack spacing={2}>
                  <TextField label="Asset Number" value={assetForm.asset_number} onChange={(e) => setAssetForm((p) => ({ ...p, asset_number: e.target.value }))} />
                  <TextField label="Asset Type" value={assetForm.asset_type} onChange={(e) => setAssetForm((p) => ({ ...p, asset_type: e.target.value }))} />
                  <TextField label="Quarter" value={assetForm.quarter_number} onChange={(e) => setAssetForm((p) => ({ ...p, quarter_number: e.target.value }))} />
                  <TextField label="Make" value={assetForm.make} onChange={(e) => setAssetForm((p) => ({ ...p, make: e.target.value }))} />
                  <TextField label="Model" value={assetForm.model} onChange={(e) => setAssetForm((p) => ({ ...p, model: e.target.value }))} />
                  <TextField label="Serial" value={assetForm.serial_number} onChange={(e) => setAssetForm((p) => ({ ...p, serial_number: e.target.value }))} />
                  <TextField
                    label="Installation Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={assetForm.installation_date || ''}
                    onChange={(e) => setAssetForm((p) => ({ ...p, installation_date: e.target.value }))}
                  />
                  <TextField label="Status" value={assetForm.status} onChange={(e) => setAssetForm((p) => ({ ...p, status: e.target.value }))} />
                  <Button variant="contained" onClick={() => assetMutation.mutate(assetForm)}>Save Asset</Button>
                </Stack>
              </Grid>
              <Grid item xs={12} md={8}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>#</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Quarter</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Installed</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {assets
                      .slice(assetsPage * assetsRowsPerPage, assetsPage * assetsRowsPerPage + assetsRowsPerPage)
                      .map((a) => (
                      <TableRow key={a.id}>
                        <TableCell>{a.asset_number}</TableCell>
                        <TableCell>{a.asset_type}</TableCell>
                        <TableCell>{a.quarter_number}</TableCell>
                        <TableCell>{a.status}</TableCell>
                        <TableCell>{a.installation_date ? isoDate(new Date(a.installation_date)) : '-'}</TableCell>
                      </TableRow>
                    ))}
                    {assets.length === 0 && (
                      <TableRow><TableCell colSpan={5}>No assets</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={assets.length}
                  page={assetsPage}
                  onPageChange={(_, page) => setAssetsPage(page)}
                  rowsPerPage={assetsRowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setAssetsRowsPerPage(parseInt(e.target.value, 10))
                    setAssetsPage(0)
                  }}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Service Categories</Typography>
            <Grid container spacing={2} mb={2}>
              <Grid item xs={12} md={4}>
                <Stack spacing={2}>
                  <TextField label="Name" value={categoryForm.name} onChange={(e) => setCategoryForm((p) => ({ ...p, name: e.target.value }))} />
                  <TextField label="Description" value={categoryForm.description} onChange={(e) => setCategoryForm((p) => ({ ...p, description: e.target.value }))} />
                  <TextField
                    label="SLA Hours"
                    type="number"
                    value={categoryForm.sla_hours}
                    onChange={(e) => setCategoryForm((p) => ({ ...p, sla_hours: Number(e.target.value) }))}
                  />
                  <TextField label="Icon" value={categoryForm.icon} onChange={(e) => setCategoryForm((p) => ({ ...p, icon: e.target.value }))} />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={categoryForm.is_active ?? true}
                        onChange={(e) => setCategoryForm((p) => ({ ...p, is_active: e.target.checked }))}
                      />
                    }
                    label="Active"
                  />
                  <Button variant="contained" onClick={() => categoryMutation.mutate(categoryForm)}>Save Category</Button>
                </Stack>
              </Grid>
              <Grid item xs={12} md={8}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>SLA (hrs)</TableCell>
                      <TableCell>Active</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {categories
                      .slice(categoriesPage * categoriesRowsPerPage, categoriesPage * categoriesRowsPerPage + categoriesRowsPerPage)
                      .map((c) => (
                      <TableRow key={c.id}>
                        <TableCell>{c.name}</TableCell>
                        <TableCell>{c.sla_hours}</TableCell>
                        <TableCell>
                          <Chip label={c.is_active ? 'Yes' : 'No'} color={c.is_active ? 'success' : 'default'} size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {categories.length === 0 && (
                      <TableRow><TableCell colSpan={3}>No categories</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={categories.length}
                  page={categoriesPage}
                  onPageChange={(_, page) => setCategoriesPage(page)}
                  rowsPerPage={categoriesRowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setCategoriesRowsPerPage(parseInt(e.target.value, 10))
                    setCategoriesPage(0)
                  }}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recurring Maintenance</Typography>
            <Grid container spacing={2} mb={2}>
              <Grid item xs={12} md={4}>
                <Stack spacing={2}>
                  <TextField label="Name" value={recurringForm.name} onChange={(e) => setRecurringForm((p) => ({ ...p, name: e.target.value }))} />
                  <TextField label="Description" value={recurringForm.description} onChange={(e) => setRecurringForm((p) => ({ ...p, description: e.target.value }))} />
                  <FormControl fullWidth size="small">
                    <InputLabel>Category</InputLabel>
                    <Select
                      label="Category"
                      value={recurringForm.category}
                      onChange={(e) => setRecurringForm((p) => ({ ...p, category: e.target.value }))}
                    >
                      {categories.map((c) => (
                        <MenuItem key={c.id} value={c.name}>{c.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControl fullWidth size="small">
                    <InputLabel>Frequency</InputLabel>
                    <Select
                      label="Frequency"
                      value={recurringForm.frequency}
                      onChange={(e) => setRecurringForm((p) => ({ ...p, frequency: e.target.value }))}
                    >
                      {frequencies.map((f) => (
                        <MenuItem key={f} value={f}>{f}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    label="Next Schedule"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={recurringForm.next_schedule_date}
                    onChange={(e) => setRecurringForm((p) => ({ ...p, next_schedule_date: e.target.value }))}
                  />
                  <FormControl fullWidth size="small">
                    <InputLabel>Vendor</InputLabel>
                    <Select
                      label="Vendor"
                      value={recurringForm.assigned_vendor_id || ''}
                      onChange={(e) => setRecurringForm((p) => ({ ...p, assigned_vendor_id: e.target.value }))}
                    >
                      <MenuItem value="">None</MenuItem>
                      {vendors.map((v) => (
                        <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={recurringForm.is_active ?? true}
                        onChange={(e) => setRecurringForm((p) => ({ ...p, is_active: e.target.checked }))}
                      />
                    }
                    label="Active"
                  />
                  <Button variant="contained" onClick={() => recurringMutation.mutate(recurringForm)}>Save Recurring Task</Button>
                </Stack>
              </Grid>
              <Grid item xs={12} md={8}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Frequency</TableCell>
                      <TableCell>Next</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recurring
                      .slice(recurringPage * recurringRowsPerPage, recurringPage * recurringRowsPerPage + recurringRowsPerPage)
                      .map((r) => (
                      <TableRow key={r.id}>
                        <TableCell>{r.name}</TableCell>
                        <TableCell>{r.category}</TableCell>
                        <TableCell>{r.frequency}</TableCell>
                        <TableCell>{isoDate(new Date(r.next_schedule_date))}</TableCell>
                        <TableCell>
                          <Chip label={r.is_active ? 'Active' : 'Paused'} color={r.is_active ? 'success' : 'default'} size="small" />
                        </TableCell>
                      </TableRow>
                    ))}
                    {recurring.length === 0 && (
                      <TableRow><TableCell colSpan={5}>No recurring tasks</TableCell></TableRow>
                    )}
                  </TableBody>
                </Table>
                <TablePagination
                  component="div"
                  count={recurring.length}
                  page={recurringPage}
                  onPageChange={(_, page) => setRecurringPage(page)}
                  rowsPerPage={recurringRowsPerPage}
                  onRowsPerPageChange={(e) => {
                    setRecurringRowsPerPage(parseInt(e.target.value, 10))
                    setRecurringPage(0)
                  }}
                  rowsPerPageOptions={[5, 10, 25, 50]}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Maintenance Request</DialogTitle>
        <DialogContent sx={{ pt: 1 }}>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Quarter Number"
              value={requestForm.quarter_number}
              placeholder="Examples: Q1-101, A-102"
              helperText="Enter the quarter/house number (e.g., Q1-101)."
              onChange={(e) => setRequestForm((p) => ({ ...p, quarter_number: e.target.value }))}
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                label="Category"
                value={requestForm.category}
                onChange={(e) => setRequestForm((p) => ({ ...p, category: e.target.value }))}
              >
                {categories.map((c) => (
                  <MenuItem key={c.id} value={c.name}>{c.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Sub Category</InputLabel>
              <Select
                label="Sub Category"
                value={requestForm.sub_category || ''}
                onChange={(e) => setRequestForm((p) => ({ ...p, sub_category: e.target.value }))}
              >
                {(subCategoryOptions[requestForm.category] || ['Other']).map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Description"
              multiline
              minRows={3}
              value={requestForm.description}
              onChange={(e) => setRequestForm((p) => ({ ...p, description: e.target.value }))}
            />
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                label="Priority"
                value={requestForm.priority}
                onChange={(e) => setRequestForm((p) => ({ ...p, priority: e.target.value }))}
              >
                {priorities.map((p) => (
                  <MenuItem key={p} value={p}>{p}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreateRequest} disabled={createRequestMutation.isPending}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
