<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as reportsApi from '@/services/reportsApi'

const authStore = useAuthStore()

const canViewHouseholdReport = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'Barangay Kagawad/Tanod',
    'Barangay Healthworker',
    'MDRRMO Officer',
  ].includes(role)
})

const canViewCenterReport = computed(() => {
  const role = authStore.user?.role
  return [
    'Barangay Secretary',
    'Barangay Kagawad/Tanod',
    'BDRRMC Chairperson',
    'MDRRMO Officer',
  ].includes(role)
})

const isResident = computed(() => authStore.user?.role === 'Resident')

const householdPriorityFilter = ref('')
const loading = reactive({ household: false, center: false, myHousehold: false })
const errorMessage = ref('')
const preview = ref(null)

const reportDetails = {
  household: { title: 'Household Report', filename: 'household_report.pdf' },
  center: { title: 'Evacuation Center Report', filename: 'evacuation_center_report.pdf' },
  myHousehold: { title: 'My Household Report', filename: 'my_household_report.pdf' },
}

async function handlePreview(kind) {
  errorMessage.value = ''
  loading[kind] = true
  try {
    let blob
    if (kind === 'household') {
      blob = await reportsApi.getHouseholdReport(householdPriorityFilter.value || null)
    } else if (kind === 'center') {
      blob = await reportsApi.getEvacuationCenterReport()
    } else if (kind === 'myHousehold') {
      blob = await reportsApi.getMyHouseholdReport()
    }
    closePreview()
    preview.value = {
      ...reportDetails[kind],
      blob,
      objectUrl: window.URL.createObjectURL(blob),
    }
  } catch (err) {
    if (err?.response?.status === 404) {
      errorMessage.value = 'No household is linked to your account yet. Contact your Barangay Secretary.'
    } else if (err?.response?.status === 403) {
      errorMessage.value = 'You are not authorized to view this report.'
    } else {
      errorMessage.value = 'Something went wrong generating the report. Please try again.'
    }
  } finally {
    loading[kind] = false
  }
}

function closePreview() {
  if (preview.value?.objectUrl) window.URL.revokeObjectURL(preview.value.objectUrl)
  preview.value = null
}

function downloadPreview() {
  if (preview.value) reportsApi.downloadReportBlob(preview.value.blob, preview.value.filename)
}

onBeforeUnmount(closePreview)
</script>

<template>
  <div>
    <AppNavBar />

    <div class="max-w-2xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-semibold text-slate-800">Reports</h1>
      <p class="text-slate-500 mt-1 mb-6">Preview each PDF before downloading it.</p>

      <div v-if="errorMessage" class="bg-red-50 text-red-700 rounded-md px-4 py-3 mb-4">
        {{ errorMessage }}
      </div>

      <section v-if="canViewHouseholdReport" class="border border-slate-200 rounded-lg p-5 mb-5">
        <h2 class="text-lg font-medium text-slate-800">Household Report</h2>
        <p class="text-slate-500 text-sm mt-1">
          Household #, head of family, purok, members, priority, and score.
        </p>

        <div class="flex items-center gap-2 mt-3 mb-4">
          <label for="priority-filter" class="text-sm text-slate-600">Filter by priority</label>
          <select
            id="priority-filter"
            v-model="householdPriorityFilter"
            class="border border-slate-300 rounded-md px-2 py-1 text-sm"
          >
            <option value="">All</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        <button
          class="bg-green-700 text-white rounded-md px-4 py-2 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
          :disabled="loading.household"
          @click="handlePreview('household')"
        >
          {{ loading.household ? 'Preparing preview…' : 'Preview PDF' }}
        </button>
      </section>

      <section v-if="canViewCenterReport" class="border border-slate-200 rounded-lg p-5 mb-5">
        <h2 class="text-lg font-medium text-slate-800">Evacuation Center Report</h2>
        <p class="text-slate-500 text-sm mt-1">
          Name, status, capacity, occupancy, and contact info.
        </p>

        <button
          class="bg-green-700 text-white rounded-md px-4 py-2 text-sm mt-3 disabled:opacity-60 disabled:cursor-not-allowed"
          :disabled="loading.center"
          @click="handlePreview('center')"
        >
          {{ loading.center ? 'Preparing preview…' : 'Preview PDF' }}
        </button>
      </section>

      <section v-if="isResident" class="border border-slate-200 rounded-lg p-5 mb-5">
        <h2 class="text-lg font-medium text-slate-800">My Household Report</h2>
        <p class="text-slate-500 text-sm mt-1">Your own household's details on file.</p>

        <button
          class="bg-green-700 text-white rounded-md px-4 py-2 text-sm mt-3 disabled:opacity-60 disabled:cursor-not-allowed"
          :disabled="loading.myHousehold"
          @click="handlePreview('myHousehold')"
        >
          {{ loading.myHousehold ? 'Preparing preview…' : 'Preview PDF' }}
        </button>
      </section>

      <p
        v-if="!canViewHouseholdReport && !canViewCenterReport && !isResident"
        class="text-slate-500"
      >
        No reports are available for your role.
      </p>
    </div>

    <Teleport to="body">
      <div
        v-if="preview"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-2 sm:p-5"
        role="dialog"
        aria-modal="true"
        aria-labelledby="report-preview-title"
        @keydown.esc="closePreview"
        @click.self="closePreview"
      >
        <section class="flex h-[95vh] w-full max-w-6xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl sm:h-[90vh]">
          <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3 sm:px-6">
            <div class="min-w-0">
              <h2 id="report-preview-title" class="truncate text-lg font-semibold text-slate-900">{{ preview.title }} preview</h2>
              <p class="text-xs text-slate-500">Review the report, then download the PDF when ready.</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <a
                :href="preview.objectUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex min-h-10 items-center rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Open in new tab
              </a>
              <button
                type="button"
                class="inline-flex min-h-10 items-center rounded-lg bg-blue-700 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-800"
                @click="downloadPreview"
              >
                Download PDF
              </button>
              <button
                type="button"
                class="inline-flex h-10 w-10 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800"
                aria-label="Close report preview"
                @click="closePreview"
              >
                <span aria-hidden="true" class="text-2xl leading-none">&times;</span>
              </button>
            </div>
          </header>
          <iframe :src="preview.objectUrl" :title="`${preview.title} PDF preview`" class="min-h-0 flex-1 bg-slate-100" />
        </section>
      </div>
    </Teleport>
  </div>
</template>
