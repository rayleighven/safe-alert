<template>
  <div>
          <p class="text-sm text-slate-500">Overview / Dashboard</p>
          <div class="mt-2 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 class="text-3xl font-bold tracking-tight text-slate-900">Good day, {{ authStore.user?.first_name || authStore.user?.username }}</h2>
              <p class="mt-2 text-sm text-slate-500">{{ roleDescription }}</p>
            </div>
            <router-link v-if="canViewHouseholds" to="/households" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700">
              View households
            </router-link>
          </div>

          <section class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <article v-for="metric in metrics" :key="metric.label" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div class="flex items-start justify-between gap-3">
                <p class="text-sm font-medium text-slate-500">{{ metric.label }}</p>
                <span :class="metric.iconClass" class="flex h-10 w-10 items-center justify-center rounded-xl">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" :d="metric.iconPath" />
                  </svg>
                </span>
              </div>
              <p class="mt-6 text-3xl font-bold text-slate-900">{{ metric.value }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ metric.detail }}</p>
            </article>
          </section>

          <section class="mt-6 grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
            <article class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div>
                <h3 class="text-lg font-bold text-slate-900">Priority overview</h3>
                <p class="mt-1 text-sm text-slate-500">Households by evacuation priority</p>
              </div>
              <div class="mt-6 space-y-4">
                <div v-for="priority in priorities" :key="priority.label" class="flex items-center gap-4">
                  <span :class="priority.dotClass" class="h-2.5 w-2.5 rounded-full" />
                  <span class="w-16 text-sm font-medium text-slate-700">{{ priority.label }}</span>
                  <div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
                    <div :class="priority.barClass" class="h-full rounded-full" :style="{ width: priority.percentage }" />
                  </div>
                  <span class="w-7 text-right text-sm font-bold text-slate-900">{{ priority.count }}</span>
                </div>
              </div>
              <p v-if="unassessedCount > 0" class="mt-4 text-xs text-slate-400">
                {{ unassessedCount }} household(s) not yet assessed.
              </p>
            </article>

            <article class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 class="text-lg font-bold text-slate-900">System status</h3>
              <p class="mt-1 text-sm text-slate-500">Current operational snapshot</p>
              <div class="mt-6 space-y-4">
                <div class="flex items-center justify-between rounded-xl bg-emerald-50 px-4 py-3">
                  <span class="text-sm font-medium text-emerald-800">Evacuation centers</span>
                  <span class="text-sm font-bold text-emerald-700">{{ activeCenters }} active</span>
                </div>
                <div class="flex items-center justify-between rounded-xl bg-blue-50 px-4 py-3">
                  <span class="text-sm font-medium text-blue-800">Household records</span>
                  <span class="text-sm font-bold text-blue-700">{{ households.length }} encoded</span>
                </div>
                <div class="rounded-xl border border-slate-200 px-4 py-3 text-sm leading-relaxed text-slate-600">
                  Keep household vulnerability assessments up to date to support accurate evacuation planning.
                </div>
              </div>
            </article>
          </section>

          <section v-if="canViewVulnerabilityDetails" class="mt-6">
            <article class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 class="text-lg font-bold text-slate-900">Highest priority households</h3>
              <p class="mt-1 text-sm text-slate-500">Top households by evacuation priority score</p>
              <table class="mt-6 w-full text-sm">
                <thead class="text-left text-slate-500">
                  <tr>
                    <th class="py-2">Household #</th>
                    <th class="py-2">Head of Family</th>
                    <th class="py-2">Purok</th>
                    <th class="py-2">Priority</th>
                    <th class="py-2">Score</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="household in topPriorityHouseholds"
                    :key="household.household_id"
                    class="cursor-pointer border-t border-slate-100 hover:bg-slate-50"
                    @click="router.push({ name: 'household-detail', params: { id: household.household_id } })"
                  >
                    <td class="py-2 font-medium text-slate-800">{{ household.household_number }}</td>
                    <td class="py-2">{{ household.head_of_family }}</td>
                    <td class="py-2">{{ household.purok }}</td>
                    <td class="py-2">
                      <span :class="priorityBadgeClass(household.evacuation_priority)" class="rounded-full px-2 py-1 text-xs font-medium">
                        {{ household.evacuation_priority }}
                      </span>
                    </td>
                    <td class="py-2">{{ household.priority_score }}%</td>
                  </tr>
                </tbody>
              </table>
              <p v-if="topPriorityHouseholds.length === 0" class="text-sm text-slate-400">No assessed households yet.</p>
            </article>
          </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as householdsApi from '@/services/householdsApi'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'

