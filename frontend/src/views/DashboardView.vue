<template>
  <div class="space-y-6 pb-4">
    <header class="space-y-3">
      <p class="text-sm text-slate-500">SAFE-ALERT / Dashboard</p>
      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Preparedness Dashboard</h1>
          <p class="mt-1 text-sm text-slate-500">
            {{ locationDescription }}<span v-if="updatedAt"> · Updated {{ updatedAt }}</span>
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link to="/reports" class="inline-flex min-h-11 items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
            View reports
          </router-link>
          <router-link v-if="canCreateHousehold" to="/households/new" class="inline-flex min-h-11 items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            + New household
          </router-link>
        </div>
      </div>
      <p class="text-sm text-slate-500">{{ roleDescription }}</p>
    </header>

    <section v-if="urgentAnnouncement || pendingBroadcasts.length" class="flex flex-col gap-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5" aria-label="Important system updates">
      <div class="flex items-start gap-3">
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-700" aria-hidden="true">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3 2.8 20h18.4L12 3Zm0 6v5m0 3h.01" /></svg>
        </span>
        <div class="min-w-0">
          <p v-if="urgentAnnouncement" class="font-semibold text-amber-950">{{ urgentAnnouncement.title }}</p>
          <p v-else class="font-semibold text-amber-950">SMS broadcast awaiting authorization</p>
          <p v-if="urgentAnnouncement" class="mt-1 line-clamp-2 text-sm text-amber-900">{{ urgentAnnouncement.body }}</p>
          <p v-else class="mt-1 text-sm text-amber-900">{{ pendingBroadcasts.length }} staged broadcast(s) are waiting for the BDRRMC Chairperson.</p>
          <p v-if="urgentAnnouncement && pendingBroadcasts.length" class="mt-1 text-xs text-amber-800">{{ pendingBroadcasts.length }} SMS broadcast(s) also await authorization.</p>
        </div>
      </div>
      <router-link v-if="canAuthorizeSms && pendingBroadcasts.length" to="/sms-notifications" class="inline-flex min-h-11 shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
        Review authorization queue <span aria-hidden="true">→</span>
      </router-link>
      <router-link v-else to="/announcements" class="inline-flex min-h-11 shrink-0 items-center justify-center rounded-xl border border-amber-300 bg-white px-4 py-2 text-sm font-semibold text-amber-900 hover:bg-amber-100">
        View updates
      </router-link>
    </section>

    <section class="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4" aria-label="Readiness metrics">
      <article v-for="metric in metrics" :key="metric.label" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-start justify-between gap-3">
          <p class="text-sm font-medium text-slate-500">{{ metric.label }}</p>
          <span :class="metric.iconClass" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" :d="metric.iconPath" /></svg>
          </span>
        </div>
        <p class="mt-5 text-3xl font-bold tracking-tight text-slate-900">{{ metric.value }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ metric.detail }}</p>
      </article>
    </section>

    <p v-if="loadWarning" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900" role="status">{{ loadWarning }}</p>

    <section class="grid gap-5 xl:grid-cols-2" aria-label="Readiness analytics">
      <article class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-bold text-slate-900">CART priority distribution</h2>
            <p class="mt-1 text-sm text-slate-500">Assessed households by evacuation priority</p>
          </div>
          <span class="rounded-full bg-cyan-50 px-2.5 py-1 text-xs font-semibold text-cyan-800">Live</span>
        </div>
        <div v-if="canViewVulnerabilityDetails && assessedHouseholdCount" class="mt-5 flex flex-col items-center gap-6 sm:flex-row sm:justify-around">
          <div class="relative h-44 w-44 shrink-0 rounded-full" :style="{ background: priorityDistributionGradient }" role="img" :aria-label="priorityChartLabel">
            <div class="absolute inset-7 flex flex-col items-center justify-center rounded-full bg-white text-center">
              <span class="text-3xl font-bold text-slate-900">{{ assessedHouseholdCount }}</span>
              <span class="mt-1 text-xs text-slate-500">assessed</span>
            </div>
          </div>
          <ul class="w-full max-w-xs space-y-3">
            <li v-for="item in priorityLegend" :key="item.label" class="flex items-center justify-between gap-4 text-sm">
              <span class="flex items-center gap-2 text-slate-600"><span :class="item.dot" class="h-2.5 w-2.5 rounded-full" />{{ item.label }} priority</span>
              <span class="font-bold text-slate-900">{{ item.count }}</span>
            </li>
            <li class="border-t border-slate-100 pt-3 text-xs text-slate-500">{{ unassessedCount }} household(s) not yet assessed</li>
          </ul>
        </div>
        <p v-else class="mt-8 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          {{ canViewVulnerabilityDetails ? 'No assessed household records yet.' : 'Household priority analytics are not available for this role.' }}
        </p>
      </article>

      <article class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900">Vulnerability by purok</h2>
          <p class="mt-1 text-sm text-slate-500">Assessed households grouped by recorded purok</p>
        </div>
        <div v-if="canViewVulnerabilityDetails && purokStats.length" class="mt-5 space-y-4">
          <div v-for="group in purokStats" :key="group.name" class="grid grid-cols-[5rem_minmax(0,1fr)_2rem] items-center gap-3">
            <span class="truncate text-xs font-medium text-slate-600 sm:text-sm" :title="group.name">{{ group.name }}</span>
            <div class="h-5 overflow-hidden rounded-full bg-slate-100" role="img" :aria-label="`${group.name}: ${group.high} high, ${group.medium} medium, ${group.low} low priority`">
              <div class="flex h-full overflow-hidden rounded-full" :style="{ width: `${(group.total / maxPurokCount) * 100}%` }">
                <span class="bg-red-500" :style="{ width: `${(group.high / group.total) * 100}%` }" />
                <span class="bg-amber-400" :style="{ width: `${(group.medium / group.total) * 100}%` }" />
                <span class="bg-emerald-500" :style="{ width: `${(group.low / group.total) * 100}%` }" />
              </div>
            </div>
            <span class="text-right text-xs font-bold text-slate-700">{{ group.total }}</span>
          </div>
          <div class="flex flex-wrap gap-x-4 gap-y-2 border-t border-slate-100 pt-4 text-xs text-slate-500">
            <span class="flex items-center gap-1.5"><i class="h-2.5 w-2.5 rounded-full bg-red-500" />High</span>
            <span class="flex items-center gap-1.5"><i class="h-2.5 w-2.5 rounded-full bg-amber-400" />Medium</span>
            <span class="flex items-center gap-1.5"><i class="h-2.5 w-2.5 rounded-full bg-emerald-500" />Low</span>
          </div>
        </div>
        <p v-else class="mt-8 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          {{ canViewVulnerabilityDetails ? 'Purok analytics will appear when assessed households are available.' : 'Household vulnerability details are not available for this role.' }}
        </p>
      </article>
    </section>

    <section class="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]" aria-label="Hazard maps and evacuation centers">
      <article class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Hazard exposure maps</h2>
            <p class="mt-1 text-sm text-slate-500">Project NOAH references and other map resources</p>
          </div>
          <router-link to="/hazard-maps" class="shrink-0 text-sm font-semibold text-blue-700 hover:text-blue-800">View maps</router-link>
        </div>
        <div v-if="hazardMaps.length" class="mt-5 space-y-3">
          <article v-for="hazardMap in hazardMaps.slice(0, 3)" :key="hazardMap.map_id" class="flex min-w-0 items-center gap-3 rounded-xl border border-slate-100 p-3">
            <img v-if="hazardMap.map_image" :src="hazardMap.map_image" :alt="''" class="h-14 w-16 shrink-0 rounded-lg object-cover" />
            <span v-else class="flex h-14 w-16 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-xs font-bold text-blue-700">{{ hazardMap.hazard_type }}</span>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold text-slate-800">{{ hazardMap.map_title }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ hazardMap.hazard_type }} · {{ hazardMap.source }}</p>
            </div>
            <router-link v-if="isInteractiveNoahMap(hazardMap)" :to="{ name: 'hazard-map-interactive', params: { id: hazardMap.map_id } }" class="shrink-0 text-xs font-semibold text-emerald-700 hover:text-emerald-800">Open map</router-link>
            <a v-else-if="hazardMap.map_url" :href="hazardMap.map_url" target="_blank" rel="noopener noreferrer" class="shrink-0 text-xs font-semibold text-blue-700 hover:text-blue-800">Open link</a>
          </article>
          <p v-if="hazardMaps.length > 3" class="text-xs text-slate-500">{{ hazardMaps.length - 3 }} more map reference(s)</p>
        </div>
        <p v-else class="mt-5 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">No hazard maps have been added for this area yet.</p>
      </article>

      <article class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Evacuation centers</h2>
            <p class="mt-1 text-sm text-slate-500">Current occupancy and available capacity</p>
          </div>
          <router-link to="/evacuation-centers" class="shrink-0 text-sm font-semibold text-blue-700 hover:text-blue-800">Manage</router-link>
        </div>
        <div v-if="activeCentersList.length" class="mt-5 space-y-4">
          <div v-for="center in activeCentersList.slice(0, 5)" :key="center.center_id" class="space-y-2">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold text-slate-800">{{ center.name }}</p>
                <p class="mt-0.5 text-xs text-slate-500">{{ center.address }}</p>
              </div>
              <span class="shrink-0 text-sm font-bold text-slate-800">{{ formatNumber(center.current_occupancy) }} / {{ formatNumber(center.capacity) }}</span>
            </div>
            <div class="h-2 overflow-hidden rounded-full bg-slate-100" role="img" :aria-label="`${center.name}: ${center.current_occupancy} of ${center.capacity} occupants`">
              <div :class="capacityBarClass(center)" class="h-full rounded-full transition-all" :style="{ width: `${capacityPercentage(center)}%` }" />
            </div>
          </div>
        </div>
        <p v-else class="mt-5 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">No active evacuation centers are available.</p>
      </article>
    </section>

    <section class="grid items-start gap-5 xl:grid-cols-[1.15fr_0.85fr]" aria-label="Recent updates and quick actions">
      <article class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Recent updates</h2>
            <p class="mt-1 text-sm text-slate-500">Latest announcements and SMS broadcast changes</p>
          </div>
          <router-link to="/announcements" class="shrink-0 text-sm font-semibold text-blue-700 hover:text-blue-800">All updates</router-link>
        </div>
        <ul v-if="recentUpdates.length" class="mt-4 divide-y divide-slate-100">
          <li v-for="item in recentUpdates" :key="item.id" class="flex gap-3 py-4 first:pt-2 last:pb-1">
            <span :class="item.iconClass" class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-xs font-bold" aria-hidden="true">{{ item.icon }}</span>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-slate-800">{{ item.title }}</p>
              <p class="mt-1 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ item.detail }}</p>
              <p class="mt-1 text-xs text-slate-400">{{ relativeTime(item.date) }}</p>
            </div>
          </li>
        </ul>
        <p v-else class="mt-5 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">No recent announcements or SMS broadcasts.</p>
      </article>

      <div class="space-y-5">
        <article class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <h2 class="text-lg font-bold text-slate-900">Quick actions</h2>
          <p class="mt-1 text-sm text-slate-500">Shortcuts available to your account</p>
          <div class="mt-4 grid gap-2 sm:grid-cols-2">
            <router-link v-for="action in quickActions" :key="action.label" :to="action.to" class="group flex min-h-16 items-center gap-3 rounded-xl border border-slate-200 p-3 transition-colors hover:border-blue-300 hover:bg-blue-50">
              <span :class="action.iconClass" class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-xs font-bold" aria-hidden="true">{{ action.icon }}</span>
              <span class="text-sm font-semibold text-slate-700 group-hover:text-blue-800">{{ action.label }}</span>
            </router-link>
          </div>
        </article>

        <article v-if="hasSmsAccess" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-bold text-slate-900">Awaiting authorization</h2>
              <p class="mt-1 text-sm text-slate-500">Staged SMS broadcasts</p>
            </div>
            <span class="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-bold text-amber-900">{{ pendingBroadcasts.length }} pending</span>
          </div>
          <div v-if="pendingBroadcasts.length" class="mt-4 space-y-3">
            <div v-for="broadcast in pendingBroadcasts.slice(0, 3)" :key="broadcast.sms_id" class="rounded-xl border border-slate-200 p-3">
              <p class="text-sm font-semibold text-slate-800">{{ broadcast.subject }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ broadcast.recipient_type }} · Staged {{ relativeTime(broadcast.created_at) }}</p>
              <router-link to="/sms-notifications" class="mt-3 inline-flex min-h-9 items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-blue-700">
                {{ canAuthorizeSms ? 'Review and authorize' : 'Review broadcast' }}
              </router-link>
            </div>
          </div>
          <p v-else class="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No broadcasts are awaiting authorization.</p>
        </article>
      </div>
    </section>

    <section v-if="canViewVulnerabilityDetails" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-slate-900">Highest priority households</h2>
          <p class="mt-1 text-sm text-slate-500">Top households by evacuation priority score</p>
        </div>
        <router-link to="/households" class="text-sm font-semibold text-blue-700 hover:text-blue-800">View households</router-link>
      </div>
      <div v-if="topPriorityHouseholds.length" class="mt-4 overflow-x-auto">
        <table class="w-full min-w-[600px] text-left text-sm">
          <thead class="text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr><th class="py-2 pr-4">Household #</th><th class="py-2 pr-4">Head of Family</th><th class="py-2 pr-4">Purok</th><th class="py-2 pr-4">Priority</th><th class="py-2">Score</th></tr>
          </thead>
          <tbody>
            <tr v-for="household in topPriorityHouseholds" :key="household.household_id" class="cursor-pointer border-t border-slate-100 hover:bg-slate-50" tabindex="0" @click="openHousehold(household)" @keydown.enter="openHousehold(household)">
              <td class="py-3 pr-4 font-medium text-slate-800">{{ household.household_number }}</td>
              <td class="py-3 pr-4 text-slate-700">{{ household.head_of_family }}</td>
              <td class="py-3 pr-4 text-slate-700">{{ household.purok }}</td>
              <td class="py-3 pr-4"><span :class="priorityBadgeClass(household.evacuation_priority)" class="rounded-full px-2 py-1 text-xs font-medium">{{ household.evacuation_priority }}</span></td>
              <td class="py-3 text-slate-700">{{ household.priority_score }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">No assessed households yet.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as householdsApi from '@/services/householdsApi'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'
import * as announcementsApi from '@/services/announcementsApi'
import * as mapsApi from '@/services/mapsApi'
import { NOAH_HAZARD_LAYERS } from '@/services/noahHazardLayers'

const authStore = useAuthStore()
const router = useRouter()
const households = ref([])
const centers = ref([])
const announcements = ref([])
const hazardMaps = ref([])
const smsNotifications = ref([])
const updatedAt = ref('')
const loadIssues = ref([])

const role = computed(() => authStore.user?.role)
const roleDescriptions = {
  'Barangay Secretary': 'Coordinate barangay readiness, household records, and emergency updates.',
  'BDRRMC Chairperson': 'Review response information and authorize staged emergency broadcasts.',
  'MDRRMO Officer': 'Monitor municipal-level readiness information across both barangays.',
  'Barangay Kagawad/Tanod': 'Review field assessments and evacuation center readiness.',
  'Barangay Healthworker': 'Review household vulnerability information for your assigned purok.',
  Resident: 'Review evacuation information and public safety updates for your household.',
}
const roleDescription = computed(() => roleDescriptions[role.value] || '')
const locationDescription = computed(() => {
  const barangay = authStore.user?.barangay_name
  return barangay ? `Baclayon, Bohol · Barangay ${barangay}` : 'Municipality of Baclayon, Bohol · All barangays'
})
const canCreateHousehold = computed(() => role.value === 'Barangay Secretary')
const canViewHouseholds = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer', 'Resident',
].includes(role.value))
const canViewVulnerabilityDetails = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer',
].includes(role.value))
const hasSmsAccess = computed(() => role.value !== 'Resident')
const canAuthorizeSms = computed(() => role.value === 'BDRRMC Chairperson')
const canManageAnnouncements = computed(() => ['Barangay Secretary', 'MDRRMO Officer'].includes(role.value))
const canViewReports = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'BDRRMC Chairperson', 'MDRRMO Officer', 'Resident',
].includes(role.value))

