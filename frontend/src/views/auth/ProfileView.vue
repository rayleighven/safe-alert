<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-2xl font-bold text-slate-800 mb-6">Profile Settings</h1>
 
    <div v-if="isLoading" class="text-slate-500">Loading profile...</div>
 
    <form v-else @submit.prevent="handleSave" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">First Name</label>
          <input
            v-model="form.first_name"
            type="text"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
          <input
            v-model="form.last_name"
            type="text"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
 
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
        <input
          v-model="form.email"
          type="email"
          class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
 
      <div class="grid grid-cols-2 gap-4 text-sm text-slate-500">
        <div>
          <span class="block font-medium text-slate-700">Role</span>
          {{ profile.role }}
        </div>
        <div>
          <span class="block font-medium text-slate-700">Status</span>
          {{ profile.status }}
        </div>
      </div>
 
      <p v-if="saveMessage" :class="saveSuccess ? 'text-green-600' : 'text-red-600'" class="text-sm">
        {{ saveMessage }}
      </p>
 
      <button
        type="submit"
        :disabled="isSaving"
        class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium rounded-lg px-4 py-2 transition-colors"
      >
        {{ isSaving ? 'Saving...' : 'Save Changes' }}
      </button>
    </form>
 
    <div class="mt-8 bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-lg font-semibold text-slate-800 mb-4">Change Password</h2>
      <form @submit.prevent="handleChangePassword" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Current Password</label>
          <input
            v-model="passwordForm.current_password"
            type="password"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">New Password</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            required
            class="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
 
        <p v-if="passwordMessage" :class="passwordSuccess ? 'text-green-600' : 'text-red-600'" class="text-sm">
          {{ passwordMessage }}
        </p>
 
        <button
          type="submit"
          :disabled="isChangingPassword"
          class="bg-slate-700 hover:bg-slate-800 disabled:bg-slate-400 text-white font-medium rounded-lg px-4 py-2 transition-colors"
        >
          {{ isChangingPassword ? 'Updating...' : 'Change Password' }}
        </button>
      </form>
    </div>
  </div>
</template>
 
<script setup>
import { onMounted, reactive, ref } from 'vue'
import * as authApi from '@/services/authApi'
import { useAuthStore } from '@/stores/auth'
 
const authStore = useAuthStore()
 
const isLoading = ref(true)
const isSaving = ref(false)
const isChangingPassword = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)
const passwordMessage = ref('')
const passwordSuccess = ref(false)
 
const profile = reactive({ role: '', status: '' })
const form = reactive({ first_name: '', last_name: '', email: '' })
const passwordForm = reactive({ current_password: '', new_password: '' })
 
onMounted(async () => {
  try {
    const data = await authStore.fetchProfile()
    Object.assign(profile, data)
    form.first_name = data.first_name
    form.last_name = data.last_name
    form.email = data.email
  } finally {
    isLoading.value = false
  }
})
 
async function handleSave() {
  isSaving.value = true
  saveMessage.value = ''
  try {
    await authApi.updateProfile(form)
    saveSuccess.value = true
    saveMessage.value = 'Profile updated successfully.'
  } catch (error) {
    saveSuccess.value = false
    saveMessage.value = 'Failed to update profile. Please check your input.'
  } finally {
    isSaving.value = false
  }
}
 
async function handleChangePassword() {
  isChangingPassword.value = true
  passwordMessage.value = ''
  try {
    await authApi.changePassword(passwordForm.current_password, passwordForm.new_password)
    passwordSuccess.value = true
    passwordMessage.value = 'Password changed successfully.'
    passwordForm.current_password = ''
    passwordForm.new_password = ''
  } catch (error) {
    passwordSuccess.value = false
    passwordMessage.value =
      (error.response?.data?.current_password && error.response.data.current_password[0]) ||
      (error.response?.data?.new_password && error.response.data.new_password[0]) ||
      'Failed to change password.'
  } finally {
    isChangingPassword.value = false
  }
}
</script>