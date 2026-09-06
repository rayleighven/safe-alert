<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />

    <main v-if="!isLoading && center" class="p-6 max-w-3xl mx-auto">
      <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 class="text-2xl font-bold text-slate-800">{{ center.name }}</h1>
          <p class="text-slate-500">{{ center.address }}</p>
        </div>
        <div class="flex items-center gap-3">
          <span :class="statusBadgeClass(center.status)" class="px-3 py-1 rounded-full text-sm font-medium">
            {{ center.status }}
          </span>
          <router-link
            v-if="isSecretary"
            :to="{ name: 'evacuation-center-edit', params: { id: center.center_id } }"
            class="bg-slate-200 hover:bg-slate-300 text-slate-700 text-sm font-medium rounded-lg px-3 py-2"
          >
            Edit
          </router-link>
          <button
            v-if="isSecretary"
            @click="handleArchive"
            class="bg-red-100 hover:bg-red-200 text-red-700 text-sm font-medium rounded-lg px-3 py-2"
          >
            Archive
          </button>
        </div>
      </div>

      <div v-if="center.photo || center.photo_url" class="mb-6 overflow-hidden rounded-xl bg-white shadow-sm">
        <img :src="center.photo || center.photo_url" :alt="`${center.name} photo`" class="h-56 w-full object-cover" />
      </div>

      <div class="bg-white rounded-xl shadow-sm p-6 mb-6 grid grid-cols-2 gap-4 text-sm">
        <div><span class="text-slate-500">Capacity</span><p class="text-slate-800">{{ center.capacity }}</p></div>
        <div><span class="text-slate-500">Current Occupancy</span><p class="text-slate-800">{{ center.current_occupancy }}</p></div>
        <div><span class="text-slate-500">Contact Person</span><p class="text-slate-800">{{ center.contact_person || '—' }}</p></div>
        <div><span class="text-slate-500">Contact Number</span><p class="text-slate-800">{{ center.contact_number || '—' }}</p></div>
      </div>

      <!-- Kagawad quick update: capacity/occupancy/status only -->
      <div v-if="isKagawad" class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Update Capacity / Occupancy / Status</h2>
        <form @submit.prevent="handleKagawadUpdate" class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Capacity</label>
            <input v-model.number="quickForm.capacity" type="number" min="0" required class="w-full rounded-lg border border-slate-300 px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Current Occupancy</label>
            <input v-model.number="quickForm.current_occupancy" type="number" min="0" required class="w-full rounded-lg border border-slate-300 px-3 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
            <select v-model="quickForm.status" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
              <option value="Active">Active</option>
              <option value="Inactive">Inactive</option>
              <option value="Under Maintenance">Under Maintenance</option>
            </select>
          </div>
          <p v-if="quickUpdateMessage" :class="quickUpdateSuccess ? 'text-green-600' : 'text-red-600'" class="col-span-3 text-sm">
            {{ quickUpdateMessage }}
          </p>
          <button
            type="submit"
            :disabled="isSavingQuick"
            class="col-span-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg px-4 py-2 text-sm w-fit"
          >
            {{ isSavingQuick ? 'Saving...' : 'Update' }}
          </button>
        </form>
      </div>

      <!-- Evacuation Records -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-800">Evacuation Records</h2>
          <button v-if="canLogRecords" @click="showRecordForm = !showRecordForm" class="text-sm text-blue-600 hover:text-blue-700">
            {{ showRecordForm ? 'Cancel' : '+ Log Check-in' }}
          </button>
        </div>

        <form v-if="showRecordForm" @submit.prevent="handleAddRecord" class="grid grid-cols-2 gap-3 mb-4 p-4 bg-slate-50 rounded-lg">
          <select v-model="recordForm.disaster" required class="rounded-lg border border-slate-300 px-3 py-2">
            <option value="" disabled>Select Disaster</option>
            <option v-for="d in disasters" :key="d.disaster_id" :value="d.disaster_id">{{ d.name }} ({{ d.status }})</option>
          </select>
          <select v-model="recordForm.household" required class="rounded-lg border border-slate-300 px-3 py-2">
            <option value="" disabled>Select Household</option>
            <option v-for="h in households" :key="h.household_id" :value="h.household_id">
              {{ h.household_number }} - {{ h.head_of_family }}
            </option>
          </select>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="recordForm.has_water" /> Water available</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="recordForm.has_electricity" /> Electricity available</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="recordForm.has_medical" /> Medical support available</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="recordForm.has_food" /> Food available</label>
          <p v-if="recordFormError" class="col-span-2 text-sm text-red-600">{{ recordFormError }}</p>
          <button type="submit" class="col-span-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm">Log Check-in</button>
        </form>

        <table class="w-full text-sm">
          <thead class="text-left text-slate-500">
            <tr>
              <th class="py-2">Household</th>
              <th class="py-2">Disaster</th>
              <th class="py-2">Status</th>
              <th class="py-2">Entered</th>
              <th class="py-2"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in centerRecords" :key="record.record_id" class="border-t border-slate-100">
              <td class="py-2">{{ householdLabel(record.household) }}</td>
              <td class="py-2">{{ disasterLabel(record.disaster) }}</td>
              <td class="py-2">
                <span
                  :class="record.entry_status === 'Checked-in' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-600'"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ record.entry_status }}
                </span>
              </td>
              <td class="py-2">{{ formatDate(record.entered_at) }}</td>
              <td class="py-2">
                <button
                  v-if="canLogRecords && record.entry_status === 'Checked-in'"
                  @click="handleDischarge(record)"
                  class="text-xs text-blue-600 hover:text-blue-700"
                >
                  Mark Departed
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="centerRecords.length === 0" class="text-slate-400 text-sm">No evacuation records for this center yet.</p>
      </div>
    </main>

    <main v-else-if="isLoading" class="p-6 text-slate-500">Loading evacuation center...</main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'
