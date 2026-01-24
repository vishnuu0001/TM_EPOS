import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { RootState } from './store'

// Layout
import MainLayout from './components/layout/MainLayout'
import AuthLayout from './components/layout/AuthLayout'

// Pages
import Login from './pages/auth/Login'
import Dashboard from './pages/Dashboard'
import ColonyMaintenance from './pages/colony/ColonyMaintenance'
import GuestHouse from './pages/guesthouse/GuestHouse'
import Equipment from './pages/equipment/Equipment'
import Vigilance from './pages/vigilance/Vigilance'
import Vehicle from './pages/vehicle/Vehicle'
import Visitor from './pages/visitor/Visitor'
import Canteen from './pages/canteen/Canteen'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const isAuthenticated = useSelector(
    (state: RootState) => state.auth.isAuthenticated
  )
  const token = useSelector((state: RootState) => state.auth.token)
  const user = useSelector((state: RootState) => state.auth.user)
  
  console.log('ProtectedRoute check:', { 
    isAuthenticated, 
    hasToken: !!token,
    hasUser: !!user,
    tokenInStorage: !!localStorage.getItem('token'),
    userInStorage: !!localStorage.getItem('user')
  })

  if (!isAuthenticated) {
    console.log('Not authenticated, redirecting to /login')
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route path="/login" element={<Login />} />
      </Route>

      {/* Protected Routes */}
      <Route
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/colony/*" element={<ColonyMaintenance />} />
        <Route path="/guesthouse/*" element={<GuestHouse />} />
        <Route path="/equipment/*" element={<Equipment />} />
        <Route path="/vigilance/*" element={<Vigilance />} />
        <Route path="/vehicle/*" element={<Vehicle />} />
        <Route path="/visitor/*" element={<Visitor />} />
        <Route path="/canteen/*" element={<Canteen />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
