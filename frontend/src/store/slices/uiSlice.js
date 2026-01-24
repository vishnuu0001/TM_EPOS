import { createSlice } from '@reduxjs/toolkit'

const initialState = {
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
    setCurrentModule: (state, action) => {
      state.currentModule = action.payload
    },
    setTheme: (state, action) => {
      state.theme = action.payload
    },
  },
})

export const { toggleSidebar, setCurrentModule, setTheme } = uiSlice.actions
export default uiSlice.reducer
