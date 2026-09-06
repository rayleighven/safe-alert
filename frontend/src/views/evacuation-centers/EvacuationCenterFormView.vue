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

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Evacuation Center Image</label>
          <div class="flex items-center gap-3">
            <label for="center-photo" class="inline-flex cursor-pointer rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50">
              Choose Image
            </label>
            <input id="center-photo" type="file" accept="image/png,image/jpeg,image/webp" class="sr-only" @change="handlePhotoChange" />
            <button v-if="photoFile" type="button" @click="handleRemovePhoto" class="text-sm text-red-600 hover:text-red-700">
              Remove
            </button>
          </div>
          <p class="mt-1 text-xs text-slate-500">PNG, JPG, or WEBP. Maximum 5 MB.</p>
          <p v-if="photoError" class="mt-1 text-xs text-red-600">{{ photoError }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Image URL</label>
          <input
            v-model="form.photo_url"
            type="url"
            placeholder="https://example.com/evacuation-center.jpg"
            :disabled="!!photoFile"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100 disabled:text-slate-400"
            @input="handlePhotoUrlInput"
          />
          <p v-if="photoFile" class="mt-1 text-xs text-slate-500">An uploaded image takes priority — remove it above to use a URL instead.</p>
        </div>

        <div v-if="photoPreview" class="rounded-lg border border-slate-200 p-3">
          <p class="mb-2 text-xs font-medium text-slate-500">Image Preview</p>
          <img :src="photoPreview" alt="Evacuation center preview" class="h-40 w-full rounded-lg object-cover" @error="handlePreviewError" />
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
const photoFile = ref(null)
const photoPreview = ref('')
const photoError = ref('')

const form = reactive({
  name: '',
  address: '',
  capacity: 0,
  current_occupancy: 0,
  status: 'Active',
  contact_person: '',
  contact_number: '',
  photo_url: '',
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
      photo_url: response.data.photo_url || '',
    })
    photoPreview.value = response.data.photo || response.data.photo_url || ''
  }
})

function handlePhotoChange(event) {
  const [file] = event.target.files
  photoError.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
    photoError.value = 'Choose a PNG, JPG, or WEBP image no larger than 5 MB.'
    event.target.value = ''
    return
  }
  photoFile.value = file
  photoPreview.value = URL.createObjectURL(file)
}

function handleRemovePhoto() {
  photoFile.value = null
  photoError.value = ''
  photoPreview.value = form.photo_url || ''
}

function handlePhotoUrlInput() {
  if (photoFile.value) return // an uploaded file takes priority; ignore URL-driven preview changes
  photoPreview.value = form.photo_url || ''
}

function handlePreviewError() {
  // An unreachable/invalid image URL shouldn't block submission — just drop
  // the broken preview. Doesn't touch form.photo_url, so the value the user
  // typed is still submitted and validated server-side.
  if (!photoFile.value) {
    photoPreview.value = ''
  }
}

async function handleSubmit() {
  isSaving.value = true
  errorMessage.value = ''
  try {
    let payload = form
    if (photoFile.value) {
      payload = new FormData()
      Object.entries(form).forEach(([key, value]) => {
        if (key === 'photo_url') return // uploaded file takes priority; don't send both
        payload.append(key, value ?? '')
      })
      payload.append('photo', photoFile.value)
    }

    if (isEditMode.value) {
      await evacuationCentersApi.updateCenter(route.params.id, payload)
      router.push({ name: 'evacuation-center-detail', params: { id: route.params.id } })
    } else {
      const response = await evacuationCentersApi.createCenter(payload)
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