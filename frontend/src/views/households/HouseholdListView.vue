<template>
  <div class="space-y-6 pb-6">
    <!-- Header with Breadcrumb and Actions -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Household Records</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Household Records</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            Registered household records, CART vulnerability profiles, and evacuation prioritization.
          </p>
        </div>
        <router-link
          v-if="isSecretary"
          to="/households/new"
          class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          <span>New Household</span>
        </router-link>
      </div>
    </header>

    <!-- Filters & Search Toolbar -->
    <div class="flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200/80 bg-white p-3.5 shadow-card sm:p-4">
      <div class="relative min-w-0 flex-1">
        <label for="household-search" class="sr-only">Search households</label>
        <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400" aria-hidden="true">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
        </span>
        <input
          id="household-search"
          v-model="searchQuery"
          type="search"
          placeholder="Search by household # or head of family..."
          class="w-full rounded-xl border border-slate-200 bg-slate-50/60 py-2 pl-9 pr-3 text-xs sm:text-sm font-medium text-slate-800 placeholder:text-slate-400 transition-colors focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
      </div>

      <div class="flex items-center gap-2">
        <label for="priority-filter-select" class="sr-only">Filter by Priority</label>
        <select
          id="priority-filter-select"
          v-model="priorityFilter"
          class="rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 py-2 text-xs sm:text-sm font-semibold text-slate-700 transition-colors focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-100"
        >
          <option value="">All Priorities</option>
          <option value="High">High Priority</option>
          <option value="Medium">Medium Priority</option>
          <option value="Low">Low Priority</option>
        </select>
        <button
          v-if="searchQuery || priorityFilter"
          type="button"
          class="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
          @click="resetFilters"
        >
          Reset
        </button>
      </div>
    </div>

    <!-- Data State: Loading, Empty, or Table -->
    <div v-if="isLoading" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="inline-flex h-10 w-10 animate-spin items-center justify-center rounded-full border-2 border-blue-600 border-t-transparent text-blue-600" />
      <p class="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-400">Loading household records...</p>
    </div>

    <div v-else-if="filteredHouseholds.length === 0" class="rounded-2xl border border-slate-200/80 bg-white p-12 text-center shadow-card">
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16 20v-1a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v1m7-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm11 9v-1a4 4 0 0 0-3-3.87m-1-12a4 4 0 0 1 0 7.75" />
        </svg>
      </div>
      <h3 class="mt-4 text-sm font-bold text-slate-800">No households found</h3>
      <p class="mt-1 text-xs text-slate-500">
        {{ searchQuery || priorityFilter ? 'Try clearing your filters or search keywords.' : 'No household records have been registered yet.' }}
      </p>
      <button
        v-if="searchQuery || priorityFilter"
        type="button"
        class="mt-4 inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
        @click="resetFilters"
      >
        Clear filters
      </button>
    </div>

    <div v-else class="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-card">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs sm:text-sm">
          <thead class="border-b border-slate-200/70 bg-slate-50/80 text-[11px] font-bold uppercase tracking-wider text-slate-500">
            <tr>
              <th scope="col" class="py-3 px-4">Household #</th>
              <th scope="col" class="py-3 px-4">Head of Family</th>
              <th scope="col" class="py-3 px-4">Purok</th>
              <th scope="col" class="py-3 px-4 text-center">Members</th>
              <th scope="col" class="py-3 px-4">Priority</th>
              <th scope="col" class="py-3 px-4 text-right">Score</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="household in filteredHouseholds"
              :key="household.household_id"
              class="cursor-pointer transition-colors hover:bg-blue-50/40 focus:bg-blue-50/50"
              tabindex="0"
              @click="goToDetail(household.household_id)"
              @keydown.enter="goToDetail(household.household_id)"
            >
              <td class="py-3.5 px-4 font-bold text-slate-800">{{ household.household_number }}</td>
              <td class="py-3.5 px-4 font-medium text-slate-700">{{ household.head_of_family }}</td>
              <td class="py-3.5 px-4 text-slate-600">{{ household.purok }}</td>
              <td class="py-3.5 px-4 text-center tabular-nums font-semibold text-slate-700">{{ household.total_members }}</td>
              <td class="py-3.5 px-4">
                <span
                  v-if="household.evacuation_priority"
                  :class="priorityBadgeClass(household.evacuation_priority)"
                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold"
                >
                  {{ household.evacuation_priority }}
                </span>
                <span v-else class="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-400">
                  Not assessed
                </span>
              </td>
              <td class="py-3.5 px-4 text-right tabular-nums font-bold text-slate-800">
                {{ household.priority_score !== null && household.priority_score !== undefined ? household.priority_score + '%' : '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="border-t border-slate-100 px-4 py-3 text-right text-xs font-medium text-slate-500">
        Showing {{ filteredHouseholds.length }} of {{ households.length }} registered households
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as householdsApi from '@/services/householdsApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const households = ref([])
const isLoading = ref(true)
const searchQuery = ref(typeof route.query.q === 'string' ? route.query.q : '')
const priorityFilter = ref('')

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

const filteredHouseholds = computed(() => {
  return households.value.filter((h) => {
    const query = searchQuery.value.toLowerCase().trim()
    const matchesSearch =
      !query ||
      (h.household_number && h.household_number.toLowerCase().includes(query)) ||
      (h.head_of_family && h.head_of_family.toLowerCase().includes(query)) ||
      (h.purok && h.purok.toLowerCase().includes(query))
    const matchesPriority = !priorityFilter.value || h.evacuation_priority === priorityFilter.value
    return matchesSearch && matchesPriority
  })
})

function resetFilters() {
  searchQuery.value = ''
  priorityFilter.value = ''
}

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-amber-100 text-amber-800'
  return 'bg-emerald-100 text-emerald-700'
}

function goToDetail(householdId) {
  router.push({ name: 'household-detail', params: { id: householdId } })
}

onMounted(async () => {
  try {
    const response = await householdsApi.listHouseholds()
    households.value = response.data
  } finally {
    isLoading.value = false
  }
})
</script>