const householdCount = computed(() => households.value.length)
const priorityCounts = computed(() => ({
  High: households.value.filter((household) => household.evacuation_priority === 'High').length,
  Medium: households.value.filter((household) => household.evacuation_priority === 'Medium').length,
  Low: households.value.filter((household) => household.evacuation_priority === 'Low').length,
}))
const assessedHouseholdCount = computed(() => priorityCounts.value.High + priorityCounts.value.Medium + priorityCounts.value.Low)
const unassessedCount = computed(() => households.value.filter((household) => !household.evacuation_priority).length)
const topPriorityHouseholds = computed(() => households.value
  .filter((household) => household.evacuation_priority)
  .slice()
  .sort((a, b) => (Number(b.priority_score) || 0) - (Number(a.priority_score) || 0))
  .slice(0, 10))
const totalResidents = computed(() => households.value.reduce((total, household) => total + (Number(household.total_members) || 0), 0))
const activeCentersList = computed(() => centers.value.filter((center) => center.status === 'Active'))
const activeCenters = computed(() => activeCentersList.value.length)
const totalCapacity = computed(() => activeCentersList.value.reduce((total, center) => total + (Number(center.capacity) || 0), 0))
const occupiedCapacity = computed(() => activeCentersList.value.reduce((total, center) => total + (Number(center.current_occupancy) || 0), 0))
const capacityUsed = computed(() => totalCapacity.value ? Math.min(100, Math.round((occupiedCapacity.value / totalCapacity.value) * 100)) : null)
const deliveryStats = computed(() => {
  const logs = smsNotifications.value.flatMap((notification) => notification.logs || [])
  const delivered = logs.filter((log) => log.delivery_status === 'Delivered').length
  const failed = logs.filter((log) => log.delivery_status === 'Failed').length
  const simulated = logs.filter((log) => log.delivery_status === 'Simulated').length
  const decided = delivered + failed
  return { delivered, failed, simulated, rate: decided ? Math.round((delivered / decided) * 1000) / 10 : null }
})

