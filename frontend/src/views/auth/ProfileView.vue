<template>
  <div class="mx-auto max-w-2xl p-6">
    <div class="mb-6">
      <p class="text-sm text-slate-500">Account / Profile</p>
      <h1 class="mt-1 text-2xl font-bold text-slate-800">Profile Settings</h1>
    </div>
 
    <div v-if="isLoading" class="text-slate-500">Loading profile...</div>
 
    <form v-else @submit.prevent="handleSave" class="space-y-4 bg-white rounded-xl shadow-sm p-6">
      <div class="flex flex-wrap items-center gap-4 border-b border-slate-100 pb-5">
        <div class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full bg-blue-100 text-xl font-bold text-blue-700">
          <img v-if="avatarPreview" :src="avatarPreview" alt="Profile picture preview" class="h-full w-full object-cover" />
          <span v-else>{{ initials }}</span>
        </div>
        <div>
          <label for="avatar" class="inline-flex cursor-pointer rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50">
            Choose profile picture
          </label>
          <input id="avatar" type="file" accept="image/png,image/jpeg,image/webp" class="sr-only" @change="handleAvatarChange" />
          <p class="mt-1 text-xs text-slate-500">PNG, JPG, or WEBP. Maximum 5 MB.</p>
          <p v-if="avatarError" class="mt-1 text-xs text-red-600">{{ avatarError }}</p>
        </div>
      </div>

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
          <label class="block text-sm font-medium text-slate-700 mb-1">Current password <span class="text-red-600">*</span></label>
          <div class="relative">
            <input
              v-model="passwordForm.current_password"
              :type="showCurrentPassword ? 'text' : 'password'"
              required
              autocomplete="current-password"
              placeholder="Enter your current password"
              class="w-full rounded-lg border border-slate-300 py-2 pl-3 pr-11 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="button" class="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 hover:text-slate-600" :aria-label="showCurrentPassword ? 'Hide current password' : 'Show current password'" @click="showCurrentPassword = !showCurrentPassword">
              <svg v-if="showCurrentPassword" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.3 4.1 9.5 6-0.5.8-1.3 2-2.4 3.1M6.2 6.2C4.7 7.4 3.6 9 2.5 10c1.2 1.9 4.5 6 9.5 6 1.1 0 2.1-.2 3-.5" /></svg>
              <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M2.5 12S5.8 6 12 6s9.5 6 9.5 6-3.3 6-9.5 6S2.5 12 2.5 12Z" /><circle cx="12" cy="12" r="2.5" /></svg>
            </button>
          </div>
          <p class="mt-1 text-xs text-slate-500">Required to verify your identity before changing your password.</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">New Password</label>
          <div class="relative">
            <input
              v-model="passwordForm.new_password"
              :type="showNewPassword ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Enter a new password"
              class="w-full rounded-lg border border-slate-300 py-2 pl-3 pr-11 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="button" class="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 hover:text-slate-600" :aria-label="showNewPassword ? 'Hide new password' : 'Show new password'" @click="showNewPassword = !showNewPassword">
              <svg v-if="showNewPassword" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.3 4.1 9.5 6-0.5.8-1.3 2-2.4 3.1M6.2 6.2C4.7 7.4 3.6 9 2.5 10c1.2 1.9 4.5 6 9.5 6 1.1 0 2.1-.2 3-.5" /></svg>
              <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M2.5 12S5.8 6 12 6s9.5 6 9.5 6-3.3 6-9.5 6S2.5 12 2.5 12Z" /><circle cx="12" cy="12" r="2.5" /></svg>
            </button>
          </div>
          <div v-if="passwordForm.new_password" class="mt-3">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium text-slate-600">Password strength</span>
              <span :class="passwordStrength.textClass" class="font-semibold">{{ passwordStrength.label }}</span>
            </div>
            <div class="mt-1.5 flex gap-1" aria-hidden="true">
              <span v-for="level in 4" :key="level" :class="level <= passwordStrength.score ? passwordStrength.barClass : 'bg-slate-200'" class="h-1.5 flex-1 rounded-full" />
            </div>
            <p class="mt-2 text-xs text-slate-500">Use 12+ characters with uppercase, lowercase, a number, and a symbol.</p>
          </div>
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
    <ConfirmActionDialog
      v-if="showPasswordConfirm"
      title="Change password?"
      message="Your current password will be replaced. Use your new password the next time you sign in."
      confirm-label="Change password"
      title-id="password-change-confirmation"
      @cancel="showPasswordConfirm = false"
      @confirm="confirmPasswordChange"
    />
  </div>
