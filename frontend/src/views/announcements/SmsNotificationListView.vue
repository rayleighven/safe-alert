<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-3xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-slate-800">SMS Broadcasts</h1>
        <button
          v-if="isSecretary"
          @click="showStageForm = !showStageForm"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2"
        >
          {{ showStageForm ? 'Cancel' : '+ Stage Broadcast' }}
        </button>
      </div>

      <div class="mb-4 bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm rounded-lg px-4 py-3">
        The SMS gateway may currently be running in dry-run mode (no real credentials configured yet).
        Authorized broadcasts will show as <strong>Simulated</strong> in the delivery log below instead of
        actually sending — check with whoever set up the backend if you're unsure.
      </div>

      <!-- Staging form (Secretary) -->
      <form v-if="showStageForm" @submit.prevent="handleStage" class="bg-white rounded-xl shadow-sm p-6 mb-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Subject</label>
          <input v-model="stageForm.subject" type="text" required class="w-full rounded-lg border border-slate-300 px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Message</label>
          <textarea
            v-model="stageForm.message_body"
            required
            rows="3"
            maxlength="480"
            class="w-full rounded-lg border border-slate-300 px-3 py-2"
          ></textarea>
          <p class="text-xs text-slate-400 mt-1">{{ stageForm.message_body.length }} / 480 characters</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Recipients</label>
          <select v-model="stageForm.recipient_type" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
            <option value="All">All households</option>
            <option value="High Priority">High priority households</option>
            <option value="Medium">Medium priority households</option>
            <option value="Low">Low priority households</option>
            <option value="Custom">Custom selection (chosen at authorization time)</option>
          </select>
        </div>
        <p v-if="stageError" class="text-sm text-red-600">{{ stageError }}</p>
        <button
          type="submit"
          :disabled="isStaging"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg px-4 py-2 text-sm"
        >
          {{ isStaging ? 'Staging...' : 'Stage for Authorization' }}
        </button>
      </form>

      <div v-if="isLoading" class="text-slate-500">Loading broadcasts...</div>
      <div v-else-if="notifications.length === 0" class="text-slate-500">No SMS broadcasts yet.</div>

      <div v-else class="space-y-4">
        <div v-for="n in notifications" :key="n.sms_id" class="bg-white rounded-xl shadow-sm p-5">
          <div class="flex items-start justify-between mb-2 gap-3 flex-wrap">
            <div>
              <h2 class="font-semibold text-slate-800">{{ n.subject }}</h2>
              <p class="text-xs text-slate-400">{{ n.recipient_type }} • Staged {{ formatDate(n.created_at) }}</p>
            </div>
            <span :class="statusBadgeClass(n.status)" class="px-2 py-1 rounded-full text-xs font-medium">{{ n.status }}</span>
          </div>
          <p class="text-slate-600 text-sm mb-3 whitespace-pre-line">{{ n.message_body }}</p>

          <div v-if="n.status !== 'Pending'" class="text-xs text-slate-500 mb-3">
            {{ n.sent_count }} sent / {{ n.failed_count }} failed / {{ n.total_recipients }} total
          </div>

          <!-- Authorize form (Chairperson, only while Pending) -->
          <div v-if="isChairperson && n.status === 'Pending'">
            <div v-if="n.recipient_type === 'Custom'" class="mb-3">
              <label class="block text-sm font-medium text-slate-700 mb-1">Select Households</label>
              <select multiple v-model="customSelections[n.sms_id]" class="w-full rounded-lg border border-slate-300 px-3 py-2 h-32">
                <option v-for="h in households" :key="h.household_id" :value="h.household_id">
                  {{ h.household_number }} - {{ h.head_of_family }}
                </option>
              </select>
            </div>
            <button
              @click="handleAuthorize(n)"
              :disabled="isAuthorizing[n.sms_id]"
              class="bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white rounded-lg px-4 py-2 text-sm"
            >
              {{ isAuthorizing[n.sms_id] ? 'Sending...' : 'Authorize & Send' }}
            </button>
          </div>
          <p v-if="!isChairperson && n.status === 'Pending'" class="text-xs text-slate-400">
            Awaiting authorization from the BDRRMC Chairperson.
          </p>

          <!-- Delivery log -->
          <div v-if="n.logs && n.logs.length > 0" class="mt-3">
            <button @click="toggleLogs(n.sms_id)" class="text-xs text-blue-600 hover:text-blue-700">
              {{ expandedLogs[n.sms_id] ? 'Hide' : 'Show' }} delivery log ({{ n.logs.length }})
            </button>
            <table v-if="expandedLogs[n.sms_id]" class="w-full text-xs mt-2">
              <thead class="text-left text-slate-500">
                <tr>
                  <th class="py-1">Number</th>
                  <th class="py-1">Status</th>
                  <th class="py-1">Response</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in n.logs" :key="log.log_id" class="border-t border-slate-100">
                  <td class="py-1">{{ log.contact_number }}</td>
                  <td class="py-1">
                    <span :class="deliveryBadgeClass(log.delivery_status)" class="px-2 py-0.5 rounded-full text-xs">
                      {{ log.delivery_status }}
                    </span>
                  </td>
                  <td class="py-1 text-slate-500">{{ log.gateway_response }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as announcementsApi from '@/services/announcementsApi'
import * as householdsApi from '@/services/householdsApi'

const authStore = useAuthStore()

const notifications = ref([])
const households = ref([])
const isLoading = ref(true)
const showStageForm = ref(false)
const isStaging = ref(false)
const stageError = ref('')
const customSelections = reactive({})
const isAuthorizing = reactive({})
const expandedLogs = reactive({})

const role = computed(() => authStore.user?.role)
const isSecretary = computed(() => role.value === 'Barangay Secretary')
const isChairperson = computed(() => role.value === 'BDRRMC Chairperson')

const stageForm = reactive({ subject: '', message_body: '', recipient_type: 'All' })

function statusBadgeClass(status) {
  if (status === 'Sent') return 'bg-green-100 text-green-700'
  if (status === 'Partially Sent') return 'bg-yellow-100 text-yellow-700'
  if (status === 'Failed') return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

function deliveryBadgeClass(status) {
  if (status === 'Delivered') return 'bg-green-100 text-green-700'
  if (status === 'Simulated') return 'bg-blue-100 text-blue-700'
  if (status === 'Failed') return 'bg-red-100 text-red-700'
  return 'bg-slate-100 text-slate-600'
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}

function toggleLogs(smsId) {
  expandedLogs[smsId] = !expandedLogs[smsId]
}

async function loadData() {
  isLoading.value = true
  const [notificationsRes, householdsRes] = await Promise.all([
    announcementsApi.listSmsNotifications(),
    householdsApi.listHouseholds(),
  ])
  notifications.value = notificationsRes.data
  households.value = householdsRes.data
  isLoading.value = false
}

onMounted(loadData)

async function handleStage() {
  isStaging.value = true
  stageError.value = ''
  try {
    await announcementsApi.stageSmsNotification(stageForm)
    Object.assign(stageForm, { subject: '', message_body: '', recipient_type: 'All' })
    showStageForm.value = false
    await loadData()
  } catch (error) {
    stageError.value = error.response?.data
      ? Object.values(error.response.data).flat().join(' ')
      : 'Failed to stage broadcast.'
  } finally {
    isStaging.value = false
  }
}

async function handleAuthorize(notification) {
  if (!confirm(`Authorize and send this broadcast to recipients matching "${notification.recipient_type}"?`)) return
  isAuthorizing[notification.sms_id] = true
  try {
    const payload = {}
    if (notification.recipient_type === 'Custom') {
      payload.household_ids = customSelections[notification.sms_id] || []
    }
    await announcementsApi.authorizeSmsNotification(notification.sms_id, payload)
    await loadData()
  } catch (error) {
    alert(error.response?.data ? Object.values(error.response.data).flat().join(' ') : 'Failed to authorize broadcast.')
  } finally {
    isAuthorizing[notification.sms_id] = false
  }
}
</script>