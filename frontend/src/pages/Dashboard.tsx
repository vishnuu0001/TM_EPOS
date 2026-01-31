import { useState } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Tabs,
  Tab,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TablePagination,
} from '@mui/material'
import {
  TrendingUp,
  People,
  CheckCircle,
  Warning,
} from '@mui/icons-material'
import { useQueries } from '@tanstack/react-query'
import { colonyService } from '../services/colonyService'
import guesthouseService from '../services/guesthouseService'
import vehicleService from '../services/vehicleService'
import visitorService from '../services/visitorService'
import equipmentService from '../services/equipmentService'
import vigilanceService from '../services/vigilanceService'
import canteenService from '../services/canteenService'
import { useSelector } from 'react-redux'
import { RootState } from '../store'

// Stat Card Component
const StatCard = ({ title, value, icon, color }: any) => (
  <Card
    sx={{
      height: '100%',
      borderRadius: 3,
      boxShadow: '0 8px 24px rgba(0,0,0,0.08)',
      border: '1px solid',
      borderColor: 'divider',
    }}
  >
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Box
          sx={{
            width: 50,
            height: 50,
            borderRadius: '50%',
            bgcolor: `${color}.light`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: `${color}.main`,
          }}
        >
          {icon}
        </Box>
        <TrendingUp sx={{ color: 'success.main' }} />
      </Box>
      <Typography variant="h4" fontWeight={600} gutterBottom>
        {value}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {title}
      </Typography>
    </CardContent>
  </Card>
)

const TabPanel = ({ value, index, children }: { value: number; index: number; children: JSX.Element }) => (
  <Box role="tabpanel" hidden={value !== index} sx={{ pt: 2 }}>
    {value === index ? children : null}
  </Box>
)

