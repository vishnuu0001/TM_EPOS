import { useMemo, useState } from 'react'
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  TablePagination,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-toastify'
import canteenService, {
  type DashboardStats,
  type Worker,
  type WorkerPayload,
  type WorkerType,
  type MealType,
  type Menu,
  type MenuPayload,
  type MenuItem as CanteenMenuItem,
  type MenuItemPayload,
  type Order,
  type OrderPayload,
  type OrderStatus,
  type InventoryItem,
  type InventoryPayload,
  type Feedback,
  type FeedbackPayload,
  type Consumption,
  type ConsumptionPayload,
} from '../../services/canteenService'

const workerTypes: WorkerType[] = ['permanent', 'contract', 'casual', 'temporary']
const mealTypes: MealType[] = ['breakfast', 'lunch', 'dinner', 'snacks']
const orderStatuses: OrderStatus[] = ['pending', 'confirmed', 'preparing', 'ready', 'served', 'cancelled']

const isoDate = (d: Date) => d.toISOString().slice(0, 10)

export default function Canteen() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState(0)

  const [workersPage, setWorkersPage] = useState(0)
  const [workersRowsPerPage, setWorkersRowsPerPage] = useState(10)
  const [menusPage, setMenusPage] = useState(0)
  const [menusRowsPerPage, setMenusRowsPerPage] = useState(10)
  const [menuItemsPage, setMenuItemsPage] = useState(0)
  const [menuItemsRowsPerPage, setMenuItemsRowsPerPage] = useState(10)
  const [ordersPage, setOrdersPage] = useState(0)
  const [ordersRowsPerPage, setOrdersRowsPerPage] = useState(10)
  const [inventoryPage, setInventoryPage] = useState(0)
  const [inventoryRowsPerPage, setInventoryRowsPerPage] = useState(10)
  const [feedbackPage, setFeedbackPage] = useState(0)
  const [feedbackRowsPerPage, setFeedbackRowsPerPage] = useState(10)
  const [consumptionsPage, setConsumptionsPage] = useState(0)
  const [consumptionsRowsPerPage, setConsumptionsRowsPerPage] = useState(10)

  const [workerForm, setWorkerForm] = useState<WorkerPayload>({
    full_name: '',
    employee_id: '',
    worker_type: 'permanent',
    department: '',
    designation: '',
    phone: '',
    email: '',
    subsidy_applicable: true,
  })

  const [menuForm, setMenuForm] = useState<MenuPayload>({
    menu_date: isoDate(new Date()),
    meal_type: 'lunch',
    menu_name: '',
    description: '',
  })

  const [menuItemForm, setMenuItemForm] = useState<MenuItemPayload>({
    menu_id: '',
    item_name: '',
    base_price: 0,
    subsidized_price: 0,
    category: '',
    item_name_hindi: '',
    description: '',
    is_vegetarian: true,
    is_vegan: false,
    display_order: 0,
  })

  const [orderForm, setOrderForm] = useState<OrderPayload & { itemsText: string }>(
    {
      worker_id: '',
      menu_id: '',
      meal_type: 'lunch',
      items: [],
      itemsText: '[{"item_id":"","quantity":1}]',
      total_amount: 0,
      subsidy_amount: 0,
      payable_amount: 0,
      payment_method: 'wallet',
    }
  )

  const [inventoryForm, setInventoryForm] = useState<InventoryPayload>({
    item_name: '',
    unit: 'kg',
    category: '',
    current_stock: 0,
    reorder_level: 0,
    unit_price: 0,
  })

  const [feedbackForm, setFeedbackForm] = useState<FeedbackPayload>({
    worker_id: '',
    meal_type: 'lunch',
    overall_rating: 4,
    comments: '',
    suggestions: '',
    complaint: false,
  })

  const [consumptionForm, setConsumptionForm] = useState<ConsumptionPayload>({
    order_id: '',
    worker_id: '',
    meal_type: 'lunch',
    consumption_date: isoDate(new Date()),
    items_ordered: '[]',
    items_consumed: '[]',
    items_wasted: '[]',
    wastage_percentage: 0,
    meal_completed: true,
  })

  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ['canteenStats'],
    queryFn: canteenService.getDashboardStats,
  })

  const { data: workers = [] } = useQuery<Worker[]>({
    queryKey: ['canteenWorkers'],
    queryFn: canteenService.getWorkers,
  })

  const { data: menus = [] } = useQuery<Menu[]>({
    queryKey: ['canteenMenus'],
    queryFn: canteenService.getMenus,
  })

  const { data: orders = [] } = useQuery<Order[]>({
    queryKey: ['canteenOrders'],
    queryFn: canteenService.getOrders,
  })

  const { data: inventory = [] } = useQuery<InventoryItem[]>({
    queryKey: ['canteenInventory'],
    queryFn: canteenService.getInventory,
  })

  const { data: feedback = [] } = useQuery<Feedback[]>({
    queryKey: ['canteenFeedback'],
    queryFn: canteenService.getFeedback,
  })

  const { data: consumptions = [] } = useQuery<Consumption[]>({
    queryKey: ['canteenConsumptions'],
    queryFn: canteenService.getConsumptions,
  })

  const menuItemsMap = useMemo(() => new Map<string, CanteenMenuItem[]>(), [])

  const workerMutation = useMutation({
    mutationFn: canteenService.createWorker,
    onSuccess: () => {
      toast.success('Worker added')
      queryClient.invalidateQueries({ queryKey: ['canteenWorkers'] })
      setWorkerForm({ full_name: '', employee_id: '', worker_type: 'permanent', department: '', designation: '', phone: '', email: '', subsidy_applicable: true })
    },
  })

  const menuMutation = useMutation({
    mutationFn: canteenService.createMenu,
    onSuccess: () => {
      toast.success('Menu created')
      queryClient.invalidateQueries({ queryKey: ['canteenMenus'] })
    },
  })

  const menuItemMutation = useMutation({
    mutationFn: canteenService.createMenuItem,
    onSuccess: () => {
      toast.success('Menu item added')
      if (menuItemForm.menu_id) {
        queryClient.invalidateQueries({ queryKey: ['canteenMenuItems', menuItemForm.menu_id] })
      }
      setMenuItemForm((p) => ({ ...p, item_name: '', base_price: 0, subsidized_price: 0, display_order: 0 }))
    },
  })

  const orderMutation = useMutation({
    mutationFn: canteenService.createOrder,
    onSuccess: () => {
      toast.success('Order placed')
      queryClient.invalidateQueries({ queryKey: ['canteenOrders'] })
    },
  })

  const orderStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: OrderStatus }) => canteenService.updateOrderStatus(id, status),
    onSuccess: () => {
      toast.success('Order status updated')
      queryClient.invalidateQueries({ queryKey: ['canteenOrders'] })
    },
  })

  const inventoryMutation = useMutation({
    mutationFn: canteenService.createInventory,
    onSuccess: () => {
      toast.success('Inventory saved')
      queryClient.invalidateQueries({ queryKey: ['canteenInventory'] })
      setInventoryForm({ item_name: '', unit: 'kg', category: '', current_stock: 0, reorder_level: 0, unit_price: 0 })
    },
  })

  const feedbackMutation = useMutation({
    mutationFn: canteenService.submitFeedback,
    onSuccess: () => {
      toast.success('Feedback submitted')
      queryClient.invalidateQueries({ queryKey: ['canteenFeedback'] })
      setFeedbackForm({ worker_id: '', meal_type: 'lunch', overall_rating: 4, comments: '', suggestions: '', complaint: false })
    },
  })

  const consumptionMutation = useMutation({
    mutationFn: canteenService.recordConsumption,
    onSuccess: () => {
      toast.success('Consumption recorded')
      queryClient.invalidateQueries({ queryKey: ['canteenConsumptions'] })
    },
  })

  const loadMenuItems = async (menuId: string) => {
    if (!menuId || menuItemsMap.has(menuId)) return
    const items = await canteenService.getMenuItems(menuId)
    menuItemsMap.set(menuId, items)
    queryClient.setQueryData(['canteenMenuItems', menuId], items)
  }

  const cards = [
    { label: 'Active Workers', value: stats?.total_workers ?? 0 },
    { label: 'Today Orders', value: stats?.today_orders ?? 0 },
    { label: 'Today Consumption', value: stats?.today_consumption ?? 0 },
    { label: 'Pending Orders', value: stats?.pending_orders ?? 0 },
    { label: 'Low Stock Items', value: stats?.low_stock_items ?? 0 },
    { label: 'Average Rating', value: stats?.average_rating ?? 0 },
    { label: 'Today Revenue', value: stats?.today_revenue ?? 0 },
  ]

  const handleCreateOrder = () => {
    try {
      const parsed = JSON.parse(orderForm.itemsText || '[]')
      orderMutation.mutate({
        worker_id: orderForm.worker_id,
        menu_id: orderForm.menu_id || undefined,
        meal_type: orderForm.meal_type,
        items: parsed,
        total_amount: orderForm.total_amount,
        subsidy_amount: orderForm.subsidy_amount ?? 0,
        payable_amount: orderForm.payable_amount,
        payment_method: orderForm.payment_method,
      })
    } catch (e) {
      toast.error('Items must be valid JSON')
    }
  }

  const renderDashboard = () => (
    <Box>
      <Grid container spacing={2} mb={3}>
        {cards.map((c) => (
          <Grid item xs={12} sm={6} md={3} key={c.label}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>{c.label}</Typography>
                <Typography variant="h5">{c.value}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h6" gutterBottom>Recent Orders</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Order #</TableCell>
              <TableCell>Worker</TableCell>
              <TableCell>Meal</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Total</TableCell>
              <TableCell>Time</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.slice(0, 5).map((o) => (
              <TableRow key={o.id}>
                <TableCell>{o.order_number}</TableCell>
                <TableCell>{o.worker_id}</TableCell>
                <TableCell>{o.meal_type}</TableCell>
                <TableCell><Chip label={o.status} size="small" /></TableCell>
                <TableCell>₹{o.total_amount}</TableCell>
                <TableCell>{new Date(o.order_time).toLocaleString()}</TableCell>
              </TableRow>
            ))}
            {orders.length === 0 && <TableRow><TableCell colSpan={6} align="center">No orders yet</TableCell></TableRow>}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )

  const renderWorkers = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Add Worker</Typography>
            <Stack spacing={2}>
              <TextField label="Full Name" value={workerForm.full_name} onChange={(e) => setWorkerForm((p) => ({ ...p, full_name: e.target.value }))} />
              <TextField label="Employee ID" value={workerForm.employee_id} onChange={(e) => setWorkerForm((p) => ({ ...p, employee_id: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select label="Type" value={workerForm.worker_type} onChange={(e) => setWorkerForm((p) => ({ ...p, worker_type: e.target.value as WorkerType }))}>
                  {workerTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField label="Department" value={workerForm.department} onChange={(e) => setWorkerForm((p) => ({ ...p, department: e.target.value }))} />
              <TextField label="Designation" value={workerForm.designation} onChange={(e) => setWorkerForm((p) => ({ ...p, designation: e.target.value }))} />
              <TextField label="Phone" value={workerForm.phone} onChange={(e) => setWorkerForm((p) => ({ ...p, phone: e.target.value }))} />
              <TextField label="Email" value={workerForm.email} onChange={(e) => setWorkerForm((p) => ({ ...p, email: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                if (!workerForm.full_name || !workerForm.employee_id) {
                  toast.error('Name and Employee ID required')
                  return
                }
                workerMutation.mutate(workerForm)
              }} disabled={workerMutation.isPending}>Save Worker</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Workers</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>#</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Dept</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {workers
                    .slice(
                      workersPage * workersRowsPerPage,
                      workersPage * workersRowsPerPage + workersRowsPerPage,
                    )
                    .map((w) => (
                    <TableRow key={w.id}>
                      <TableCell>{w.worker_number}</TableCell>
                      <TableCell>{w.full_name}</TableCell>
                      <TableCell>{w.worker_type}</TableCell>
                      <TableCell>{w.department || '-'}</TableCell>
                      <TableCell><Chip label={w.is_active ? 'Active' : 'Inactive'} size="small" color={w.is_active ? 'success' : 'default'} /></TableCell>
                    </TableRow>
                  ))}
                  {workers.length === 0 && <TableRow><TableCell colSpan={5} align="center">No workers</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={workers.length}
              page={workersPage}
              onPageChange={(_, newPage) => setWorkersPage(newPage)}
              rowsPerPage={workersRowsPerPage}
              onRowsPerPageChange={(event) => {
                setWorkersRowsPerPage(Number(event.target.value))
                setWorkersPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderMenus = () => {
    const menuItems = menuItemForm.menu_id
      ? (queryClient.getQueryData<CanteenMenuItem[]>(['canteenMenuItems', menuItemForm.menu_id]) || [])
      : []

    return (
      <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Create Menu</Typography>
            <Stack spacing={2}>
              <TextField label="Menu Name" value={menuForm.menu_name} onChange={(e) => setMenuForm((p) => ({ ...p, menu_name: e.target.value }))} />
              <TextField label="Description" value={menuForm.description} onChange={(e) => setMenuForm((p) => ({ ...p, description: e.target.value }))} />
              <TextField label="Date" type="date" InputLabelProps={{ shrink: true }} value={menuForm.menu_date} onChange={(e) => setMenuForm((p) => ({ ...p, menu_date: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Meal</InputLabel>
                <Select label="Meal" value={menuForm.meal_type} onChange={(e) => setMenuForm((p) => ({ ...p, meal_type: e.target.value as MealType }))}>
                  {mealTypes.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
                </Select>
              </FormControl>
              <Button variant="contained" onClick={() => menuMutation.mutate(menuForm)} disabled={menuMutation.isPending}>Create Menu</Button>
            </Stack>
          </CardContent>
        </Card>
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Add Menu Item</Typography>
            <Stack spacing={2}>
              <FormControl fullWidth>
                <InputLabel>Menu</InputLabel>
                <Select
                  label="Menu"
                  value={menuItemForm.menu_id}
                  onChange={(e) => {
                    const val = e.target.value
                    setMenuItemForm((p) => ({ ...p, menu_id: val }))
                    loadMenuItems(val)
                  }}
                >
                  {menus.map((m) => <MenuItem key={m.id} value={m.id}>{m.menu_name || `${m.meal_type} - ${m.menu_date}`}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField label="Item Name" value={menuItemForm.item_name} onChange={(e) => setMenuItemForm((p) => ({ ...p, item_name: e.target.value }))} />
              <TextField label="Category" value={menuItemForm.category} onChange={(e) => setMenuItemForm((p) => ({ ...p, category: e.target.value }))} />
              <TextField label="Base Price" type="number" value={menuItemForm.base_price} onChange={(e) => setMenuItemForm((p) => ({ ...p, base_price: Number(e.target.value) }))} />
              <TextField label="Subsidized Price" type="number" value={menuItemForm.subsidized_price} onChange={(e) => setMenuItemForm((p) => ({ ...p, subsidized_price: Number(e.target.value) }))} />
              <TextField label="Display Order" type="number" value={menuItemForm.display_order || 0} onChange={(e) => setMenuItemForm((p) => ({ ...p, display_order: Number(e.target.value) }))} />
              <Button variant="contained" onClick={() => {
                if (!menuItemForm.menu_id || !menuItemForm.item_name) {
                  toast.error('Menu and item name are required')
                  return
                }
                menuItemMutation.mutate(menuItemForm)
              }} disabled={menuItemMutation.isPending}>Add Item</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Menus</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Meal</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Published</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {menus
                    .slice(
                      menusPage * menusRowsPerPage,
                      menusPage * menusRowsPerPage + menusRowsPerPage,
                    )
                    .map((m) => (
                    <TableRow key={m.id} hover onClick={() => loadMenuItems(m.id)}>
                      <TableCell>{m.menu_date}</TableCell>
                      <TableCell>{m.meal_type}</TableCell>
                      <TableCell>{m.menu_name || '-'}</TableCell>
                      <TableCell><Chip label={m.is_published ? 'Yes' : 'No'} size="small" color={m.is_published ? 'success' : 'default'} /></TableCell>
                    </TableRow>
                  ))}
                  {menus.length === 0 && <TableRow><TableCell colSpan={4} align="center">No menus</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={menus.length}
              page={menusPage}
              onPageChange={(_, newPage) => setMenusPage(newPage)}
              rowsPerPage={menusRowsPerPage}
              onRowsPerPageChange={(event) => {
                setMenusRowsPerPage(Number(event.target.value))
                setMenusPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Menu Items (selected menu)</Typography>
            <Typography variant="body2" color="text.secondary" mb={1}>Pick a menu to load items.</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Price</TableCell>
                    <TableCell>Available</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {menuItems
                    .slice(
                      menuItemsPage * menuItemsRowsPerPage,
                      menuItemsPage * menuItemsRowsPerPage + menuItemsRowsPerPage,
                    )
                    .map((i) => (
                    <TableRow key={i.id}>
                      <TableCell>{i.item_name}</TableCell>
                      <TableCell>{i.category || '-'}</TableCell>
                      <TableCell>₹{i.subsidized_price || i.base_price}</TableCell>
                      <TableCell><Chip label={i.is_available ? 'Yes' : 'No'} size="small" /></TableCell>
                    </TableRow>
                  ))}
                  {(!menuItemForm.menu_id || menuItems.length === 0) && (
                    <TableRow><TableCell colSpan={4} align="center">No items</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={menuItems.length}
              page={menuItemsPage}
              onPageChange={(_, newPage) => setMenuItemsPage(newPage)}
              rowsPerPage={menuItemsRowsPerPage}
              onRowsPerPageChange={(event) => {
                setMenuItemsRowsPerPage(Number(event.target.value))
                setMenuItemsPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
    )
  }

  const renderOrders = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Create Order</Typography>
            <Stack spacing={2}>
              <TextField label="Worker ID" value={orderForm.worker_id} onChange={(e) => setOrderForm((p) => ({ ...p, worker_id: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Meal</InputLabel>
                <Select label="Meal" value={orderForm.meal_type} onChange={(e) => setOrderForm((p) => ({ ...p, meal_type: e.target.value as MealType }))}>
                  {mealTypes.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Menu (optional)</InputLabel>
                <Select label="Menu (optional)" value={orderForm.menu_id} onChange={(e) => setOrderForm((p) => ({ ...p, menu_id: e.target.value }))}>
                  <MenuItem value="">None</MenuItem>
                  {menus.map((m) => <MenuItem key={m.id} value={m.id}>{m.menu_name || `${m.meal_type} ${m.menu_date}`}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField label="Items JSON" multiline minRows={3} value={orderForm.itemsText} onChange={(e) => setOrderForm((p) => ({ ...p, itemsText: e.target.value }))} helperText='Example: [{"item_id":"abc","quantity":1,"unit_price":40}]' />
              <TextField label="Total Amount" type="number" value={orderForm.total_amount} onChange={(e) => setOrderForm((p) => ({ ...p, total_amount: Number(e.target.value) }))} />
              <TextField label="Subsidy" type="number" value={orderForm.subsidy_amount ?? 0} onChange={(e) => setOrderForm((p) => ({ ...p, subsidy_amount: Number(e.target.value) }))} />
              <TextField label="Payable" type="number" value={orderForm.payable_amount} onChange={(e) => setOrderForm((p) => ({ ...p, payable_amount: Number(e.target.value) }))} />
              <Button variant="contained" onClick={handleCreateOrder} disabled={orderMutation.isPending}>Place Order</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Orders</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Order #</TableCell>
                    <TableCell>Worker</TableCell>
                    <TableCell>Meal</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Total</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders
                    .slice(
                      ordersPage * ordersRowsPerPage,
                      ordersPage * ordersRowsPerPage + ordersRowsPerPage,
                    )
                    .map((o) => (
                    <TableRow key={o.id}>
                      <TableCell>{o.order_number}</TableCell>
                      <TableCell>{o.worker_id}</TableCell>
                      <TableCell>{o.meal_type}</TableCell>
                      <TableCell><Chip label={o.status} size="small" /></TableCell>
                      <TableCell>₹{o.total_amount}</TableCell>
                      <TableCell>
                        <Stack direction="row" spacing={1}>
                          {orderStatuses.map((s) => (
                            <Button key={s} size="small" onClick={() => orderStatusMutation.mutate({ id: o.id, status: s })} disabled={orderStatusMutation.isPending}>{s}</Button>
                          ))}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  ))}
                  {orders.length === 0 && <TableRow><TableCell colSpan={6} align="center">No orders</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={orders.length}
              page={ordersPage}
              onPageChange={(_, newPage) => setOrdersPage(newPage)}
              rowsPerPage={ordersRowsPerPage}
              onRowsPerPageChange={(event) => {
                setOrdersRowsPerPage(Number(event.target.value))
                setOrdersPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderInventory = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Add Inventory</Typography>
            <Stack spacing={2}>
              <TextField label="Item Name" value={inventoryForm.item_name} onChange={(e) => setInventoryForm((p) => ({ ...p, item_name: e.target.value }))} />
              <TextField label="Category" value={inventoryForm.category} onChange={(e) => setInventoryForm((p) => ({ ...p, category: e.target.value }))} />
              <TextField label="Unit" value={inventoryForm.unit} onChange={(e) => setInventoryForm((p) => ({ ...p, unit: e.target.value }))} />
              <TextField label="Stock" type="number" value={inventoryForm.current_stock ?? 0} onChange={(e) => setInventoryForm((p) => ({ ...p, current_stock: Number(e.target.value) }))} />
              <TextField label="Reorder Level" type="number" value={inventoryForm.reorder_level ?? 0} onChange={(e) => setInventoryForm((p) => ({ ...p, reorder_level: Number(e.target.value) }))} />
              <TextField label="Unit Price" type="number" value={inventoryForm.unit_price ?? 0} onChange={(e) => setInventoryForm((p) => ({ ...p, unit_price: Number(e.target.value) }))} />
              <Button variant="contained" onClick={() => {
                if (!inventoryForm.item_name) {
                  toast.error('Item name required')
                  return
                }
                inventoryMutation.mutate(inventoryForm)
              }} disabled={inventoryMutation.isPending}>Save Item</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Inventory</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Code</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Stock</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {inventory
                    .slice(
                      inventoryPage * inventoryRowsPerPage,
                      inventoryPage * inventoryRowsPerPage + inventoryRowsPerPage,
                    )
                    .map((i) => (
                    <TableRow key={i.id}>
                      <TableCell>{i.item_code}</TableCell>
                      <TableCell>{i.item_name}</TableCell>
                      <TableCell>{i.current_stock}</TableCell>
                      <TableCell><Chip label={i.status} size="small" color={i.status === 'low_stock' || i.status === 'out_of_stock' ? 'error' : 'success'} /></TableCell>
                    </TableRow>
                  ))}
                  {inventory.length === 0 && <TableRow><TableCell colSpan={4} align="center">No items</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={inventory.length}
              page={inventoryPage}
              onPageChange={(_, newPage) => setInventoryPage(newPage)}
              rowsPerPage={inventoryRowsPerPage}
              onRowsPerPageChange={(event) => {
                setInventoryRowsPerPage(Number(event.target.value))
                setInventoryPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderFeedback = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Submit Feedback</Typography>
            <Stack spacing={2}>
              <TextField label="Worker ID" value={feedbackForm.worker_id} onChange={(e) => setFeedbackForm((p) => ({ ...p, worker_id: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Meal</InputLabel>
                <Select label="Meal" value={feedbackForm.meal_type} onChange={(e) => setFeedbackForm((p) => ({ ...p, meal_type: e.target.value as MealType }))}>
                  {mealTypes.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField label="Overall Rating (1-5)" type="number" value={feedbackForm.overall_rating ?? ''} onChange={(e) => setFeedbackForm((p) => ({ ...p, overall_rating: Number(e.target.value) }))} />
              <TextField label="Comments" multiline minRows={2} value={feedbackForm.comments} onChange={(e) => setFeedbackForm((p) => ({ ...p, comments: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                if (!feedbackForm.worker_id) {
                  toast.error('Worker ID required')
                  return
                }
                feedbackMutation.mutate(feedbackForm)
              }} disabled={feedbackMutation.isPending}>Send Feedback</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Feedback</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Worker</TableCell>
                    <TableCell>Meal</TableCell>
                    <TableCell>Rating</TableCell>
                    <TableCell>Comment</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {feedback
                    .slice(
                      feedbackPage * feedbackRowsPerPage,
                      feedbackPage * feedbackRowsPerPage + feedbackRowsPerPage,
                    )
                    .map((f) => (
                    <TableRow key={f.id}>
                      <TableCell>{f.worker_id}</TableCell>
                      <TableCell>{f.meal_type}</TableCell>
                      <TableCell>{f.overall_rating ?? '-'}</TableCell>
                      <TableCell>{f.comments || '-'}</TableCell>
                    </TableRow>
                  ))}
                  {feedback.length === 0 && <TableRow><TableCell colSpan={4} align="center">No feedback</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={feedback.length}
              page={feedbackPage}
              onPageChange={(_, newPage) => setFeedbackPage(newPage)}
              rowsPerPage={feedbackRowsPerPage}
              onRowsPerPageChange={(event) => {
                setFeedbackRowsPerPage(Number(event.target.value))
                setFeedbackPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  )

  const renderConsumption = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Record Consumption</Typography>
            <Stack spacing={2}>
              <TextField label="Order ID" value={consumptionForm.order_id} onChange={(e) => setConsumptionForm((p) => ({ ...p, order_id: e.target.value }))} />
              <TextField label="Worker ID" value={consumptionForm.worker_id} onChange={(e) => setConsumptionForm((p) => ({ ...p, worker_id: e.target.value }))} />
              <FormControl fullWidth>
                <InputLabel>Meal</InputLabel>
                <Select label="Meal" value={consumptionForm.meal_type} onChange={(e) => setConsumptionForm((p) => ({ ...p, meal_type: e.target.value as MealType }))}>
                  {mealTypes.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
                </Select>
              </FormControl>
              <TextField label="Date" type="date" InputLabelProps={{ shrink: true }} value={consumptionForm.consumption_date} onChange={(e) => setConsumptionForm((p) => ({ ...p, consumption_date: e.target.value }))} />
              <TextField label="Items Ordered JSON" multiline minRows={2} value={consumptionForm.items_ordered} onChange={(e) => setConsumptionForm((p) => ({ ...p, items_ordered: e.target.value }))} />
              <TextField label="Items Consumed JSON" multiline minRows={2} value={consumptionForm.items_consumed} onChange={(e) => setConsumptionForm((p) => ({ ...p, items_consumed: e.target.value }))} />
              <TextField label="Items Wasted JSON" multiline minRows={2} value={consumptionForm.items_wasted} onChange={(e) => setConsumptionForm((p) => ({ ...p, items_wasted: e.target.value }))} />
              <Button variant="contained" onClick={() => {
                try {
                  JSON.parse(consumptionForm.items_ordered || '[]')
                  JSON.parse(consumptionForm.items_consumed || '[]')
                  JSON.parse(consumptionForm.items_wasted || '[]')
                } catch {
                  toast.error('Items must be JSON')
                  return
                }
                consumptionMutation.mutate(consumptionForm)
              }} disabled={consumptionMutation.isPending}>Record</Button>
            </Stack>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Consumption Logs</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Order</TableCell>
                    <TableCell>Worker</TableCell>
                    <TableCell>Meal</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {consumptions
                    .slice(
                      consumptionsPage * consumptionsRowsPerPage,
                      consumptionsPage * consumptionsRowsPerPage + consumptionsRowsPerPage,
                    )
                    .map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.order_id}</TableCell>
                      <TableCell>{c.worker_id}</TableCell>
                      <TableCell>{c.meal_type}</TableCell>
                      <TableCell>{c.consumption_date}</TableCell>
                    </TableRow>
                  ))}
                  {consumptions.length === 0 && <TableRow><TableCell colSpan={4} align="center">No records</TableCell></TableRow>}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={consumptions.length}
              page={consumptionsPage}
              onPageChange={(_, newPage) => setConsumptionsPage(newPage)}
              rowsPerPage={consumptionsRowsPerPage}
              onRowsPerPageChange={(event) => {
                setConsumptionsRowsPerPage(Number(event.target.value))
                setConsumptionsPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
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
          <Typography variant="h4" fontWeight={600}>Canteen Management System</Typography>
          <Typography variant="body1" color="text.secondary">Meal ordering, consumption tracking, and kiosk operations</Typography>
        </Box>
        <Button variant="outlined" onClick={() => {
          queryClient.invalidateQueries({ queryKey: ['canteenStats'] })
          queryClient.invalidateQueries({ queryKey: ['canteenWorkers'] })
          queryClient.invalidateQueries({ queryKey: ['canteenMenus'] })
          queryClient.invalidateQueries({ queryKey: ['canteenOrders'] })
          queryClient.invalidateQueries({ queryKey: ['canteenInventory'] })
          queryClient.invalidateQueries({ queryKey: ['canteenFeedback'] })
          queryClient.invalidateQueries({ queryKey: ['canteenConsumptions'] })
          if (menuItemForm.menu_id) {
            queryClient.invalidateQueries({ queryKey: ['canteenMenuItems', menuItemForm.menu_id] })
          }
        }}>Refresh</Button>
      </Box>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab label="Dashboard" />
        <Tab label="Workers" />
        <Tab label="Menus" />
        <Tab label="Orders" />
        <Tab label="Inventory" />
        <Tab label="Feedback" />
        <Tab label="Consumption" />
      </Tabs>

      {tab === 0 && renderDashboard()}
      {tab === 1 && renderWorkers()}
      {tab === 2 && renderMenus()}
      {tab === 3 && renderOrders()}
      {tab === 4 && renderInventory()}
      {tab === 5 && renderFeedback()}
      {tab === 6 && renderConsumption()}
    </Box>
  )
}
