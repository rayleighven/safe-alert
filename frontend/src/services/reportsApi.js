import api from '@/services/api'

export function downloadReportBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => window.URL.revokeObjectURL(url), 1000)
}

export async function getHouseholdReport(priority = null) {
  const params = priority ? { priority } : {}
  const response = await api.get('/reports/households/', {
    params,
    responseType: 'blob',
  })
  return response.data
}

export async function getEvacuationCenterReport() {
  const response = await api.get('/reports/evacuation-centers/', {
    responseType: 'blob',
  })
  return response.data
}

export async function getMyHouseholdReport() {
  const response = await api.get('/reports/my-household/', {
    responseType: 'blob',
  })
  return response.data
}
