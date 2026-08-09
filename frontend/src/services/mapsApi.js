import api from './api'

export function listHazardMaps() {
  return api.get('/hazard-maps/')
}

export function getHazardMap(mapId) {
  return api.get(`/hazard-maps/${mapId}/`)
}

export function createHazardMap(data) {
  return api.post('/hazard-maps/', data)
}

export function updateHazardMap(mapId, data) {
  return api.patch(`/hazard-maps/${mapId}/`, data)
}

export function archiveHazardMap(mapId) {
  return api.delete(`/hazard-maps/${mapId}/`)
}