<script setup>
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
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
    errorMessage.value = err.response?.data?.error || 'Failed to prepare the report preview.'
  } finally {
    loading[kind] = false
  }
}

function downloadPreview() {
  if (!preview.value) return
  const link = document.createElement('a')
  link.href = preview.value.objectUrl
  link.download = preview.value.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function closePreview() {
  if (preview.value?.objectUrl) {
    window.URL.revokeObjectURL(preview.value.objectUrl)
  }
  preview.value = null
}

onBeforeUnmount(closePreview)
</script>

<template>
  <div class="space-y-6 pb-6 max-w-4xl">
    <!-- Breadcrumb & Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Reports</span>
      </nav>

      <div>
        <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Preparedness Reports</h1>
        <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
          Generate official PDF documentation, household vulnerability assessments, and center readiness audits.
        </p>
      </div>
    </header>

    <!-- Error Banner -->
    <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 p-4 text-xs font-semibold text-red-700" role="alert">
      {{ errorMessage }}
    </div>

    <!-- Reports Grid / Sections -->
    <div class="space-y-4">
      <!-- Household Report Section -->
      <section v-if="canViewHouseholdReport" class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start gap-4">
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600 ring-1 ring-blue-100">
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75" />
            </svg>
          </span>
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-bold text-slate-900">Household Readiness Report</h2>
            <p class="mt-1 text-xs sm:text-sm text-slate-500 leading-relaxed">
              Complete inventory including household number, head of family, recorded purok, family members count, CART priority classification, and priority vulnerability score.
            </p>

            <div class="mt-4 flex flex-wrap items-center gap-3">
              <div class="flex items-center gap-2">
                <label for="priority-filter" class="text-xs font-bold uppercase tracking-wider text-slate-600">Filter priority:</label>
                <select
                  id="priority-filter"
                  v-model="householdPriorityFilter"
                  class="rounded-xl border border-slate-200 bg-slate-50/70 px-3 py-1.5 text-xs font-semibold text-slate-700 focus:border-blue-500 focus:bg-white focus:outline-none"
                >
                  <option value="">All Priorities</option>
                  <option value="High">High Priority Only</option>
                  <option value="Medium">Medium Priority Only</option>
                  <option value="Low">Low Priority Only</option>
                </select>
              </div>

              <button
                type="button"
                class="inline-flex min-h-9 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
                :disabled="loading.household"
                @click="handlePreview('household')"
              >
                <svg v-if="!loading.household" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
                <span>{{ loading.household ? 'Preparing preview…' : 'Preview PDF' }}</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Evacuation Center Report Section -->
      <section v-if="canViewCenterReport" class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start gap-4">
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-700 ring-1 ring-amber-100">
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="m3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6" />
            </svg>
          </span>
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-bold text-slate-900">Evacuation Center Report</h2>
            <p class="mt-1 text-xs sm:text-sm text-slate-500 leading-relaxed">
              Shelter status, assigned facilities, maximum person capacity, live occupancy rates, and facility coordinator contacts.
            </p>

            <div class="mt-4">
              <button
                type="button"
                class="inline-flex min-h-9 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
                :disabled="loading.center"
                @click="handlePreview('center')"
              >
                <svg v-if="!loading.center" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
                <span>{{ loading.center ? 'Preparing preview…' : 'Preview PDF' }}</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Resident Household Report -->
      <section v-if="isResident" class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start gap-4">
          <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100">
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
            </svg>
          </span>
          <div class="min-w-0 flex-1">
            <h2 class="text-base font-bold text-slate-900">My Household Report</h2>
            <p class="mt-1 text-xs sm:text-sm text-slate-500 leading-relaxed">
              Official summary of your registered household details and evacuation prioritization profile.
            </p>

            <div class="mt-4">
              <button
                type="button"
                class="inline-flex min-h-9 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
                :disabled="loading.myHousehold"
                @click="handlePreview('myHousehold')"
              >
                <span>{{ loading.myHousehold ? 'Preparing preview…' : 'Preview PDF' }}</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <p
        v-if="!canViewHouseholdReport && !canViewCenterReport && !isResident"
        class="rounded-2xl border border-slate-200/80 bg-white p-8 text-center text-xs text-slate-500 shadow-card"
      >
        No printable reports are currently available for your account role.
      </p>
    </div>

    <!-- PDF Modal Viewer -->
    <Teleport to="body">
      <div
        v-if="preview"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-xs p-2 sm:p-5"
        role="dialog"
        aria-modal="true"
        aria-labelledby="report-preview-title"
        @keydown.esc="closePreview"
        @click.self="closePreview"
      >
        <section class="flex h-[95vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl sm:h-[90vh]">
          <header class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3 sm:px-6">
            <div class="min-w-0">
              <h2 id="report-preview-title" class="truncate text-base font-bold text-slate-900">{{ preview.title }} Preview</h2>
              <p class="text-xs text-slate-500">Review document details before saving.</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <a
                :href="preview.objectUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex min-h-9 items-center rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
              >
                Open in tab
              </a>
              <button
                type="button"
                class="inline-flex min-h-9 items-center gap-1.5 rounded-xl bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-700"
                @click="downloadPreview"
              >
                <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                </svg>
                <span>Download PDF</span>
              </button>
              <button
                type="button"
                class="inline-flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-100 hover:text-slate-800"
                aria-label="Close report preview"
                @click="closePreview"
              >
                <span aria-hidden="true" class="text-xl leading-none">&times;</span>
              </button>
            </div>
          </header>
          <iframe :src="preview.objectUrl" :title="`${preview.title} PDF preview`" class="min-h-0 flex-1 bg-slate-100" />
        </section>
      </div>
    </Teleport>
  </div>
</template>
