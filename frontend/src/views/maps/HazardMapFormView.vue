<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />
    <main class="p-6 max-w-2xl mx-auto">
      <h1 class="text-2xl font-bold text-slate-800 mb-6">
        {{ isEditMode ? 'Edit Hazard Map Reference' : 'New Hazard Map Reference' }}
      </h1>

      <form @submit.prevent="handleSubmit" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Map Title</label>
          <input
            v-model="form.map_title"
            type="text"
            required
            placeholder="e.g. Baclayon Flood Hazard Map"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Hazard Type</label>
            <select
              v-model="form.hazard_type"
              required
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="" disabled>Select</option>
              <option value="Flood">Flood</option>
              <option value="Storm Surge">Storm Surge</option>
              <option value="Landslide">Landslide</option>
              <option value="Earthquake">Earthquake</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Source</label>
            <input
              v-model="form.source"
              type="text"
              required
              placeholder="e.g. Project NOAH"
              class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Map URL</label>
          <input
            v-model="form.map_url"
            type="url"
            required
            placeholder="https://noah.up.edu.ph/..."
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Description (optional)</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>

        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>

        <div class="flex gap-3">
          <button
            type="submit"
            :disabled="isSaving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg px-4 py-2"
          >
            {{ isSaving ? 'Saving...' : isEditMode ? 'Save Changes' : 'Add Map Reference' }}
          </button>
          <router-link to="/hazard-maps" class="bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium rounded-lg px-4 py-2">
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
import * as mapsApi from '@/services/mapsApi'

const route = useRoute()
const router = useRouter()

const isEditMode = computed(() => !!route.params.id)
const isSaving = ref(false)
const errorMessage = ref('')

const form = reactive({
  map_title: '',
  hazard_type: '',
  source: '',
  map_url: '',
  description: '',
})

onMounted(async () => {
  if (isEditMode.value) {
    const response = await mapsApi.getHazardMap(route.params.id)
    Object.assign(form, {
      map_title: response.data.map_title,
      hazard_type: response.data.hazard_type,
      source: response.data.source,
      map_url: response.data.map_url,
      description: response.data.description || '',
    })
  }
})

async function handleSubmit() {
  isSaving.value = true
  errorMessage.value = ''
  try {
    if (isEditMode.value) {
      await mapsApi.updateHazardMap(route.params.id, form)
    } else {
      await mapsApi.createHazardMap(form)
    }
    router.push({ name: 'hazard-maps' })
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.entries(data)
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' | ')
      : 'Failed to save hazard map reference.'
  } finally {
    isSaving.value = false
  }
}
</script>