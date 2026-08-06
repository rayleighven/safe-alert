<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-4xl mx-auto">
      <h1 class="text-2xl font-bold text-slate-800 mb-6">Vulnerability Dashboard</h1>

      <div v-if="isLoading" class="text-slate-500">Loading...</div>

      <div v-else>
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="bg-white rounded-xl shadow-sm p-4">
            <p class="text-slate-500 text-sm">Total Households</p>
            <p class="text-2xl font-bold text-slate-800">{{ total }}</p>
          </div>
          <div class="bg-white rounded-xl shadow-sm p-4">
            <p class="text-slate-500 text-sm">High Priority</p>
            <p class="text-2xl font-bold text-red-600">{{ counts.High }}</p>
          </div>
          <div class="bg-white rounded-xl shadow-sm p-4">
            <p class="text-slate-500 text-sm">Medium Priority</p>
            <p class="text-2xl font-bold text-yellow-600">{{ counts.Medium }}</p>
          </div>
          <div class="bg-white rounded-xl shadow-sm p-4">
            <p class="text-slate-500 text-sm">Low Priority</p>
            <p class="text-2xl font-bold text-green-600">{{ counts.Low }}</p>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4">Priority Breakdown</h2>
          <div class="space-y-3">
            <div v-for="level in ['High', 'Medium', 'Low']" :key="level">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-slate-600">{{ level }}</span>
                <span class="text-slate-500">{{ counts[level] }} ({{ percentage(counts[level]) }}%)</span>
              </div>
              <div class="w-full bg-slate-100 rounded-full h-3">
                <div
                  :class="barColorClass(level)"
                  class="h-3 rounded-full transition-all"
                  :style="{ width: percentage(counts[level]) + '%' }"
                ></div>
              </div>
            </div>
          </div>
          <p v-if="counts.Unassessed > 0" class="text-slate-400 text-xs mt-4">
            {{ counts.Unassessed }} household(s) not yet assessed.
          </p>
        </div>

        <div class="bg-white rounded-xl shadow-sm p-6">
          <h2 class="text-lg font-semibold text-slate-800 mb-4">Highest Priority Households</h2>
          <table class="w-full text-sm">
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
                class="border-t border-slate-100 hover:bg-slate-50 cursor-pointer"
                @click="router.push({ name: 'household-detail', params: { id: household.household_id } })"
              >
                <td class="py-2 font-medium text-slate-800">{{ household.household_number }}</td>
                <td class="py-2">{{ household.head_of_family }}</td>
                <td class="py-2">{{ household.purok }}</td>
                <td class="py-2">
                  <span :class="priorityBadgeClass(household.evacuation_priority)" class="px-2 py-1 rounded-full text-xs font-medium">
                    {{ household.evacuation_priority }}
                  </span>
                </td>
                <td class="py-2">{{ household.priority_score }}%</td>
              </tr>
            </tbody>
          </table>
          <p v-if="topPriorityHouseholds.length === 0" class="text-slate-400 text-sm">No assessed households yet.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppNavBar from '@/components/AppNavBar.vue'
import * as householdsApi from '@/services/householdsApi'

const router = useRouter()
const households = ref([])
const isLoading = ref(true)

const total = computed(() => households.value.length)

const counts = computed(() => {
  const result = { High: 0, Medium: 0, Low: 0, Unassessed: 0 }
  households.value.forEach((h) => {
    if (h.evacuation_priority && result[h.evacuation_priority] !== undefined) {
      result[h.evacuation_priority]++
    } else {
      result.Unassessed++
    }
  })
  return result
})

const topPriorityHouseholds = computed(() => {
  return households.value
    .filter((h) => h.evacuation_priority)
    .sort((a, b) => (b.priority_score ?? 0) - (a.priority_score ?? 0))
    .slice(0, 10)
})

function percentage(count) {
  if (total.value === 0) return 0
  return Math.round((count / total.value) * 100)
}

function barColorClass(level) {
  if (level === 'High') return 'bg-red-500'
  if (level === 'Medium') return 'bg-yellow-500'
  return 'bg-green-500'
}

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

onMounted(async () => {
  const response = await householdsApi.listHouseholds()
  households.value = response.data
  isLoading.value = false
})
</script>