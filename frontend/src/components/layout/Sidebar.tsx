import { useNavigate, useLocation } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Box,
  Typography,
  Divider,
} from '@mui/material'
import {
  Dashboard as DashboardIcon,
  Home as HomeIcon,
  Hotel as HotelIcon,
  Construction as ConstructionIcon,
  Security as SecurityIcon,
  DirectionsCar as CarIcon,
  Badge as BadgeIcon,
  Restaurant as RestaurantIcon,
} from '@mui/icons-material'

interface SidebarProps {
  drawerWidth: number
  open: boolean
  onToggle: () => void
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Colony Maintenance', icon: <HomeIcon />, path: '/colony' },
  { text: 'Guest House', icon: <HotelIcon />, path: '/guesthouse' },
  { text: 'Equipment', icon: <ConstructionIcon />, path: '/equipment' },
  { text: 'Night Vigilance', icon: <SecurityIcon />, path: '/vigilance' },
  { text: 'Vehicle', icon: <CarIcon />, path: '/vehicle' },
  { text: 'Visitor Pass', icon: <BadgeIcon />, path: '/visitor' },
  { text: 'Canteen', icon: <RestaurantIcon />, path: '/canteen' },
]

export default function Sidebar({ drawerWidth, open, onToggle }: SidebarProps) {
  const navigate = useNavigate()
  const location = useLocation()

  console.log('[SIDEBAR] Rendering, path:', location.pathname)

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      onClose={onToggle}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1.2rem',
            }}
          >
            eP
          </Box>
          <Typography variant="h6" noWrap>
            ePOS
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ pt: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path)
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={isActive}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  '&.Mui-selected': {
                    bgcolor: 'primary.light',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.main',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'white' : 'inherit',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          )
        })}
      </List>
    </Drawer>
  )
}