export default function Dashboard() {
  const user = useSelector((state: RootState) => state.auth.user)
  const [activitiesPage, setActivitiesPage] = useState(0)
  const [activitiesRowsPerPage, setActivitiesRowsPerPage] = useState(5)
  const [activeTab, setActiveTab] = useState(0)
  const [
    colonyQuery,
    guestQuery,
    equipmentQuery,
    vigilanceQuery,
    vehicleQuery,
    visitorQuery,
    canteenQuery,
  ] = useQueries({
    queries: [
      { queryKey: ['dashboard-colony'], queryFn: colonyService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-guesthouse'], queryFn: guesthouseService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-equipment'], queryFn: equipmentService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-vigilance'], queryFn: vigilanceService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-vehicle'], queryFn: vehicleService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-visitor'], queryFn: visitorService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
      { queryKey: ['dashboard-canteen'], queryFn: canteenService.getDashboardStats, enabled: !!user, refetchOnMount: 'always', refetchOnWindowFocus: true, staleTime: 0 },
    ],
  }) as const

  const recentActivities = [
    {
      id: 1,
      module: 'Colony Maintenance',
      action: 'Requests',
      description: `Pending ${colonyQuery.data?.pending_requests ?? 0}, In-progress ${colonyQuery.data?.in_progress_requests ?? 0}`,
      time: 'live',
      status: 'pending',
    },
    {
      id: 2,
      module: 'Guest House',
      action: 'Bookings',
      description: `Occupied ${guestQuery.data?.occupied_rooms ?? 0} / ${guestQuery.data?.total_rooms ?? 0}`,
      time: 'live',
      status: 'info',
    },
    {
      id: 3,
      module: 'Vehicle',
      action: 'Fleet',
      description: `Active trips ${vehicleQuery.data?.active_trips ?? 0}`,
      time: 'live',
      status: 'active',
    },
    {
      id: 4,
      module: 'Visitor',
      action: 'Gate Pass',
      description: `Active visitors ${visitorQuery.data?.active_visitors ?? 0}`,
      time: 'live',
      status: 'info',
    },
    {
      id: 5,
      module: 'Vigilance',
      action: 'Incidents',
      description: `Open incidents ${vigilanceQuery.data?.incidents_open ?? 0}`,
      time: 'live',
      status: 'warning',
    },
    {
      id: 6,
      module: 'Canteen',
      action: 'Orders',
      description: `Today orders ${canteenQuery.data?.today_orders ?? 0}`,
      time: 'live',
      status: 'active',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'warning'
      case 'approved':
        return 'info'
      case 'completed':
        return 'success'
      case 'active':
        return 'primary'
      case 'info':
        return 'info'
      case 'warning':
        return 'warning'
      case 'live':
        return 'success'
      default:
        return 'default'
    }
  }

  const overviewCards = [
    { title: 'Pending Requests', value: colonyQuery.data?.pending_requests || 0, icon: <Warning />, color: 'warning' },
    { title: 'Occupied Rooms', value: guestQuery.data?.occupied_rooms || 0, icon: <People />, color: 'primary' },
    { title: 'Active Trips', value: vehicleQuery.data?.active_trips || 0, icon: <TrendingUp />, color: 'info' },
    { title: 'Incidents Open', value: vigilanceQuery.data?.incidents_open || 0, icon: <Warning />, color: 'warning' },
    { title: 'Visitors Today', value: visitorQuery.data?.visitors_today || 0, icon: <People />, color: 'primary' },
    { title: 'Today Orders', value: canteenQuery.data?.today_orders || 0, icon: <CheckCircle />, color: 'success' },
  ]

  const sections = [
    {
      label: 'Colony',
      cards: [
        { title: 'Total Requests', value: colonyQuery.data?.total_requests || 0, icon: <People />, color: 'primary' },
        { title: 'Pending', value: colonyQuery.data?.pending_requests || 0, icon: <Warning />, color: 'warning' },
        { title: 'In Progress', value: colonyQuery.data?.in_progress_requests || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Completed', value: colonyQuery.data?.completed_requests || 0, icon: <CheckCircle />, color: 'success' },
      ],
    },
    {
      label: 'Guest House',
      cards: [
        { title: 'Total Rooms', value: guestQuery.data?.total_rooms || 0, icon: <People />, color: 'primary' },
        { title: 'Occupied', value: guestQuery.data?.occupied_rooms || 0, icon: <Warning />, color: 'warning' },
        { title: 'Available', value: guestQuery.data?.available_rooms || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Bookings', value: guestQuery.data?.total_bookings || 0, icon: <CheckCircle />, color: 'success' },
      ],
    },
    {
      label: 'Equipment',
      cards: [
        { title: 'Total', value: equipmentQuery.data?.total_equipment || 0, icon: <People />, color: 'primary' },
        { title: 'Available', value: equipmentQuery.data?.available_equipment || 0, icon: <CheckCircle />, color: 'success' },
        { title: 'In Use', value: equipmentQuery.data?.in_use_equipment || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Maintenance', value: equipmentQuery.data?.pending_maintenance || 0, icon: <Warning />, color: 'warning' },
      ],
    },
    {
      label: 'Vigilance',
      cards: [
        { title: 'Active Patrols', value: vigilanceQuery.data?.active_patrols || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Incidents Open', value: vigilanceQuery.data?.incidents_open || 0, icon: <Warning />, color: 'warning' },
        { title: 'SOS Active', value: vigilanceQuery.data?.sos_alerts_active || 0, icon: <People />, color: 'primary' },
        { title: 'Missed Patrols', value: vigilanceQuery.data?.missed_patrols || 0, icon: <Warning />, color: 'warning' },
      ],
    },
    {
      label: 'Vehicles',
      cards: [
        { title: 'Total Fleet', value: vehicleQuery.data?.total_vehicles || 0, icon: <People />, color: 'primary' },
        { title: 'Available', value: vehicleQuery.data?.available_vehicles || 0, icon: <CheckCircle />, color: 'success' },
        { title: 'Active Trips', value: vehicleQuery.data?.active_trips || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Reqs', value: vehicleQuery.data?.pending_requisitions ?? vehicleQuery.data?.pending_approvals ?? 0, icon: <Warning />, color: 'warning' },
      ],
    },
    {
      label: 'Visitors',
      cards: [
        { title: 'Visitors Today', value: visitorQuery.data?.visitors_today || 0, icon: <People />, color: 'primary' },
        { title: 'Onsite', value: visitorQuery.data?.visitors_onsite || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Requests', value: visitorQuery.data?.pending_requests || 0, icon: <Warning />, color: 'warning' },
        { title: 'Approved', value: visitorQuery.data?.approved_requests || 0, icon: <CheckCircle />, color: 'success' },
      ],
    },
    {
      label: 'Canteen',
      cards: [
        { title: 'Active Workers', value: canteenQuery.data?.total_workers || 0, icon: <People />, color: 'primary' },
        { title: 'Today Orders', value: canteenQuery.data?.today_orders || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Orders', value: canteenQuery.data?.pending_orders || 0, icon: <Warning />, color: 'warning' },
        { title: 'Low Stock Items', value: canteenQuery.data?.low_stock_items || 0, icon: <CheckCircle />, color: 'success' },
      ],
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Welcome to Enterprise Plant Operations System
      </Typography>

      <Paper
        sx={{
          p: 2,
          borderRadius: 3,
          boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
          mb: 3,
        }}
      >
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Quick Overview
        </Typography>
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          sx={{
            overflowX: { sm: 'auto' },
            pb: { sm: 1 },
          }}
        >
          {overviewCards.map((card) => (
            <Box key={card.title} sx={{ minWidth: { sm: 220 }, flex: 1 }}>
              <StatCard {...card} />
            </Box>
          ))}
        </Stack>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper
            sx={{
              p: 2,
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              boxShadow: '0 10px 30px rgba(0,0,0,0.06)',
            }}
          >
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                '& .MuiTab-root': { textTransform: 'none', fontWeight: 600 },
              }}
            >
              {sections.map((section) => (
                <Tab key={section.label} label={section.label} />
              ))}
            </Tabs>

            {sections.map((section, index) => (
              <TabPanel key={section.label} value={activeTab} index={index}>
                <Grid container spacing={2}>
                  {section.cards.map((card) => (
                    <Grid item xs={12} sm={6} md={3} key={`${section.label}-${card.title}`}>
                      <StatCard title={card.title} value={card.value} icon={card.icon} color={card.color} />
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>
            ))}
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              borderRadius: 3,
              border: '1px solid',
              borderColor: 'divider',
              boxShadow: '0 10px 30px rgba(0,0,0,0.06)',
              height: '100%',
            }}
          >
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Recent Activities
            </Typography>
            <TableContainer component={Box} sx={{ maxHeight: 360 }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Module</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentActivities
                    .slice(
                      activitiesPage * activitiesRowsPerPage,
                      activitiesPage * activitiesRowsPerPage + activitiesRowsPerPage,
                    )
                    .map((activity) => (
                      <TableRow key={activity.id} hover>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>
                            {activity.module}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {activity.description}
                          </Typography>
                        </TableCell>
                        <TableCell>{activity.action}</TableCell>
                        <TableCell>
                          <Chip
                            label={activity.status}
                            color={getStatusColor(activity.status) as any}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={recentActivities.length}
              page={activitiesPage}
              onPageChange={(_, newPage) => setActivitiesPage(newPage)}
              rowsPerPage={activitiesRowsPerPage}
              onRowsPerPageChange={(event) => {
                setActivitiesRowsPerPage(Number(event.target.value))
                setActivitiesPage(0)
              }}
              rowsPerPageOptions={[5, 10, 25]}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
