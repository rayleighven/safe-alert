<template>
  <div class="space-y-6 pb-6">
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Archives</span>
      </nav>
      <div>
        <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Archives</h1>
        <p class="mt-1 text-xs font-medium text-slate-500 sm:text-sm">View and restore archived records.</p>
      </div>
    </header>

    <div class="flex flex-wrap gap-2" role="tablist" aria-label="Archived modules">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        role="tab"
        :aria-selected="activeTab === tab.key"
        :class="activeTab === tab.key ? 'bg-blue-600 text-white font-semibold rounded-xl' : 'text-slate-600 hover:bg-slate-100 rounded-xl'"
        class="px-4 py-2 text-xs transition-colors"
        @click="activateTab(tab.key)"
      >{{ tab.label }}</button>
    </div>

    <div v-if="successMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700" role="status">
      {{ successMessage }}
    </div>
    <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">
      {{ errorMessage }}
    </div>

    <div v-if="loading[activeTab]" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading archived records...</p>
    </div>

    <div v-else-if="records[activeTab].length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No archived records</h3>
      <p class="mt-1 text-xs text-slate-500">There are no archived {{ currentTabLabel.toLowerCase() }} to display.</p>
    </div>

    <div v-else class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-card">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs sm:text-sm">
          <thead class="border-b border-slate-200/70 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
            <tr>
              <th v-for="column in currentColumns" :key="column.key" scope="col" class="px-4 py-3">{{ column.label }}</th>
              <th scope="col" class="px-4 py-3 text-right">Restore</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="record in records[activeTab]" :key="recordId(record)" class="hover:bg-blue-50/40">
              <td v-for="column in currentColumns" :key="column.key" class="px-4 py-3.5 font-medium text-slate-700">
                {{ formatValue(record, column.key) }}
              </td>
              <td class="px-4 py-3.5 text-right">
                <button
                  type="button"
                  class="inline-flex items-center gap-1.5 rounded-xl bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-60"
                  :disabled="restoringId === recordId(record)"
                  @click="restoreRecord(record)"
                >{{ restoringId === recordId(record) ? 'Restoring...' : 'Restore' }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as householdsApi from '@/services/householdsApi'
import * as centersApi from '@/services/evacuationCentersApi'
import * as announcementsApi from '@/services/announcementsApi'
import * as mapsApi from '@/services/mapsApi'

const router = useRouter()
const authStore = useAuthStore()
const tabs = [
  { key: 'households', label: 'Households' },
  { key: 'centers', label: 'Evacuation Centers' },
  { key: 'announcements', label: 'Announcements' },
  { key: 'maps', label: 'Hazard Maps' },
]
const columns = {
  households: [
    { key: 'household_number', label: 'Household #' }, { key: 'head_of_family', label: 'Head of Family' },
    { key: 'purok', label: 'Purok' }, { key: 'archived_at', label: 'Archived On' },
  ],
  centers: [
    { key: 'name', label: 'Name' }, { key: 'barangay', label: 'Barangay' },
    { key: 'status', label: 'Status' }, { key: 'archived_at', label: 'Archived On' },
  ],
  announcements: [
    { key: 'title', label: 'Title' }, { key: 'categories', label: 'Category' },
    { key: 'posted_by', label: 'Posted By' }, { key: 'archived_at', label: 'Archived On' },
  ],
  maps: [
    { key: 'map_title', label: 'Title' }, { key: 'hazard_type', label: 'Hazard Type' },
    { key: 'archived_at', label: 'Archived On' },
  ],
}
const listFunctions = {
  households: householdsApi.listArchivedHouseholds,
  centers: centersApi.listArchivedCenters,
  announcements: announcementsApi.listArchivedAnnouncements,
  maps: mapsApi.listArchivedHazardMaps,
}
const restoreFunctions = {
  households: (record) => householdsApi.restoreHousehold(record.household_id),
  centers: (record) => centersApi.restoreCenter(record.center_id),
  announcements: (record) => announcementsApi.restoreAnnouncement(record.announcement_id),
  maps: (record) => mapsApi.restoreHazardMap(record.map_id),
}
const idFields = { households: 'household_id', centers: 'center_id', announcements: 'announcement_id', maps: 'map_id' }
const activeTab = ref('households')
const records = reactive({ households: [], centers: [], announcements: [], maps: [] })
const loaded = reactive({ households: false, centers: false, announcements: false, maps: false })
const loading = reactive({ households: false, centers: false, announcements: false, maps: false })
const restoringId = ref(null)
const successMessage = ref('')
const errorMessage = ref('')
let messageTimer
const currentColumns = computed(() => columns[activeTab.value])
const currentTabLabel = computed(() => tabs.find((tab) => tab.key === activeTab.value)?.label || '')

function recordId(record) {
  return record[idFields[activeTab.value]]
}

function formatValue(record, key) {
  if (key === 'archived_at') {
    return record.archived_at ? new Date(record.archived_at).toLocaleDateString() : '—'
  }
  if (key === 'categories') {
    return record.categories?.map((category) => category.category).join(', ') || '—'
  }
  const value = record[key]
  return value === null || value === undefined || value === '' ? '—' : value
}

async function activateTab(key) {
  activeTab.value = key
  if (loaded[key]) return
  loading[key] = true
  errorMessage.value = ''
  try {
    const response = await listFunctions[key]()
    records[key] = response.data
    loaded[key] = true
  } catch {
    errorMessage.value = 'Unable to load archived records. Please try again.'
  } finally {
    loading[key] = false
  }
}

async function restoreRecord(record) {
  if (!window.confirm('Restore this record?')) return
  const key = activeTab.value
  const id = recordId(record)
  restoringId.value = id
  errorMessage.value = ''
  records[key] = records[key].filter((item) => item[idFields[key]] !== id)
  try {
    await restoreFunctions[key](record)
    successMessage.value = 'Record restored successfully.'
    clearTimeout(messageTimer)
    messageTimer = setTimeout(() => { successMessage.value = '' }, 3000)
  } catch {
    records[key] = [record, ...records[key]]
    errorMessage.value = 'Unable to restore this record. Please try again.'
  } finally {
    restoringId.value = null
  }
}

onMounted(() => {
  if (authStore.user?.role !== 'Barangay Secretary') {
    router.replace({ name: 'dashboard' })
    return
  }
  activateTab('households')
})
</script>
