<template>
  <div class="mx-auto max-w-6xl p-6">
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm text-slate-500">Administration / Accounts</p>
        <h1 class="mt-1 text-2xl font-bold text-slate-800">Barangay accounts</h1>
        <p class="mt-1 text-sm text-slate-500">Accounts registered under {{ barangayName }}.</p>
      </div>
      <div class="flex w-full flex-wrap gap-3 sm:w-auto sm:flex-nowrap">
        <label class="relative block min-w-0 flex-1 sm:w-72">
          <span class="sr-only">Search accounts</span>
          <input v-model="search" type="search" placeholder="Search name or username..." class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100" />
        </label>
        <button type="button" class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-700" @click="showCreateForm = !showCreateForm">
          {{ showCreateForm ? 'Close form' : 'Add account' }}
        </button>
      </div>
    </div>

    <form v-if="showCreateForm" class="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" @submit.prevent="handleCreateAccount">
      <div class="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 class="text-lg font-bold text-slate-800">Add barangay account</h2>
          <p class="mt-1 text-sm text-slate-500">The account will automatically be assigned to {{ barangayName }}.</p>
        </div>
      </div>
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Username</label>
          <input v-model.trim="newAccount.username" required autocomplete="off" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Temporary password</label>
          <input v-model="newAccount.password" type="password" required autocomplete="new-password" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">First name</label>
          <input v-model.trim="newAccount.first_name" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Last name</label>
          <input v-model.trim="newAccount.last_name" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Email</label>
          <input v-model.trim="newAccount.email" type="email" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Role</label>
          <select v-model="newAccount.role" required class="form-input">
            <option v-for="role in staffRoles" :key="role" :value="role">{{ role }}</option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Assigned purok <span class="font-normal text-slate-400">(optional)</span></label>
          <input v-model.trim="newAccount.assigned_purok" class="form-input" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Initial status</label>
          <select v-model="newAccount.status" class="form-input">
            <option>Active</option>
            <option>Inactive</option>
          </select>
        </div>
      </div>
      <p v-if="createError" class="mt-4 text-sm text-red-600">{{ createError }}</p>
      <div class="mt-5 flex gap-3">
        <button type="submit" :disabled="isCreating" class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300">
          {{ isCreating ? 'Creating...' : 'Create account' }}
        </button>
        <button type="button" class="rounded-lg bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-200" @click="showCreateForm = false">Cancel</button>
      </div>
    </form>

    <div v-if="isLoading" class="rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm">Loading accounts...</div>
    <div v-else-if="errorMessage" class="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ errorMessage }}</div>
    <div v-else class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[700px] text-left text-sm">
          <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th class="px-5 py-3">Account</th>
              <th class="px-5 py-3">Role</th>
              <th class="px-5 py-3">Assigned purok</th>
              <th class="px-5 py-3">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="account in filteredAccounts" :key="account.user_id" class="hover:bg-slate-50">
              <td class="px-5 py-4">
                <div class="flex items-center gap-3">
                  <div class="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-blue-100 text-xs font-bold text-blue-700">
                    <img v-if="account.avatar" :src="account.avatar" alt="" class="h-full w-full object-cover" />
                    <span v-else>{{ initials(account) }}</span>
                  </div>
                  <div>
                    <p class="font-semibold text-slate-800">{{ account.first_name || account.last_name ? `${account.first_name} ${account.last_name}`.trim() : account.username }}</p>
                    <p class="text-xs text-slate-500">@{{ account.username }}<span v-if="account.email"> · {{ account.email }}</span></p>
                  </div>
                </div>
              </td>
              <td class="px-5 py-4 text-slate-700">{{ account.role }}</td>
              <td class="px-5 py-4 text-slate-600">{{ account.assigned_purok || '—' }}</td>
              <td class="px-5 py-4">
                <label class="sr-only" :for="`status-${account.user_id}`">Account status for {{ account.username }}</label>
                <select
                  :id="`status-${account.user_id}`"
                  :value="account.status"
                  :disabled="savingStatusId === account.user_id"
                  :class="statusClass(account.status)"
                  class="rounded-full border-0 px-2.5 py-1 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:cursor-wait"
                  @change="handleStatusChange(account, $event)"
                >
                  <option>Active</option>
                  <option>Inactive</option>
                </select>
              </td>
            </tr>
            <tr v-if="filteredAccounts.length === 0">
              <td colspan="4" class="px-5 py-10 text-center text-slate-500">No matching accounts found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import * as authApi from '@/services/authApi'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const accounts = ref([])
const search = ref('')
const isLoading = ref(true)
const errorMessage = ref('')
const showCreateForm = ref(false)
const isCreating = ref(false)
const createError = ref('')
const savingStatusId = ref(null)
const barangayName = computed(() => authStore.user?.barangay_name || 'your barangay')
const staffRoles = ['Barangay Secretary', 'BDRRMC Chairperson', 'Barangay Kagawad/Tanod', 'Barangay Healthworker']
const newAccount = reactive({
  username: '', password: '', first_name: '', last_name: '', email: '',
  role: 'Barangay Kagawad/Tanod', assigned_purok: '', status: 'Active',
})
const filteredAccounts = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return accounts.value
  return accounts.value.filter((account) => [account.username, account.first_name, account.last_name, account.email, account.role]
    .some((value) => value?.toLowerCase().includes(term)))
})

onMounted(async () => {
  try {
    const response = await authApi.listBarangayAccounts()
    accounts.value = response.data
  } catch {
    errorMessage.value = 'Unable to load barangay accounts.'
  } finally {
    isLoading.value = false
  }
})

function initials(account) {
  return `${account.first_name?.[0] || ''}${account.last_name?.[0] || ''}`.toUpperCase() || account.username.slice(0, 2).toUpperCase()
}

function statusClass(status) {
  return status === 'Active' ? 'bg-emerald-100 text-emerald-700' : status === 'Archived' ? 'bg-slate-200 text-slate-600' : 'bg-amber-100 text-amber-700'
}

async function handleCreateAccount() {
  isCreating.value = true
  createError.value = ''
  try {
    const response = await authApi.createBarangayAccount({ ...newAccount })
    accounts.value.push(response.data)
    Object.assign(newAccount, {
      username: '', password: '', first_name: '', last_name: '', email: '',
      role: 'Barangay Kagawad/Tanod', assigned_purok: '', status: 'Active',
    })
    showCreateForm.value = false
  } catch (error) {
    const data = error.response?.data
    createError.value = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Unable to create the account.'
  } finally {
    isCreating.value = false
  }
}

async function handleStatusChange(account, event) {
  const status = event.target.value
  if (status === account.status) return
  savingStatusId.value = account.user_id
  try {
    const response = await authApi.updateBarangayAccount(account.user_id, { status })
    Object.assign(account, response.data)
  } catch (error) {
    event.target.value = account.status
    errorMessage.value = error.response?.data?.status?.[0] || 'Unable to update the account status.'
  } finally {
    savingStatusId.value = null
  }
}
</script>

<style scoped>
.form-input {
  @apply w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-800 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100;
}
</style>
