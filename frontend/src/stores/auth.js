import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false
  }),

  getters: {
    hasRole: (state) => (role) => {
      return state.user?.role === role
    },
    canManageOrders: (state) => {
      return state.user?.role === 'logistics' && state.user?.tenant?.type === 'LOGISTICS'
    }
  },

  actions: {
    async login(username, password) {
      try {
        const response = await api.post('/api/auth/login', {
          username,
          password
        })
        
        const { access_token, refresh_token, user } = response.data
        
        this.token = access_token
        this.refreshToken = refresh_token
        this.user = user
        this.isAuthenticated = true
        
        // 存储到localStorage
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)
        localStorage.setItem('user', JSON.stringify(user))
        
        return response.data
      } catch (error) {
        this.logout()
        throw error
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isAuthenticated = false
      
      // 清除localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    },

    loadFromStorage() {
      const token = localStorage.getItem('token')
      const refreshToken = localStorage.getItem('refreshToken')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        try {
          this.token = token
          this.refreshToken = refreshToken
          this.user = JSON.parse(userStr)
          this.isAuthenticated = true
        } catch (error) {
          console.error('Failed to load user from storage:', error)
          this.logout()
        }
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) {
        this.logout()
        return false
      }
      
      try {
        const response = await api.post('/api/auth/refresh', {}, {
          headers: { Authorization: `Bearer ${this.refreshToken}` }
        })
        
        this.token = response.data.access_token
        localStorage.setItem('token', response.data.access_token)
        
        return true
      } catch (error) {
        this.logout()
        return false
      }
    }
  }
})
