<script setup>
import { computed, reactive, ref } from 'vue'
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

async function handleDownload(kind) {
  errorMessage.value = ''
  loading[kind] = true
  try {
    if (kind === 'household') {
      await reportsApi.downloadHouseholdReport(householdPriorityFilter.value || null)
    } else if (kind === 'center') {
      await reportsApi.downloadEvacuationCenterReport()
    } else if (kind === 'myHousehold') {
      await reportsApi.downloadMyHouseholdReport()
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
</script>

<template>
  <div>
    <AppNavBar />

    <div class="max-w-2xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-semibold text-slate-800">Reports</h1>
      <p class="text-slate-500 mt-1 mb-6">Generate a PDF report. Downloads start immediately — there's no preview.</p>

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
          @click="handleDownload('household')"
        >
          {{ loading.household ? 'Generating…' : 'Download PDF' }}
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
          @click="handleDownload('center')"
        >
          {{ loading.center ? 'Generating…' : 'Download PDF' }}
        </button>
      </section>

      <section v-if="isResident" class="border border-slate-200 rounded-lg p-5 mb-5">
        <h2 class="text-lg font-medium text-slate-800">My Household Report</h2>
        <p class="text-slate-500 text-sm mt-1">Your own household's details on file.</p>

        <button
          class="bg-green-700 text-white rounded-md px-4 py-2 text-sm mt-3 disabled:opacity-60 disabled:cursor-not-allowed"
          :disabled="loading.myHousehold"
          @click="handleDownload('myHousehold')"
        >
          {{ loading.myHousehold ? 'Generating…' : 'Download PDF' }}
        </button>
      </section>

      <p
        v-if="!canViewHouseholdReport && !canViewCenterReport && !isResident"
        class="text-slate-500"
      >
        No reports are available for your role.
      </p>
    </div>
  </div>
</template>