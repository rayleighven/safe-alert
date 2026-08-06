<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-slate-800 mb-6">
        {{ isEditMode ? 'Edit Evacuation Center' : 'New Evacuation Center' }}
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Name</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
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

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Capacity</label>
            <input
              v-model.number="form.capacity"
              type="number"
              min="0"
              required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Current Occupancy</label>
            <input
              v-model.number="form.current_occupancy"
              type="number"
              min="0"
              required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Status</label>
          <select
            v-model="form.status"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
            <option value="Under Maintenance">Under Maintenance</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Contact Person</label>
            <input
              v-model="form.contact_person"
              type="text"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Contact Number</label>
            <input
              v-model="form.contact_number"
              type="text"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="isSaving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg px-4 py-2"
          >
            {{ isSaving ? 'Saving...' : isEditMode ? 'Save Changes' : 'Create Center' }}
          </button>
          <router-link
            to="/evacuation-centers"
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
import * as evacuationCentersApi from '@/services/evacuationCentersApi'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)
const isSaving = ref(false)
const errorMessage = ref('')

const form = reactive({
  name: '',
  address: '',
  capacity: 0,
  current_occupancy: 0,
  status: 'Active',
  contact_person: '',
  contact_number: '',
})

onMounted(async () => {
  if (isEditMode.value) {
    const response = await evacuationCentersApi.getCenter(route.params.id)
    Object.assign(form, {
      name: response.data.name,
      address: response.data.address,
      capacity: response.data.capacity,
      current_occupancy: response.data.current_occupancy,
      status: response.data.status,
      contact_person: response.data.contact_person || '',
      contact_number: response.data.contact_number || '',
    })
  }
})

async function handleSubmit() {
  isSaving.value = true
  errorMessage.value = ''
  try {
    if (isEditMode.value) {
      await evacuationCentersApi.updateCenter(route.params.id, form)
      router.push({ name: 'evacuation-center-detail', params: { id: route.params.id } })
    } else {
      const response = await evacuationCentersApi.createCenter(form)
      router.push({ name: 'evacuation-center-detail', params: { id: response.data.center_id } })
    }
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.entries(data)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ')
      : 'Failed to save evacuation center.'
  } finally {
    isSaving.value = false
  }
}
</script>