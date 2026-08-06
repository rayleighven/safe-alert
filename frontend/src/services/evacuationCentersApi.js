import api from './api'

export function listCenters() {
  return api.get('/evacuation-centers/')
}

export function getCenter(centerId) {
  return api.get(`/evacuation-centers/${centerId}/`)
}

export function createCenter(data) {
  return api.post('/evacuation-centers/', data)
}

export function updateCenter(centerId, data) {
  return api.patch(`/evacuation-centers/${centerId}/`, data)
}

export function archiveCenter(centerId) {
  return api.delete(`/evacuation-centers/${centerId}/`)
}

export function listDisasters() {
  return api.get('/disasters/')
}

export function createDisaster(data) {
  return api.post('/disasters/', data)
}

export function updateDisaster(disasterId, data) {
  return api.patch(`/disasters/${disasterId}/`, data)
}

export function listEvacuationRecords() {
  return api.get('/evacuation-records/')
}

export function createEvacuationRecord(data) {
  return api.post('/evacuation-records/', data)
}

export function updateEvacuationRecord(recordId, data) {
  return api.patch(`/evacuation-records/${recordId}/`, data)
}