<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-slate-800">Households</h1>
        <router-link
          v-if="isSecretary"
          to="/households/new"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-4 py-2"
        >
          + New Household
        </router-link>
      </div>

      <div class="flex gap-4 mb-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by household # or head of family..."
          class="flex-1 rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          v-model="priorityFilter"
          class="rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Priorities</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>

      <div v-if="isLoading" class="text-slate-500">Loading households...</div>
      <div v-else-if="filteredHouseholds.length === 0" class="text-slate-500">No households found.</div>

      <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-slate-100 text-slate-600 text-left">
            <tr>
              <th class="px-4 py-3">Household #</th>
              <th class="px-4 py-3">Head of Family</th>
              <th class="px-4 py-3">Purok</th>
              <th class="px-4 py-3">Members</th>
              <th class="px-4 py-3">Priority</th>
              <th class="px-4 py-3">Score</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="household in filteredHouseholds"
              :key="household.household_id"
              class="border-t border-slate-100 hover:bg-slate-50 cursor-pointer"
              @click="goToDetail(household.household_id)"
            >
              <td class="px-4 py-3 font-medium text-slate-800">{{ household.household_number }}</td>
              <td class="px-4 py-3">{{ household.head_of_family }}</td>
              <td class="px-4 py-3">{{ household.purok }}</td>
              <td class="px-4 py-3">{{ household.total_members }}</td>
              <td class="px-4 py-3">
                <span
                  v-if="household.evacuation_priority"
                  :class="priorityBadgeClass(household.evacuation_priority)"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ household.evacuation_priority }}
                </span>
                <span v-else class="text-slate-400 text-xs">Not assessed</span>
              </td>
              <td class="px-4 py-3">{{ household.priority_score !== null && household.priority_score !== undefined ? household.priority_score + '%' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as householdsApi from '@/services/householdsApi'

const router = useRouter()
const authStore = useAuthStore()

const households = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const priorityFilter = ref('')

const isSecretary = computed(() => authStore.user?.role === 'Barangay Secretary')

const filteredHouseholds = computed(() => {
  return households.value.filter((h) => {
    const query = searchQuery.value.toLowerCase()
    const matchesSearch =
      !query ||
      h.household_number.toLowerCase().includes(query) ||
      h.head_of_family.toLowerCase().includes(query)
    const matchesPriority = !priorityFilter.value || h.evacuation_priority === priorityFilter.value
    return matchesSearch && matchesPriority
  })
})

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
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