const metrics = computed(() => [
  { label: 'Households encoded', value: canViewHouseholds.value ? formatNumber(householdCount.value) : '—', detail: canViewHouseholds.value ? `${formatNumber(assessedHouseholdCount.value)} classified by CART` : 'Not available for this role', iconClass: 'bg-blue-50 text-blue-700', iconPath: 'm3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6' },
  { label: 'High-priority households', value: canViewHouseholds.value ? formatNumber(priorityCounts.value.High) : '—', detail: canViewHouseholds.value ? `${householdCount.value ? ((priorityCounts.value.High / householdCount.value) * 100).toFixed(1) : 0}% of encoded households` : 'Not available for this role', iconClass: 'bg-red-50 text-red-600', iconPath: 'M12 3 4.5 6v5.5c0 4.5 3.1 7.7 7.5 9.5 4.4-1.8 7.5-5 7.5-9.5V6L12 3Zm0 5v5m0 3h.01' },
  { label: 'Evacuation capacity used', value: capacityUsed.value === null ? '—' : `${capacityUsed.value}%`, detail: totalCapacity.value ? `${formatNumber(occupiedCapacity.value)} of ${formatNumber(totalCapacity.value)} places occupied` : `${activeCenters.value} active center(s) · capacity not recorded`, iconClass: 'bg-amber-50 text-amber-700', iconPath: 'M4 20h16M6 20V8l6-4 6 4v12m-9-8h.01M12 12h.01m3 0h.01m-6 4h.01m3 0h.01m3 0h.01' },
  { label: 'SMS delivery rate', value: hasSmsAccess.value && deliveryStats.value.rate !== null ? `${deliveryStats.value.rate}%` : '—', detail: hasSmsAccess.value ? `${deliveryStats.value.delivered} delivered · ${deliveryStats.value.failed} failed${deliveryStats.value.simulated ? ` · ${deliveryStats.value.simulated} simulated` : ''}` : 'Not available for this role', iconClass: 'bg-emerald-50 text-emerald-700', iconPath: 'M4 5h16v11H8l-4 4V5Zm4 4h8m-8 3h5' },
])