import * as householdsApi from '@/services/householdsApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const center = ref(null)
const isLoading = ref(true)
const allRecords = ref([])
const disasters = ref([])
const households = ref([])
const showRecordForm = ref(false)
const recordFormError = ref('')
const isSavingQuick = ref(false)
const quickUpdateMessage = ref('')
const quickUpdateSuccess = ref(false)

const role = computed(() => authStore.user?.role)
const isSecretary = computed(() => role.value === 'Barangay Secretary')
const isKagawad = computed(() => role.value === 'Barangay Kagawad/Tanod')
const canLogRecords = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod'].includes(role.value))

const quickForm = reactive({ capacity: 0, current_occupancy: 0, status: 'Active' })
const recordForm = reactive({
  disaster: '',
  household: '',
  has_water: false,
  has_electricity: false,
  has_medical: false,
  has_food: false,
})

const centerRecords = computed(() => allRecords.value.filter((r) => r.center === route.params.id))

function statusBadgeClass(status) {
  if (status === 'Active') return 'bg-green-100 text-green-700'
  if (status === 'Under Maintenance') return 'bg-yellow-100 text-yellow-700'
  return 'bg-slate-100 text-slate-600'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

function householdLabel(householdId) {
  const h = households.value.find((h) => h.household_id === householdId)
  return h ? `${h.household_number} - ${h.head_of_family}` : householdId
}

function disasterLabel(disasterId) {
  const d = disasters.value.find((d) => d.disaster_id === disasterId)
  return d ? d.name : disasterId
}

async function loadCenter() {
  isLoading.value = true
  const [centerRes, recordsRes, disastersRes, householdsRes] = await Promise.all([
    evacuationCentersApi.getCenter(route.params.id),
    evacuationCentersApi.listEvacuationRecords(),
    evacuationCentersApi.listDisasters(),
    householdsApi.listHouseholds(),
  ])
  center.value = centerRes.data
  allRecords.value = recordsRes.data
  disasters.value = disastersRes.data
  households.value = householdsRes.data
  Object.assign(quickForm, {
    capacity: center.value.capacity,
    current_occupancy: center.value.current_occupancy,
    status: center.value.status,
  })
  isLoading.value = false
}

onMounted(loadCenter)

async function handleArchive() {
  if (!confirm('Archive this evacuation center?')) return
  await evacuationCentersApi.archiveCenter(route.params.id)
  router.push({ name: 'evacuation-centers' })
}

async function handleKagawadUpdate() {
  isSavingQuick.value = true
  quickUpdateMessage.value = ''
  try {
    await evacuationCentersApi.updateCenter(route.params.id, quickForm)
    quickUpdateSuccess.value = true
    quickUpdateMessage.value = 'Updated successfully.'
    await loadCenter()
  } catch (error) {
    quickUpdateSuccess.value = false
    quickUpdateMessage.value = error.response?.data
      ? Object.values(error.response.data).flat().join(' ')
      : 'Failed to update.'
  } finally {
    isSavingQuick.value = false
  }
}

async function handleAddRecord() {
  recordFormError.value = ''
  try {
    await evacuationCentersApi.createEvacuationRecord({
      ...recordForm,
      center: route.params.id,
      entered_at: new Date().toISOString(),
    })
    showRecordForm.value = false
    Object.assign(recordForm, {
      disaster: '',
      household: '',
      has_water: false,
      has_electricity: false,
      has_medical: false,
      has_food: false,
    })
    await loadCenter()
  } catch (error) {
    recordFormError.value = error.response?.data
      ? Object.values(error.response.data).flat().join(' ')
      : 'Failed to log check-in.'
  }
}

async function handleDischarge(record) {
  await evacuationCentersApi.updateEvacuationRecord(record.record_id, {
    entry_status: 'Departed',
    discharged_at: new Date().toISOString(),
  })
  await loadCenter()
}
</script>