const authStore = useAuthStore()
const router = useRouter()
const households = ref([])
const centers = ref([])

const roleDescriptions = {
  'Barangay Secretary': 'Full system administration and household record management.',
  'BDRRMC Chairperson': 'Executive oversight and SMS broadcast authorization.',
  'MDRRMO Officer': 'Read-only municipal-level monitoring across both barangays.',
  'Barangay Kagawad/Tanod': 'Field validation and evacuation center management.',
  'Barangay Healthworker': 'Health-related vulnerability indicator management.',
  Resident: 'View your household information and public announcements.',
}

const roleDescription = computed(() => roleDescriptions[authStore.user?.role] || '')
const canViewHouseholds = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer', 'Resident',
].includes(authStore.user?.role))
const canViewVulnerabilityDetails = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer',
].includes(authStore.user?.role))

const priorityCounts = computed(() => ({
  High: households.value.filter((household) => household.evacuation_priority === 'High').length,
  Medium: households.value.filter((household) => household.evacuation_priority === 'Medium').length,
  Low: households.value.filter((household) => household.evacuation_priority === 'Low').length,
}))
const unassessedCount = computed(() => households.value.filter((household) => !household.evacuation_priority).length)
const topPriorityHouseholds = computed(() => households.value
  .filter((household) => household.evacuation_priority)
  .sort((a, b) => (b.priority_score ?? 0) - (a.priority_score ?? 0))
  .slice(0, 10))

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}
const totalResidents = computed(() => households.value.reduce((total, household) => total + (Number(household.total_members) || 0), 0))
const activeCenters = computed(() => centers.value.filter((center) => center.status === 'Active').length)
const metrics = computed(() => [
  { label: 'Total Households', value: households.value.length, detail: 'Encoded records', iconClass: 'bg-blue-50 text-blue-600', iconPath: 'm3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6' },
  { label: 'High Priority', value: priorityCounts.value.High, detail: 'Evacuate first', iconClass: 'bg-red-50 text-red-500', iconPath: 'M12 3 4.5 6v5.5c0 4.5 3.1 7.7 7.5 9.5 4.4-1.8 7.5-5 7.5-9.5V6L12 3Zm0 5v5m0 3h.01' },
  { label: 'Residents Covered', value: totalResidents.value, detail: 'Across all households', iconClass: 'bg-cyan-50 text-cyan-600', iconPath: 'M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75' },
  { label: 'Active Centers', value: activeCenters.value, detail: `${centers.value.length} total centers`, iconClass: 'bg-amber-50 text-amber-600', iconPath: 'm3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6' },
])
const priorities = computed(() => {
  const total = households.value.length || 1
  return [
    { label: 'High', count: priorityCounts.value.High, percentage: `${(priorityCounts.value.High / total) * 100}%`, dotClass: 'bg-red-500', barClass: 'bg-red-400' },
    { label: 'Medium', count: priorityCounts.value.Medium, percentage: `${(priorityCounts.value.Medium / total) * 100}%`, dotClass: 'bg-amber-500', barClass: 'bg-amber-400' },
    { label: 'Low', count: priorityCounts.value.Low, percentage: `${(priorityCounts.value.Low / total) * 100}%`, dotClass: 'bg-emerald-500', barClass: 'bg-emerald-400' },
  ]
})

onMounted(async () => {
  const [householdsResult, centersResult] = await Promise.allSettled([
    householdsApi.listHouseholds(),
    evacuationCentersApi.listCenters(),
  ])
  if (householdsResult.status === 'fulfilled') households.value = householdsResult.value.data
  if (centersResult.status === 'fulfilled') centers.value = centersResult.value.data
})
</script>