const priorityLegend = computed(() => [
  { label: 'High', count: priorityCounts.value.High, dot: 'bg-red-500' },
  { label: 'Medium', count: priorityCounts.value.Medium, dot: 'bg-amber-400' },
  { label: 'Low', count: priorityCounts.value.Low, dot: 'bg-emerald-500' },
])
const priorityDistributionGradient = computed(() => {
  const total = assessedHouseholdCount.value
  if (!total) return 'conic-gradient(#e2e8f0 0% 100%)'
  const highEnd = priorityCounts.value.High / total * 100
  const mediumEnd = highEnd + priorityCounts.value.Medium / total * 100
  return `conic-gradient(#ef4444 0% ${highEnd}%, #fbbf24 ${highEnd}% ${mediumEnd}%, #10b981 ${mediumEnd}% 100%)`
})
const priorityChartLabel = computed(() => `Priority distribution: ${priorityCounts.value.High} high, ${priorityCounts.value.Medium} medium, ${priorityCounts.value.Low} low`)

const purokStats = computed(() => {
  const groups = new Map()
  for (const household of households.value) {
    if (!household.evacuation_priority) continue
    const name = household.purok || 'Unassigned'
    if (!groups.has(name)) groups.set(name, { name, high: 0, medium: 0, low: 0, total: 0 })
    const group = groups.get(name)
    const key = household.evacuation_priority.toLowerCase()
    if (key in group) {
      group[key] += 1
      group.total += 1
    }
  }
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true })).slice(0, 8)
})
const maxPurokCount = computed(() => Math.max(1, ...purokStats.value.map((group) => group.total)))

