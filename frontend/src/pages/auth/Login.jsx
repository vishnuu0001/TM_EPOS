import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import {
  Box,
  TextField,
  Button,
  Typography,
  InputAdornment,
  IconButton,
  CircularProgress,
  Paper,
  Stack,
  Divider,
} from '@mui/material'
import {
  Visibility,
  VisibilityOff,
  Login as LoginIcon,
} from '@mui/icons-material'
import { toast } from 'react-toastify'
import { authService } from '../../services/authService'
import { setCredentials } from '../../store/slices/authSlice'

export default function Login() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleFillDemo = () => {
    setUsername('admin@epos.com')
    setPassword('Admin@123')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!username || !password) {
      toast.error('Please enter username and password')
      return
    }

    setLoading(true)

    try {
      const response = await authService.login({ username, password })
      dispatch(
        setCredentials({
          user: response.user,
          token: response.access_token,
        })
      )

      toast.success('Login successful!')

      // Small delay to ensure state is updated before navigating
      setTimeout(() => navigate('/dashboard', { replace: true }), 150)
    } catch (error) {
      toast.error(error?.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background:
          'radial-gradient(circle at 20% 20%, rgba(88,141,255,0.12), transparent 35%), radial-gradient(circle at 85% 15%, rgba(6,214,160,0.12), transparent 30%), linear-gradient(135deg, #040914 0%, #0a1230 45%, #041633 100%)',
        px: { xs: 2, md: 4 },
        py: { xs: 6, md: 10 },
      }}
    >
      <Paper
        elevation={0}
        sx={{
          width: '100%',
          maxWidth: { xs: 560, md: '50vw' },
          borderRadius: 16,
          overflow: 'hidden',
          backdropFilter: 'blur(18px)',
          boxShadow: '0 26px 90px rgba(0,0,0,0.32)',
          border: '1px solid rgba(255,255,255,0.05)',
          p: { xs: 3.5, md: 4.5 },
        }}
      >
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" fontWeight={800} gutterBottom>
              Sign in
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Enter your credentials to continue.
            </Typography>
          </Box>
          <Button size="small" variant="text" onClick={handleFillDemo} sx={{ textTransform: 'none' }}>
            Fill demo
          </Button>
        </Box>

        <Paper
          variant="outlined"
          sx={{
            p: { xs: 3, md: 3.5 },
            borderRadius: 3,
            boxShadow: '0 16px 40px rgba(15,30,70,0.08)',
          }}
        >
          <TextField
            fullWidth
            label="Username or Email"
            variant="outlined"
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSubmit(e)
              }
            }}
          />

          <TextField
            fullWidth
            label="Password"
            type={showPassword ? 'text' : 'password'}
            variant="outlined"
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSubmit(e)
              }
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} alignItems="center" sx={{ mt: 2 }}>
            <Button
              type="button"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              onClick={handleSubmit}
              startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
              sx={{ py: 1.25, textTransform: 'none', fontWeight: 700 }}
            >
              {loading ? 'Signing you in...' : 'Login'}
            </Button>
          </Stack>

          <Divider sx={{ my: 3 }} />

          <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
            <Typography variant="caption" color="text.secondary">
              Demo:
            </Typography>
            <Typography variant="caption">admin@epos.com / Admin@123</Typography>
          </Stack>
        </Paper>
      </Paper>
    </Box>
  )
}
