import api from './api'

export function listBarangays() {
  return api.get('/barangays/')
}
