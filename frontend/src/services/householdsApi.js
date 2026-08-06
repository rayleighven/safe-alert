import api from './api'

export function listHouseholds() {
  return api.get('/households/')
}

export function getHousehold(householdId) {
  return api.get(`/households/${householdId}/`)
}

export function createHousehold(data) {
  return api.post('/households/', data)
}

export function updateHousehold(householdId, data) {
  return api.patch(`/households/${householdId}/`, data)
}

export function archiveHousehold(householdId) {
  return api.delete(`/households/${householdId}/`)
}

export function createMember(householdId, data) {
  return api.post(`/households/${householdId}/members/`, data)
}

export function updateMember(householdId, memberId, data) {
  return api.patch(`/households/${householdId}/members/${memberId}/`, data)
}

export function archiveMember(householdId, memberId) {
  return api.delete(`/households/${householdId}/members/${memberId}/`)
}

export function createVulnerabilityIndicator(householdId, data) {
  return api.post(`/households/${householdId}/vulnerability/`, data)
}

export function updateVulnerabilityIndicator(householdId, indicatorId, data) {
  return api.patch(`/households/${householdId}/vulnerability/${indicatorId}/`, data)
}