</template>
 
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import * as authApi from '@/services/authApi'
import { useAuthStore } from '@/stores/auth'
import ConfirmActionDialog from '@/components/ConfirmActionDialog.vue'
 
const authStore = useAuthStore()
 
const isLoading = ref(true)
const isSaving = ref(false)
const isChangingPassword = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)
const passwordMessage = ref('')
const passwordSuccess = ref(false)
const avatarFile = ref(null)
const avatarPreview = ref('')
const avatarError = ref('')
const showPasswordConfirm = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
 
const profile = reactive({ role: '', status: '' })
const form = reactive({ first_name: '', last_name: '', email: '' })
const passwordForm = reactive({ current_password: '', new_password: '' })

const initials = computed(() => `${form.first_name?.[0] || ''}${form.last_name?.[0] || ''}`.toUpperCase() || 'U')
const passwordStrength = computed(() => {
  const password = passwordForm.new_password
  if (!password) return { score: 0, label: '', barClass: '', textClass: '' }
  const checks = [password.length >= 12, /[a-z]/.test(password), /[A-Z]/.test(password), /\d/.test(password), /[^A-Za-z0-9]/.test(password)]
  const score = checks.filter(Boolean).length <= 1 ? 1 : checks.filter(Boolean).length <= 2 ? 2 : checks.filter(Boolean).length <= 3 ? 3 : 4
  const levels = [
    { label: 'Weak', barClass: 'bg-red-500', textClass: 'text-red-600' },
    { label: 'Fair', barClass: 'bg-amber-500', textClass: 'text-amber-600' },
    { label: 'Good', barClass: 'bg-blue-500', textClass: 'text-blue-600' },
    { label: 'Strong', barClass: 'bg-emerald-500', textClass: 'text-emerald-600' },
  ]
  return { score, ...levels[score - 1] }
})
 
onMounted(async () => {
  try {
    const data = await authStore.fetchProfile()
    Object.assign(profile, data)
    form.first_name = data.first_name
    form.last_name = data.last_name
    form.email = data.email
    avatarPreview.value = data.avatar || ''
  } finally {
    isLoading.value = false
  }
})
 
async function handleSave() {
  isSaving.value = true
  saveMessage.value = ''
  try {
    const payload = new FormData()
    payload.append('first_name', form.first_name || '')
    payload.append('last_name', form.last_name || '')
    payload.append('email', form.email || '')
    if (avatarFile.value) payload.append('avatar', avatarFile.value)
    const response = await authApi.updateProfile(payload)
    avatarPreview.value = response.data.avatar || avatarPreview.value
    authStore.user = { ...authStore.user, ...response.data }
    localStorage.setItem('safe_alert_user', JSON.stringify(authStore.user))
    avatarFile.value = null
    saveSuccess.value = true
    saveMessage.value = 'Profile updated successfully.'
  } catch (error) {
    saveSuccess.value = false
    saveMessage.value = 'Failed to update profile. Please check your input.'
  } finally {
    isSaving.value = false
  }
}

function handleAvatarChange(event) {
  const [file] = event.target.files
  avatarError.value = ''
  if (!file) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 5 * 1024 * 1024) {
    avatarError.value = 'Choose a PNG, JPG, or WEBP image no larger than 5 MB.'
    event.target.value = ''
    return
  }
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}
 
async function handleChangePassword() {
  showPasswordConfirm.value = true
}

async function confirmPasswordChange() {
  showPasswordConfirm.value = false
  isChangingPassword.value = true
  passwordMessage.value = ''
  try {
    await authApi.changePassword(passwordForm.current_password, passwordForm.new_password)
    passwordSuccess.value = true
    passwordMessage.value = 'Password changed successfully.'
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    showCurrentPassword.value = false
    showNewPassword.value = false
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