const urgentAnnouncement = computed(() => announcements.value.find((announcement) => {
  const urgent = (announcement.categories || []).some((category) => ['Emergency', 'Alert'].includes(category.category))
  const notExpired = !announcement.expires_at || new Date(announcement.expires_at) > new Date()
  return urgent && notExpired
}) || null)
const pendingBroadcasts = computed(() => smsNotifications.value.filter((notification) => notification.status === 'Pending'))
const recentUpdates = computed(() => [
  ...announcements.value.map((announcement) => ({
    id: `announcement-${announcement.announcement_id}`,
    title: announcement.title,
    detail: announcement.body,
    date: announcement.created_at,
    icon: 'A',
    iconClass: 'bg-amber-50 text-amber-700',
  })),
  ...smsNotifications.value.map((notification) => ({
    id: `sms-${notification.sms_id}`,
    title: `${notification.subject} · ${notification.status}`,
    detail: `${notification.recipient_type} recipients · ${notification.sent_count} sent · ${notification.failed_count} failed`,
    date: notification.created_at,
    icon: 'SMS',
    iconClass: 'bg-cyan-50 text-cyan-800',
  })),
].filter((item) => item.date).sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5))

const quickActions = computed(() => {
  const actions = []
  if (canCreateHousehold.value) actions.push({ label: 'Add household', to: '/households/new', icon: 'HH', iconClass: 'bg-blue-50 text-blue-700' })
  if (canManageAnnouncements.value) actions.push({ label: 'Post announcement', to: '/announcements/new', icon: 'AN', iconClass: 'bg-amber-50 text-amber-700' })
  if (role.value === 'Barangay Secretary') actions.push({ label: 'Stage SMS alert', to: '/sms-notifications', icon: 'SMS', iconClass: 'bg-cyan-50 text-cyan-800' })
  if (canAuthorizeSms.value) actions.push({ label: 'Authorize SMS', to: '/sms-notifications', icon: 'OK', iconClass: 'bg-emerald-50 text-emerald-700' })
  if (role.value === 'Barangay Kagawad/Tanod') actions.push({ label: 'Update center occupancy', to: '/evacuation-centers', icon: 'EC', iconClass: 'bg-orange-50 text-orange-700' })
  if (role.value === 'Barangay Secretary') actions.push({ label: 'Manage accounts', to: '/accounts', icon: 'UA', iconClass: 'bg-indigo-50 text-indigo-700' })
  if (canViewReports.value) actions.push({ label: 'Generate reports', to: '/reports', icon: 'PDF', iconClass: 'bg-slate-100 text-slate-700' })
  return actions
})

