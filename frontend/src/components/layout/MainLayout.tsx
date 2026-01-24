import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import Sidebar from './Sidebar'
import Header from './Header'

const DRAWER_WIDTH = 280

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  useEffect(() => {
    console.log('[MAINLAYOUT] Component mounted')
    return () => console.log('[MAINLAYOUT] Component unmounted')
  }, [])

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen)
  }

  console.log('[MAINLAYOUT] Rendering...')

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header
        drawerWidth={DRAWER_WIDTH}
        sidebarOpen={sidebarOpen}
        onToggle={handleDrawerToggle}
      />
      <Sidebar
        drawerWidth={DRAWER_WIDTH}
        open={sidebarOpen}
        onToggle={handleDrawerToggle}
      />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: sidebarOpen ? 0 : `-${DRAWER_WIDTH}px`,
          transition: (theme) =>
            theme.transitions.create(['margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
