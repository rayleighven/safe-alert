import { defineStore } from 'pinia'
import * as authApi from '@/services/authApi'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('safe_alert_access_token') || null,
    refreshTokenValue: localStorage.getItem('safe_alert_refresh_token') || null,
    user: JSON.parse(localStorage.getItem('safe_alert_user') || 'null'),
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    role: (state) => (state.user ? state.user.role : null),
  },

  actions: {
    async login(username, password) {
      const response = await authApi.login(username, password)
      this.setSession(response.data.access, response.data.refresh, response.data.user)
      return response.data.user
    },

    setSession(accessToken, refreshTokenValue, user) {
      this.accessToken = accessToken
      this.refreshTokenValue = refreshTokenValue
      this.user = user
      localStorage.setItem('safe_alert_access_token', accessToken)
      localStorage.setItem('safe_alert_refresh_token', refreshTokenValue)
      localStorage.setItem('safe_alert_user', JSON.stringify(user))
    },

    async refreshAccessToken() {
      if (!this.refreshTokenValue) {
        throw new Error('No refresh token available.')
      }
      const response = await authApi.refreshToken(this.refreshTokenValue)
      this.accessToken = response.data.access
      localStorage.setItem('safe_alert_access_token', response.data.access)
      return response.data.access
    },

    async fetchProfile() {
      const response = await authApi.getProfile()
      this.user = { ...this.user, ...response.data }
      localStorage.setItem('safe_alert_user', JSON.stringify(this.user))
      return response.data
    },

    async logout() {
      try {
        if (this.refreshTokenValue) {
          await authApi.logout(this.refreshTokenValue)
        }
      } catch (error) {
        // Even if the blacklist call fails, clear the local session anyway.
        console.error('Logout request failed:', error)
      } finally {
        this.clearSession()
      }
    },

    clearSession() {
      this.accessToken = null
      this.refreshTokenValue = null
      this.user = null
      localStorage.removeItem('safe_alert_access_token')
      localStorage.removeItem('safe_alert_refresh_token')
      localStorage.removeItem('safe_alert_user')
    },
  },
})