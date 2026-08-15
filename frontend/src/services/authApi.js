import api from './api'

export function login(username, password, accessArea = null) {
  return api.post('/auth/login/', { username, password, ...(accessArea ? { access_area: accessArea } : {}) })
}

export function refreshToken(refresh) {
  return api.post('/auth/login/refresh/', { refresh })
}

export function logout(refresh) {
  return api.post('/auth/logout/', { refresh })
}

export function getProfile() {
  return api.get('/auth/profile/')
}

export function updateProfile(data) {
  return api.patch('/auth/profile/', data)
}

export function changePassword(currentPassword, newPassword) {
  return api.post('/auth/profile/change-password/', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}

export function createResidentAccount(data) {
  return api.post('/auth/users/create-resident/', data)
}

export function listBarangayAccounts() {
  return api.get('/auth/users/')
}

export function createBarangayAccount(data) {
  return api.post('/auth/users/', data)
}

export function updateBarangayAccount(userId, data) {
  return api.patch(`/auth/users/${userId}/`, data)
}
