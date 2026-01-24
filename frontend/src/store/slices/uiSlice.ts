import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  sidebarOpen: boolean
  currentModule: string
  theme: 'light' | 'dark'
}

const initialState: UIState = {
  sidebarOpen: true,
  currentModule: 'dashboard',
  theme: 'light',
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setCurrentModule: (state, action: PayloadAction<string>) => {
      state.currentModule = action.payload
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload
    },
  },
})

export const { toggleSidebar, setCurrentModule, setTheme } = uiSlice.actions
export default uiSlice.reducer
