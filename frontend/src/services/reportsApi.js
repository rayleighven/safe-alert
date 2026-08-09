import api from '@/services/api'

function downloadBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function downloadHouseholdReport(priority = null) {
  const params = priority ? { priority } : {}
  const response = await api.get('/reports/households/', {
    params,
    responseType: 'blob',
  })
  downloadBlob(response.data, 'household_report.pdf')
}

export async function downloadEvacuationCenterReport() {
  const response = await api.get('/reports/evacuation-centers/', {
    responseType: 'blob',
  })
  downloadBlob(response.data, 'evacuation_center_report.pdf')
}

export async function downloadMyHouseholdReport() {
  const response = await api.get('/reports/my-household/', {
    responseType: 'blob',
  })
  downloadBlob(response.data, 'my_household_report.pdf')
}