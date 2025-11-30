import { create } from 'zustand'
import { supabase } from '../lib/supabase'

interface User {
  id: string
  email: string
  role: 'admin' | 'user'
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      const user: User = {
        id: data.user.id,
        email: data.user.email!,
        role: 'admin', // Por enquanto todos são admin, depois podemos adicionar lógica de roles
      }

      set({ user, isAuthenticated: true })
    } catch (error) {
      console.error('Erro ao fazer login:', error)
      throw error
    }
  },

  logout: async () => {
    try {
      const { error } = await supabase.auth.signOut()
      if (error) throw error
      
      set({ user: null, isAuthenticated: false })
    } catch (error) {
      console.error('Erro ao fazer logout:', error)
      throw error
    }
  },

  checkAuth: async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (session) {
        const user: User = {
          id: session.user.id,
          email: session.user.email!,
          role: 'admin',
        }
        set({ user, isAuthenticated: true, isLoading: false })
      } else {
        set({ user: null, isAuthenticated: false, isLoading: false })
      }
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error)
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },
}))