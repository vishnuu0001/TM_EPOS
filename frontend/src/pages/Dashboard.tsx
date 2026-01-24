import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
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
  <Card sx={{ height: '100%' }}>
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

export default function Dashboard() {
  const user = useSelector((state: RootState) => state.auth.user)
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
      { queryKey: ['dashboard-colony'], queryFn: colonyService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-guesthouse'], queryFn: guesthouseService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-equipment'], queryFn: equipmentService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-vigilance'], queryFn: vigilanceService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-vehicle'], queryFn: vehicleService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-visitor'], queryFn: visitorService.getDashboardStats, enabled: !!user },
      { queryKey: ['dashboard-canteen'], queryFn: canteenService.getDashboardStats, enabled: !!user },
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

  const renderSection = (title: string, cards: { title: string; value: number; icon: JSX.Element; color: any }[]) => (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom fontWeight={600}>{title}</Typography>
      <Grid container spacing={2}>
        {cards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={`${title}-${card.title}`}>
            <StatCard title={card.title} value={card.value} icon={card.icon} color={card.color} />
          </Grid>
        ))}
      </Grid>
    </Box>
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Welcome to Enterprise Plant Operations System
      </Typography>

      {/* Colony Overview */}
      {renderSection('Colony Maintenance', [
        { title: 'Total Requests', value: colonyQuery.data?.total_requests || 0, icon: <People />, color: 'primary' },
        { title: 'Pending', value: colonyQuery.data?.pending_requests || 0, icon: <Warning />, color: 'warning' },
        { title: 'In Progress', value: colonyQuery.data?.in_progress_requests || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Completed', value: colonyQuery.data?.completed_requests || 0, icon: <CheckCircle />, color: 'success' },
      ])}

      {renderSection('Guest House', [
        { title: 'Total Rooms', value: guestQuery.data?.total_rooms || 0, icon: <People />, color: 'primary' },
        { title: 'Occupied', value: guestQuery.data?.occupied_rooms || 0, icon: <Warning />, color: 'warning' },
        { title: 'Available', value: guestQuery.data?.available_rooms || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Bookings', value: guestQuery.data?.total_bookings || 0, icon: <CheckCircle />, color: 'success' },
      ])}

      {renderSection('Equipment', [
        { title: 'Total', value: equipmentQuery.data?.total_equipment || 0, icon: <People />, color: 'primary' },
        { title: 'Available', value: equipmentQuery.data?.available_equipment || 0, icon: <CheckCircle />, color: 'success' },
        { title: 'In Use', value: equipmentQuery.data?.in_use_equipment || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Maintenance', value: equipmentQuery.data?.pending_maintenance || 0, icon: <Warning />, color: 'warning' },
      ])}

      {renderSection('Vigilance', [
        { title: 'Active Patrols', value: vigilanceQuery.data?.active_patrols || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Incidents Open', value: vigilanceQuery.data?.incidents_open || 0, icon: <Warning />, color: 'warning' },
        { title: 'SOS Active', value: vigilanceQuery.data?.sos_alerts_active || 0, icon: <People />, color: 'primary' },
        { title: 'Missed Patrols', value: vigilanceQuery.data?.missed_patrols || 0, icon: <Warning />, color: 'warning' },
      ])}

      {renderSection('Vehicles', [
        { title: 'Total Fleet', value: vehicleQuery.data?.total_vehicles || 0, icon: <People />, color: 'primary' },
        { title: 'Available', value: vehicleQuery.data?.available_vehicles || 0, icon: <CheckCircle />, color: 'success' },
        { title: 'Active Trips', value: vehicleQuery.data?.active_trips || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Reqs', value: vehicleQuery.data?.pending_requisitions || 0, icon: <Warning />, color: 'warning' },
      ])}

      {renderSection('Visitors', [
          { title: 'Visitors Today', value: visitorQuery.data?.visitors_today || 0, icon: <People />, color: 'primary' },
          { title: 'Onsite', value: visitorQuery.data?.visitors_onsite || 0, icon: <TrendingUp />, color: 'info' },
          { title: 'Pending Requests', value: visitorQuery.data?.pending_requests || 0, icon: <Warning />, color: 'warning' },
          { title: 'Approved', value: visitorQuery.data?.approved_requests || 0, icon: <CheckCircle />, color: 'success' },
      ])}

      {renderSection('Canteen', [
        { title: 'Active Workers', value: canteenQuery.data?.total_workers || 0, icon: <People />, color: 'primary' },
        { title: 'Today Orders', value: canteenQuery.data?.today_orders || 0, icon: <TrendingUp />, color: 'info' },
        { title: 'Pending Orders', value: canteenQuery.data?.pending_orders || 0, icon: <Warning />, color: 'warning' },
        { title: 'Low Stock Items', value: canteenQuery.data?.low_stock_items || 0, icon: <CheckCircle />, color: 'success' },
      ])}

      {/* Recent Activities */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight={600}>
          Recent Activities
        </Typography>
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Module</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentActivities.map((activity) => (
                <TableRow key={activity.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {activity.module}
                    </Typography>
                  </TableCell>
                  <TableCell>{activity.action}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {activity.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {activity.time}
                    </Typography>
                  </TableCell>
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
      </Box>
    </Box>
  )
}
