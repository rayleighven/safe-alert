import api from './api'

export function listAnnouncements() {
  return api.get('/announcements/')
}

export function getAnnouncement(announcementId) {
  return api.get(`/announcements/${announcementId}/`)
}

export function createAnnouncement(data) {
  return api.post('/announcements/', data)
}

export function updateAnnouncement(announcementId, data) {
  return api.patch(`/announcements/${announcementId}/`, data)
}

export function archiveAnnouncement(announcementId) {
  return api.delete(`/announcements/${announcementId}/`)
}

export function listSmsNotifications() {
  return api.get('/sms-notifications/')
}

export function stageSmsNotification(data) {
  return api.post('/sms-notifications/', data)
}

export function authorizeSmsNotification(smsId, data) {
  return api.post(`/sms-notifications/${smsId}/authorize/`, data)
}