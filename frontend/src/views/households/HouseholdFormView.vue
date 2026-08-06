<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-slate-800 mb-6">
        {{ isEditMode ? 'Edit Household' : 'New Household' }}
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Household Number</label>
          <input
            v-model="form.household_number"
            type="text"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Head of Family</label>
          <input
            v-model="form.head_of_family"
            type="text"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Contact Number</label>
            <input
              v-model="form.contact_number"
              type="text"
              required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Purok</label>
            <input
              v-model="form.purok"
              type="text"
              required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Address</label>
          <textarea
            v-model="form.address"
            required
            rows="2"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Total Members</label>
          <input
            v-model.number="form.total_members"
            type="number"
            min="0"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="isSaving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg px-4 py-2"
          >
            {{ isSaving ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Household' }}
          </button>
          <router-link
            to="/households"
            class="bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-lg px-4 py-2"
          >
            Cancel
          </router-link>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppNavBar from '@/components/AppNavBar.vue'
import * as householdsApi from '@/services/householdsApi'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)
const isSaving = ref(false)
const errorMessage = ref('')

const form = reactive({
  household_number: '',
  head_of_family: '',
  contact_number: '',
  address: '',
  purok: '',
  total_members: 1,
})

onMounted(async () => {
  if (isEditMode.value) {
    const response = await householdsApi.getHousehold(route.params.id)
    Object.assign(form, {
      household_number: response.data.household_number,
      head_of_family: response.data.head_of_family,
      contact_number: response.data.contact_number,
      address: response.data.address,
      purok: response.data.purok,
      total_members: response.data.total_members,
    })
  }
})

async function handleSubmit() {
  isSaving.value = true
  errorMessage.value = ''
  try {
    if (isEditMode.value) {
      await householdsApi.updateHousehold(route.params.id, form)
      router.push({ name: 'household-detail', params: { id: route.params.id } })
    } else {
      const response = await householdsApi.createHousehold(form)
      router.push({ name: 'household-detail', params: { id: response.data.household_id } })
    }
  } catch (error) {
    const data = error.response?.data
    if (data) {
      errorMessage.value = Object.entries(data)
        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
        .join(' | ')
    } else {
      errorMessage.value = 'Failed to save household. Please try again.'
    }
  } finally {
    isSaving.value = false
  }
}
</script>