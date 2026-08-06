<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-100 px-4">
    <div class="w-full max-w-sm bg-white rounded-xl shadow-md p-8">
      <h1 class="text-2xl font-bold text-slate-800 mb-1">SAFE-ALERT</h1>
      <p class="text-sm text-slate-500 mb-6">Barangay Cambanac &amp; Poblacion, Baclayon</p>
 
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-slate-700 mb-1">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            autocomplete="username"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
 
        <div>
          <label for="password" class="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
 
        <p v-if="errorMessage" class="text-sm text-red-600">{{ errorMessage }}</p>
 
        <button
          type="submit"
          :disabled="isLoading"
          class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg py-2 transition-colors"
        >
          {{ isLoading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
    </div>
  </div>
</template>
 
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
 
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
 
const authStore = useAuthStore()
const router = useRouter()
 
async function handleLogin() {
  errorMessage.value = ''
  isLoading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (error) {
    if (error.response && error.response.data) {
      const data = error.response.data
      errorMessage.value =
        data.detail ||
        (data.non_field_errors && data.non_field_errors[0]) ||
        'Invalid username or password.'
    } else {
      errorMessage.value = 'Unable to reach the server. Please try again.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>