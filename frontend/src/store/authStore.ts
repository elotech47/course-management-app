import { create } from 'zustand'
import api from '@/lib/api'

interface User {
  id: number
  email: string
  full_name: string
  role: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (email: string, password: string) => {
    // API expects application/x-www-form-urlencoded (OAuth2PasswordRequestForm)
    // Using URLSearchParams avoids CORS preflight (simple content-type)
    const body = new URLSearchParams()
    body.set('username', email)
    body.set('password', password)

    const response = await api.post('/api/auth/login', body, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    const { access_token } = response.data
    localStorage.setItem('token', access_token)

    // Get user info
    const userResponse = await api.get('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    })

    set({
      token: access_token,
      user: userResponse.data,
      isAuthenticated: true,
    })
  },

  register: async (email: string, password: string, fullName: string) => {
    await api.post('/api/auth/register', {
      email,
      password,
      full_name: fullName,
      role: 'ta',
    })
  },

  logout: () => {
    localStorage.removeItem('token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    })
  },

  checkAuth: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      set({ isAuthenticated: false, user: null, token: null })
      return
    }

    try {
      const response = await api.get('/api/auth/me')
      set({
        user: response.data,
        isAuthenticated: true,
        token,
      })
    } catch (error) {
      localStorage.removeItem('token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
      })
    }
  },
}))
