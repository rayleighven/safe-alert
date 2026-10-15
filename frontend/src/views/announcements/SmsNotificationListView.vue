<template>
  <div class="space-y-6 pb-6 max-w-4xl">
    <!-- Breadcrumb & Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">SMS Broadcasts</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">SMS Broadcasts</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Emergency SMS staging, Chairperson authorization queue, and carrier delivery logs.
          </p>
        </div>
        <button
          v-if="isSecretary"
          type="button"
          class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          @click="showStageForm = !showStageForm"
        >
          <svg v-if="!showStageForm" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>{{ showStageForm ? 'Cancel Staging' : 'Stage Broadcast' }}</span>
        </button>
      </div>
    </header>

    <!-- Dry Run / Simulation Mode Notice -->
    <div class="flex items-start gap-3 rounded-2xl border border-amber-200/80 bg-amber-50/70 p-4 text-xs sm:text-sm text-amber-900 shadow-xs">
      <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-800">
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
        </svg>
      </span>
      <div class="leading-relaxed">
        <strong class="font-bold">Gateway Notice:</strong> The SMS gateway may operate in dry-run simulation mode without live carrier credentials. Authorized broadcasts will show as <strong>Simulated</strong> in the delivery audit log below without charging airtime.
      </div>
    </div>

    <!-- Staging Form (Secretary) -->
    <form
      v-if="showStageForm"
      class="space-y-4 rounded-2xl border border-blue-200/90 bg-white p-5 sm:p-6 shadow-card"
      @submit.prevent="handleStage"
    >
      <div class="border-b border-slate-100 pb-3">
        <h2 class="text-base font-bold text-slate-900">Stage Emergency Broadcast</h2>
        <p class="mt-0.5 text-xs text-slate-500">Staged messages require BDRRMC Chairperson authorization before transmission.</p>
      </div>

      <div>
        <label for="sms-subject" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">Subject</label>
        <input
          id="sms-subject"
          v-model="stageForm.subject"
          type="text"
          required
          placeholder="e.g. PAGASA Tropical Cyclone Warning"
          class="w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2 text-xs sm:text-sm font-medium text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <div>
        <div class="flex items-center justify-between mb-1">
          <label for="sms-body" class="block text-xs font-bold uppercase tracking-wider text-slate-700">Message Body</label>
          <span class="text-[11px] font-semibold text-slate-400 tabular-nums">{{ stageForm.message_body.length }} / 480</span>
        </div>
        <textarea
          id="sms-body"
          v-model="stageForm.message_body"
          required
          rows="3"
          maxlength="480"
          placeholder="Enter clear, concise emergency instructions for residents..."
          class="w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2 text-xs sm:text-sm font-medium text-slate-800 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <div>
        <label for="sms-recipients" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">Target Recipients</label>
        <select
          id="sms-recipients"
          v-model="stageForm.recipient_type"
          required
          class="w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-700 focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
        >
          <option value="All">All households in Barangay</option>
          <option value="High Priority">High priority households only</option>
          <option value="Medium">Medium priority households</option>
          <option value="Low">Low priority households</option>
          <option value="Custom">Custom selection (chosen at authorization time)</option>
        </select>
      </div>

      <p v-if="stageError" class="rounded-xl bg-red-50 p-3 text-xs font-medium text-red-700" role="alert">
        {{ stageError }}
      </p>

      <div class="flex justify-end gap-2.5 pt-2">
        <button
          type="button"
          class="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50"
          @click="showStageForm = false"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="isStaging"
          class="rounded-xl bg-blue-600 px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-blue-300"
        >
          {{ isStaging ? 'Staging...' : 'Stage for Authorization' }}
        </button>
      </div>
    </form>

    <!-- Action Feedback Toast -->
    <p
      v-if="actionMessage"
      :class="actionSuccess ? 'bg-emerald-50 text-emerald-800 border-emerald-200' : 'bg-red-50 text-red-800 border-red-200'"
      class="rounded-xl border p-3.5 text-xs font-semibold"
      role="status"
    >
      {{ actionMessage }}
    </p>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin items-center justify-center rounded-full border-2 border-blue-600 border-t-transparent text-blue-600" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading broadcasts...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="notifications.length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.5a8.4 8.4 0 0 1-9 8.5 9.7 9.7 0 0 1-4.2-1L3 20l1.1-4A8.4 8.4 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No broadcasts recorded</h3>
      <p class="mt-1 text-xs text-slate-500">Staged and dispatched SMS broadcasts will be archived here.</p>
    </div>

    <!-- Broadcasts Feed -->
    <div v-else class="space-y-4">
      <article
        v-for="n in notifications"
        :key="n.sms_id"
        class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card transition-all duration-200 hover:border-slate-300 hover:shadow-card-hover"
      >
        <!-- Header & Status Pill -->
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <div>
            <h2 class="text-base font-bold text-slate-900">{{ n.subject }}</h2>
            <p class="mt-0.5 text-xs text-slate-400 font-medium">
              Target: <span class="text-slate-600 font-semibold">{{ n.recipient_type }}</span> · Staged {{ formatDate(n.created_at) }}
            </p>
          </div>
          <span :class="statusBadgeClass(n.status)" class="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold">
            {{ n.status }}
          </span>
        </div>

        <!-- Message Preview -->
        <p class="mt-3 text-xs sm:text-sm text-slate-700 bg-slate-50/70 rounded-xl p-3.5 border border-slate-100 whitespace-pre-line leading-relaxed font-mono">
          {{ n.message_body }}
        </p>

        <!-- Sent Counts Summary -->
        <div v-if="n.status !== 'Pending'" class="mt-3 flex items-center gap-3 text-xs text-slate-500 font-medium tabular-nums">
          <span class="text-emerald-700 font-bold">{{ n.sent_count }} sent</span>
          <span>·</span>
          <span class="text-red-700 font-bold">{{ n.failed_count }} failed</span>
          <span>·</span>
          <span>{{ n.total_recipients }} total recipients</span>
        </div>

        <!-- Chairperson Authorization Panel (Pending only) -->
        <div v-if="isChairperson && n.status === 'Pending'" class="mt-4 border-t border-slate-100 pt-4">
          <div v-if="n.recipient_type === 'Custom'" class="mb-3">
            <label :for="`custom-select-${n.sms_id}`" class="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Select Recipient Households
            </label>
            <select
              :id="`custom-select-${n.sms_id}`"
              multiple
              v-model="customSelections[n.sms_id]"
              class="w-full rounded-xl border border-slate-300 px-3 py-2 text-xs h-32 focus:border-blue-500 focus:outline-none"
            >
              <option v-for="h in households" :key="h.household_id" :value="h.household_id">
                {{ h.household_number }} — {{ h.head_of_family }} ({{ h.purok }})
              </option>
            </select>
          </div>
          <button
            type="button"
            :disabled="isAuthorizing[n.sms_id]"
            class="inline-flex min-h-9 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-emerald-700 disabled:bg-emerald-300"
            @click="handleAuthorize(n)"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
            <span>{{ isAuthorizing[n.sms_id] ? 'Authorizing & Dispatching...' : 'Authorize & Broadcast Now' }}</span>
          </button>
        </div>

        <p v-if="!isChairperson && n.status === 'Pending'" class="mt-3 text-xs font-medium text-amber-700">
          Awaiting authorization by the BDRRMC Chairperson before broadcast.
        </p>

        <!-- Delivery Log Drawer/Accordion -->
        <div v-if="n.logs && n.logs.length > 0" class="mt-4 border-t border-slate-100 pt-3">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-800 transition-colors"
            @click="toggleLogs(n.sms_id)"
          >
            <span>{{ expandedLogs[n.sms_id] ? 'Hide' : 'View' }} delivery audit log ({{ n.logs.length }} records)</span>
            <svg class="h-3.5 w-3.5 transition-transform" :class="{ 'rotate-180': expandedLogs[n.sms_id] }" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z" clip-rule="evenodd" />
            </svg>
          </button>

          <div v-if="expandedLogs[n.sms_id]" class="mt-3 overflow-x-auto rounded-xl border border-slate-100">
            <table class="w-full text-left text-xs">
              <thead class="border-b border-slate-100 bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                <tr>
                  <th class="py-2 px-3">Contact Number</th>
                  <th class="py-2 px-3">Status</th>
                  <th class="py-2 px-3">Gateway Feedback</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="log in n.logs" :key="log.log_id" class="hover:bg-slate-50">
                  <td class="py-2 px-3 font-mono font-medium text-slate-700 tabular-nums">{{ log.contact_number }}</td>
                  <td class="py-2 px-3">
                    <span :class="deliveryBadgeClass(log.delivery_status)" class="inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold">
                      {{ log.delivery_status }}
                    </span>
                  </td>
                  <td class="py-2 px-3 text-slate-500 font-mono text-[11px]">{{ log.gateway_response || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import * as announcementsApi from '@/services/announcementsApi'
import * as householdsApi from '@/services/householdsApi'

const authStore = useAuthStore()

const notifications = ref([])
const households = ref([])
const isLoading = ref(true)
const showStageForm = ref(false)
const isStaging = ref(false)
const stageError = ref('')
const actionMessage = ref('')
const actionSuccess = ref(false)
const customSelections = reactive({})
const isAuthorizing = reactive({})
const expandedLogs = reactive({})

const role = computed(() => authStore.user?.role)
const isSecretary = computed(() => role.value === 'Barangay Secretary')
const isChairperson = computed(() => role.value === 'BDRRMC Chairperson')

const stageForm = reactive({ subject: '', message_body: '', recipient_type: 'All' })

function statusBadgeClass(status) {
  if (status === 'Sent') return 'bg-emerald-100 text-emerald-800'
  if (status === 'Partially Sent') return 'bg-amber-100 text-amber-800'
  if (status === 'Failed') return 'bg-red-100 text-red-800'
  return 'bg-amber-50 text-amber-800 border border-amber-200'
}

function deliveryBadgeClass(status) {
  if (status === 'Delivered') return 'bg-emerald-100 text-emerald-800'
  if (status === 'Simulated') return 'bg-blue-100 text-blue-800'
  if (status === 'Failed') return 'bg-red-100 text-red-800'
  return 'bg-slate-100 text-slate-700'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Intl.DateTimeFormat('en-PH', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Manila' }).format(new Date(dateStr))
}

function toggleLogs(smsId) {
  expandedLogs[smsId] = !expandedLogs[smsId]
}

async function loadData() {
  isLoading.value = true
  try {
    const [notificationsRes, householdsRes] = await Promise.all([
      announcementsApi.listSmsNotifications(),
      householdsApi.listHouseholds(),
    ])
    notifications.value = notificationsRes.data
    households.value = householdsRes.data
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)

async function handleStage() {
  isStaging.value = true
  stageError.value = ''
  actionMessage.value = ''
  try {
    await announcementsApi.stageSmsNotification(stageForm)
    Object.assign(stageForm, { subject: '', message_body: '', recipient_type: 'All' })
    showStageForm.value = false
    await loadData()
    actionSuccess.value = true
    actionMessage.value = 'Broadcast staged for authorization.'
  } catch (error) {
    stageError.value = error.response?.data
      ? Object.values(error.response.data).flat().join(' ')
      : 'Failed to stage broadcast.'
  } finally {
    isStaging.value = false
  }
}

async function handleAuthorize(notification) {
  if (!window.confirm(`Authorize and send this broadcast to recipients matching "${notification.recipient_type}"?`)) return
  isAuthorizing[notification.sms_id] = true
  actionMessage.value = ''
  try {
    const payload = {}
    if (notification.recipient_type === 'Custom') {
      payload.household_ids = customSelections[notification.sms_id] || []
    }
    await announcementsApi.authorizeSmsNotification(notification.sms_id, payload)
    await loadData()
    actionSuccess.value = true
    actionMessage.value = 'Broadcast authorization completed.'
  } catch (error) {
    actionSuccess.value = false
    actionMessage.value = error.response?.data ? Object.values(error.response.data).flat().join(' ') : 'Failed to authorize broadcast.'
  } finally {
    isAuthorizing[notification.sms_id] = false
  }
}
</script>
