import api from './api'

export function listBarangays() {
  return api.get('/barangays/')
}

export function getBarangay(barangayId) {
  return api.get(`/barangays/${barangayId}/`)
}