const loadWarning = computed(() => loadIssues.value.length ? `Some dashboard data could not be loaded: ${loadIssues.value.join(', ')}.` : '')

function formatNumber(value) {
  return new Intl.NumberFormat().format(Number(value) || 0)
}

function formatDate(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('en-PH', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Manila' }).format(new Date(value))
}

function relativeTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Recently'
  const minutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000))
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hr${hours === 1 ? '' : 's'} ago`
  const days = Math.floor(hours / 24)
  return `${days} day${days === 1 ? '' : 's'} ago`
}

function capacityPercentage(center) {
  const capacity = Number(center.capacity) || 0
  return capacity ? Math.min(100, Math.round((Number(center.current_occupancy || 0) / capacity) * 100)) : 0
}

function capacityBarClass(center) {
  const percentage = capacityPercentage(center)
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
}

function isInteractiveNoahMap(hazardMap) {
  return hazardMap.source === 'Project NOAH' && Boolean(NOAH_HAZARD_LAYERS[hazardMap.hazard_type])
}

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-amber-100 text-amber-800'
  return 'bg-emerald-100 text-emerald-700'
}

function openHousehold(household) {
  router.push({ name: 'household-detail', params: { id: household.household_id } })
}

onMounted(async () => {
  const requests = [
    householdsApi.listHouseholds(),
    evacuationCentersApi.listCenters(),
    announcementsApi.listAnnouncements(),
    mapsApi.listHazardMaps(),
  ]
  if (hasSmsAccess.value) requests.push(announcementsApi.listSmsNotifications())
  const results = await Promise.allSettled(requests)
  const [householdResult, centerResult, announcementResult, mapResult] = results
  loadIssues.value = []
  if (householdResult.status === 'fulfilled') households.value = householdResult.value.data
  else loadIssues.value.push('households')
  if (centerResult.status === 'fulfilled') centers.value = centerResult.value.data
  else loadIssues.value.push('evacuation centers')
  if (announcementResult.status === 'fulfilled') announcements.value = announcementResult.value.data
  else loadIssues.value.push('announcements')
  if (mapResult.status === 'fulfilled') hazardMaps.value = mapResult.value.data
  else loadIssues.value.push('hazard maps')
  if (hasSmsAccess.value) {
    const smsResult = results[4]
    if (smsResult.status === 'fulfilled') smsNotifications.value = smsResult.value.data
    else loadIssues.value.push('SMS broadcasts')
  }
  updatedAt.value = formatDate(new Date())
})
</script>
