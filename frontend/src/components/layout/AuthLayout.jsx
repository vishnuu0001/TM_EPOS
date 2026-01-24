import { Outlet, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { Box, Container, Paper } from '@mui/material'

export default function AuthLayout() {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated)

  console.log('AuthLayout check - isAuthenticated:', isAuthenticated)

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    console.log('Already authenticated, redirecting to /dashboard')
    return <Navigate to="/dashboard" replace />
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={6}
          sx={{
            p: 4,
            borderRadius: 2,
          }}
        >
          <Outlet />
        </Paper>
      </Container>
    </Box>
  )
}
