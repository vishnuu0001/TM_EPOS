# Authentication Redirect Issue - Root Cause Analysis & Fix

## Problem Summary
After successful login, users were immediately redirected back to the login page when accessing ANY menu (Dashboard, Guest House, Vehicle, Visitor).

## Root Cause
**Timing Issue with React Query API Calls**

All menu components were making API calls immediately on component mount using React Query, BEFORE the user was fully authenticated in Redux state:

```typescript
// PROBLEM: Query fires immediately on mount
const { data: stats } = useQuery({
  queryKey: ['guesthouseStats'],
  queryFn: guesthouseService.getDashboardStats,
  retry: 1,
})
```

### What Was Happening:
1. ✅ User logs in successfully
2. ✅ Token and user saved to localStorage
3. ✅ Navigation to /dashboard (or other menu) executes
4. ❌ **Component mounts and React Query fires API calls**
5. ❌ **API calls happen before Redux state fully initializes from localStorage**
6. ❌ **Axios interceptor reads localStorage but gets timing issue**
7. ❌ **API returns 401 Unauthorized**
8. ❌ **Axios interceptor clears localStorage and redirects to /login**

### Why Some Menus Worked:
- ✅ **Colony, Equipment, Vigilance, Canteen** - No API calls on mount
- ❌ **Dashboard, Guest House, Vehicle, Visitor** - Multiple API calls on mount

## The Fix
Added `enabled: !!user` to ALL React Query hooks to prevent API calls until user is authenticated:

```typescript
// SOLUTION: Only query when user exists
const user = useSelector((state: RootState) => state.auth.user)

const { data: stats } = useQuery({
  queryKey: ['guesthouseStats'],
  queryFn: guesthouseService.getDashboardStats,
  enabled: !!user,  // ← KEY FIX: Wait for user to be authenticated
  retry: 1,
})
```

## Files Fixed

### 1. Dashboard.tsx
- Added user selector
- Changed `enabled: false` → `enabled: !!user`
- Now waits for authentication before fetching stats

### 2. GuestHouse.tsx
Fixed 3 queries:
- `guesthouseStats` query - Added `enabled: !!user`
- `rooms` query - Added `enabled: !!user`
- `bookings` query - Added `enabled: !!user`

### 3. Vehicle.tsx
Fixed 3 queries:
- `vehicleStats` query - Added `enabled: !!user`
- `vehicles` query - Added `enabled: !!user`
- `requisitions` query - Added `enabled: !!user`

### 4. Visitor.tsx
Fixed 3 queries:
- `visitorStats` query - Added `enabled: !!user`
- `visitorRequests` query - Added `enabled: !!user`
- `activeVisitors` query - Added `enabled: !!user`

### 5. api.ts (Enhanced Logging)
Added comprehensive logging to help debug future issues:
- Request interceptor logs every API call with token status
- 401 handler logs detailed context before redirecting

## Testing Checklist

After this fix, verify:
- [x] Login succeeds and stays on dashboard
- [x] Dashboard loads without redirecting
- [x] Guest House menu accessible
- [x] Vehicle menu accessible
- [x] Visitor menu accessible
- [x] Colony menu accessible (was already working)
- [x] Equipment menu accessible (was already working)
- [x] Vigilance menu accessible (was already working)
- [x] Canteen menu accessible (was already working)
- [x] No 401 errors in console after login
- [x] Token persists across page refreshes
- [x] Logout works correctly

## Key Learnings

1. **React Query Timing**: `useQuery` fires immediately on mount, can race with Redux initialization
2. **Always Use enabled**: For authenticated queries, always add `enabled: !!user` or similar auth check
3. **Axios Interceptor Impact**: 401 errors trigger hard redirects, clearing all auth state
4. **Component Mount Order**: Redux may not be fully hydrated from localStorage when components first mount

## Pattern for Future Components

When creating new protected pages with API calls:

```typescript
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { useQuery } from '@tanstack/react-query'

export default function MyComponent() {
  // Always get user from Redux
  const user = useSelector((state: RootState) => state.auth.user)
  
  // Always add enabled check
  const { data } = useQuery({
    queryKey: ['myData'],
    queryFn: myService.getData,
    enabled: !!user,  // ← CRITICAL: Don't fire until authenticated
  })
  
  return (/* component JSX */)
}
```

## Previous Debugging Work

During investigation, we also fixed:
- ✅ User interface mismatch (`full_name` vs `first_name`/`last_name`)
- ✅ User object persistence in localStorage
- ✅ Header component field access
- ✅ Form submission preventing page reload
- ✅ Comprehensive logging throughout auth flow
- ✅ API Gateway lifespan deprecation warning

All these fixes remain in place and contribute to overall system stability.

## Conclusion

The root cause was a **race condition** between React Query API calls and Redux state initialization from localStorage. By adding `enabled: !!user` to all queries, we ensure API calls only fire after authentication is confirmed, preventing the 401 → redirect loop.
