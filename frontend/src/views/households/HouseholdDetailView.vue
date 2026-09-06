<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavBar />

    <main v-if="!isLoading && household" class="p-6 max-w-4xl mx-auto">
      <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div>
          <h1 class="text-2xl font-bold text-slate-800">{{ household.household_number }}</h1>
          <p class="text-slate-500">{{ household.head_of_family }} • Purok {{ household.purok }}</p>
        </div>
        <div class="flex items-center gap-3">
          <span
            v-if="household.evacuation_priority"
            :class="priorityBadgeClass(household.evacuation_priority)"
            class="px-3 py-1 rounded-full text-sm font-medium"
          >
            {{ household.evacuation_priority }} Priority ({{ household.priority_score }}%)
          </span>
          <span v-else class="text-slate-400 text-sm">Not yet assessed</span>
          <router-link
            v-if="isSecretary"
            :to="{ name: 'household-edit', params: { id: household.household_id } }"
            class="bg-slate-200 hover:bg-slate-300 text-slate-700 text-sm font-medium rounded-lg px-3 py-2"
          >
            Edit
          </router-link>
          <button
            v-if="isSecretary"
            @click="handleArchive"
            class="bg-red-100 hover:bg-red-200 text-red-700 text-sm font-medium rounded-lg px-3 py-2"
          >
            Archive
          </button>
        </div>
      </div>

      <!-- Household Info -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6 grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-slate-500">Contact Number</span>
          <p class="text-slate-800">{{ household.contact_number }}</p>
        </div>
        <div>
          <span class="text-slate-500">Total Members</span>
          <p class="text-slate-800">{{ household.total_members }}</p>
        </div>
        <div class="col-span-2">
          <span class="text-slate-500">Address</span>
          <p class="text-slate-800">{{ household.address }}</p>
        </div>
      </div>

      <!-- Resident Account -->
      <div v-if="isSecretary" class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Resident Account</h2>

        <div v-if="household.resident_account" class="text-sm text-slate-700">
          Linked to <span class="font-medium">{{ household.resident_account.username }}</span>
          ({{ household.resident_account.status }})
        </div>

        <div v-else>
          <p class="text-slate-500 text-sm mb-4">
            No Resident account is linked yet. Residents don't self-register — create the account here,
            tied to this household.
          </p>
          <button
            v-if="!showResidentForm"
            @click="showResidentForm = true"
            class="text-sm text-blue-600 hover:text-blue-700"
          >
            + Create Resident Account
          </button>

          <form v-else @submit.prevent="handleCreateResident" class="grid grid-cols-2 gap-3 p-4 bg-slate-50 rounded-lg">
            <input v-model="residentForm.username" type="text" placeholder="Username" required class="rounded-lg border border-slate-300 px-3 py-2" />
            <input v-model="residentForm.email" type="email" placeholder="Email (optional)" class="rounded-lg border border-slate-300 px-3 py-2" />
            <input v-model="residentForm.first_name" type="text" placeholder="First Name" class="rounded-lg border border-slate-300 px-3 py-2" />
            <input v-model="residentForm.last_name" type="text" placeholder="Last Name" class="rounded-lg border border-slate-300 px-3 py-2" />
            <input v-model="residentForm.password" type="password" placeholder="Password" required class="col-span-2 rounded-lg border border-slate-300 px-3 py-2" />

            <p v-if="residentFormError" class="col-span-2 text-sm text-red-600">{{ residentFormError }}</p>

            <div class="col-span-2 flex gap-3">
              <button type="submit" :disabled="isSavingResident" class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg px-4 py-2 text-sm">
                {{ isSavingResident ? 'Creating...' : 'Create Account' }}
              </button>
              <button type="button" @click="showResidentForm = false" class="bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg px-4 py-2 text-sm">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Household Members -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-slate-800">Household Members</h2>
          <button v-if="isSecretary" @click="toggleMemberForm" class="text-sm text-blue-600 hover:text-blue-700">
            {{ showMemberForm ? 'Cancel' : '+ Add Member' }}
          </button>
        </div>

        <form
          v-if="showMemberForm"
          @submit.prevent="handleSaveMember"
          class="grid grid-cols-2 gap-3 mb-4 p-4 bg-slate-50 rounded-lg"
        >
          <input v-model="memberForm.full_name" type="text" placeholder="Full Name" required class="rounded-lg border border-slate-300 px-3 py-2" />
          <input v-model="memberForm.birth_date" type="date" @change="handleBirthDateChange" class="rounded-lg border border-slate-300 px-3 py-2" />
          <input v-model.number="memberForm.age" type="number" min="0" placeholder="Age" required class="rounded-lg border border-slate-300 px-3 py-2" />
          <select v-model="memberForm.sex" required class="rounded-lg border border-slate-300 px-3 py-2">
            <option value="" disabled>Sex</option>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
          </select>
          <input v-model="memberForm.relationship" type="text" placeholder="Relationship to head" required class="rounded-lg border border-slate-300 px-3 py-2" />
          <input v-model="memberForm.occupation" type="text" placeholder="Occupation (optional)" class="rounded-lg border border-slate-300 px-3 py-2" />
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="memberForm.is_senior_citizen" /> Senior Citizen</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="memberForm.is_pwd" /> PWD</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="memberForm.is_pregnant" /> Pregnant</label>
          <label class="flex items-center gap-2 text-sm"><input type="checkbox" v-model="memberForm.is_child" /> Child</label>
          <div class="col-span-2 flex gap-3">
            <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 text-sm">
              {{ editingMemberId ? 'Update Member' : 'Save Member' }}
            </button>
            <button v-if="editingMemberId" type="button" @click="cancelMemberForm" class="bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg px-4 py-2 text-sm">
              Cancel Edit
            </button>
          </div>
        </form>

        <table class="w-full text-sm">
          <thead class="text-left text-slate-500">
            <tr>
              <th class="py-2">Name</th>
              <th class="py-2">Birthdate</th>
              <th class="py-2">Age</th>
              <th class="py-2">Sex</th>
              <th class="py-2">Relationship</th>
              <th class="py-2">Occupation</th>
              <th class="py-2">Flags</th>
              <th v-if="isSecretary" class="py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="member in activeMembers" :key="member.member_id" class="border-t border-slate-100">
              <td class="py-2">{{ member.full_name }}</td>
              <td class="py-2">{{ member.birth_date || '—' }}</td>
              <td class="py-2">{{ member.age }}</td>
              <td class="py-2">{{ member.sex }}</td>
              <td class="py-2">{{ member.relationship }}</td>
              <td class="py-2">{{ member.occupation || '—' }}</td>
              <td class="py-2 text-xs text-slate-500">
                <span v-if="member.is_senior_citizen">Senior </span>
                <span v-if="member.is_pwd">PWD </span>
                <span v-if="member.is_pregnant">Pregnant </span>
                <span v-if="member.is_child">Child</span>
              </td>
              <td v-if="isSecretary" class="py-2 whitespace-nowrap">
                <button type="button" @click="startEditMember(member)" class="text-blue-600 hover:text-blue-700 mr-3">Edit</button>
                <button type="button" @click="handleArchiveMember(member)" class="text-red-600 hover:text-red-700">Archive</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="activeMembers.length === 0" class="text-slate-400 text-sm">No members recorded yet.</p>
      </div>

      <!-- Vulnerability Assessment -->
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h2 class="text-lg font-semibold text-slate-800 mb-4">Vulnerability Assessment</h2>

        <!-- No assessment exists yet -->
        <div v-if="!latestIndicator">
          <p v-if="canCreateAssessment" class="text-slate-500 text-sm mb-4">
            No field assessment yet. Fill in the hazard and structural details below to create one.
          </p>
          <p v-else class="text-slate-400 text-sm">
            No field assessment yet. Waiting on a Barangay Kagawad/Tanod to complete the initial hazard and structural assessment.
          </p>

          <form v-if="canCreateAssessment" @submit.prevent="handleCreateAssessment" class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">House Material</label>
                <select v-model="assessmentForm.house_material" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
                  <option value="" disabled>Select</option>
                  <option value="Concrete">Concrete</option>
                  <option value="Mixed">Mixed</option>
                  <option value="Light">Light</option>
                  <option value="Salvaged">Salvaged</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-slate-700 mb-1">Roof Material</label>
                <select v-model="assessmentForm.roof_material" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
                  <option value="" disabled>Select</option>
                  <option value="Concrete">Concrete</option>
                  <option value="Mixed">Mixed</option>
                  <option value="GI Sheet">GI Sheet</option>
                  <option value="Cogon">Cogon</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Hazard Types (select all that apply)</label>
              <div class="grid grid-cols-4 gap-3 text-sm">
                <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.flood_prone" /> Flood-prone</label>
                <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.storm_surge_prone" /> Storm surge-prone</label>
                <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.landslide_prone" /> Landslide-prone</label>
                <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.coastal_zone" /> Coastal zone</label>
              </div>
            </div>

            <div class="rounded-lg bg-slate-50 p-3">
              <p class="text-sm font-medium text-slate-700 mb-2">Vulnerable members (from Household Members list)</p>
              <div class="grid grid-cols-4 gap-3 text-sm text-slate-600">
                <span>Senior citizen: <strong>{{ memberDerivedFlags.has_senior_citizen ? 'Yes' : 'No' }}</strong></span>
                <span>PWD: <strong>{{ memberDerivedFlags.has_pwd ? 'Yes' : 'No' }}</strong></span>
                <span>Pregnant: <strong>{{ memberDerivedFlags.has_pregnant_member ? 'Yes' : 'No' }}</strong></span>
                <span>Child: <strong>{{ memberDerivedFlags.has_child ? 'Yes' : 'No' }}</strong></span>
              </div>
            </div>

            <button
              type="submit"
              :disabled="isSavingAssessment"
              class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg px-4 py-2 text-sm"
            >
              {{ isSavingAssessment ? 'Saving...' : 'Save Assessment' }}
            </button>
          </form>
        </div>

        <!-- Assessment exists — Secretary/Kagawad full edit -->
        <form v-else-if="canEditFullAssessment" @submit.prevent="handleUpdateAssessment" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">House Material</label>
              <select v-model="assessmentForm.house_material" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
                <option value="Concrete">Concrete</option>
                <option value="Mixed">Mixed</option>
                <option value="Light">Light</option>
                <option value="Salvaged">Salvaged</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1">Roof Material</label>
              <select v-model="assessmentForm.roof_material" required class="w-full rounded-lg border border-slate-300 px-3 py-2">
                <option value="Concrete">Concrete</option>
                <option value="Mixed">Mixed</option>
                <option value="GI Sheet">GI Sheet</option>
                <option value="Cogon">Cogon</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Hazard Zone (select all that apply)</label>
            <div class="grid grid-cols-4 gap-3 text-sm">
              <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.flood_prone" /> Flood-prone</label>
              <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.storm_surge_prone" /> Storm surge-prone</label>
              <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.landslide_prone" /> Landslide-prone</label>
              <label class="flex items-center gap-2"><input type="checkbox" v-model="assessmentForm.coastal_zone" /> Coastal zone</label>
            </div>
            <p class="mt-2 text-xs text-slate-500">
              Calculated Hazard Zone: <span class="font-semibold text-slate-700">{{ latestIndicator.hazard_zone }}</span>
              — derived automatically from the hazard types selected above, recalculated on save.
            </p>
          </div>

          <div class="rounded-lg bg-slate-50 p-3">
            <p class="text-sm font-medium text-slate-700 mb-2">Vulnerable members (from Household Members list)</p>
            <div class="grid grid-cols-4 gap-3 text-sm text-slate-600">
              <span>Senior citizen: <strong>{{ memberDerivedFlags.has_senior_citizen ? 'Yes' : 'No' }}</strong></span>
              <span>PWD: <strong>{{ memberDerivedFlags.has_pwd ? 'Yes' : 'No' }}</strong></span>
              <span>Pregnant: <strong>{{ memberDerivedFlags.has_pregnant_member ? 'Yes' : 'No' }}</strong></span>
              <span>Child: <strong>{{ memberDerivedFlags.has_child ? 'Yes' : 'No' }}</strong></span>
            </div>
          </div>

          <button
            type="submit"
            :disabled="isSavingAssessment"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg px-4 py-2 text-sm"
          >
            {{ isSavingAssessment ? 'Saving...' : 'Update Assessment' }}
          </button>
        </form>

        <!-- Assessment exists — BHW view (health fields are derived from Household Members, nothing left to edit here) -->
        <div v-else-if="canEditHealthFields" class="space-y-3">
          <p class="text-slate-500 text-sm">
            Health-related indicators are derived automatically from the Household Members list above.
            Structural and hazard details are managed by the Barangay Kagawad/Tanod.
          </p>
          <div class="rounded-lg bg-slate-50 p-3">
            <div class="grid grid-cols-4 gap-3 text-sm text-slate-600">
              <span>Senior citizen: <strong>{{ memberDerivedFlags.has_senior_citizen ? 'Yes' : 'No' }}</strong></span>
              <span>PWD: <strong>{{ memberDerivedFlags.has_pwd ? 'Yes' : 'No' }}</strong></span>
              <span>Pregnant: <strong>{{ memberDerivedFlags.has_pregnant_member ? 'Yes' : 'No' }}</strong></span>
              <span>Child: <strong>{{ memberDerivedFlags.has_child ? 'Yes' : 'No' }}</strong></span>
            </div>
          </div>
        </div>

        <!-- Read-only (MDRRMO) -->
        <div v-else class="grid grid-cols-2 gap-3 text-sm text-slate-700">
          <div>House Material: {{ latestIndicator.house_material }}</div>
          <div>Roof Material: {{ latestIndicator.roof_material }}</div>
          <div>Hazard Zone: {{ latestIndicator.hazard_zone }}</div>
          <div>Flood-prone: {{ latestIndicator.flood_prone ? 'Yes' : 'No' }}</div>
          <div>Storm surge-prone: {{ latestIndicator.storm_surge_prone ? 'Yes' : 'No' }}</div>
          <div>Landslide-prone: {{ latestIndicator.landslide_prone ? 'Yes' : 'No' }}</div>
          <div>Coastal zone: {{ latestIndicator.coastal_zone ? 'Yes' : 'No' }}</div>
          <div>Has senior citizen: {{ latestIndicator.has_senior_citizen ? 'Yes' : 'No' }}</div>
          <div>Has PWD: {{ latestIndicator.has_pwd ? 'Yes' : 'No' }}</div>
          <div>Has pregnant member: {{ latestIndicator.has_pregnant_member ? 'Yes' : 'No' }}</div>
          <div>Has child: {{ latestIndicator.has_child ? 'Yes' : 'No' }}</div>
        </div>

        <p v-if="assessmentMessage" :class="assessmentSuccess ? 'text-green-600' : 'text-red-600'" class="text-sm mt-3">
          {{ assessmentMessage }}
        </p>
      </div>
    </main>

    <main v-else-if="isLoading" class="p-6 text-slate-500">Loading household...</main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavBar from '@/components/AppNavBar.vue'
import * as householdsApi from '@/services/householdsApi'
import * as authApi from '@/services/authApi'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const household = ref(null)
const isLoading = ref(true)
const showMemberForm = ref(false)
const editingMemberId = ref(null)
const isSavingAssessment = ref(false)
const assessmentMessage = ref('')
const assessmentSuccess = ref(false)
const showResidentForm = ref(false)
const isSavingResident = ref(false)
const residentFormError = ref('')

const memberForm = reactive({
  full_name: '',
  birth_date: '',
  age: null,
  sex: '',
  relationship: '',
  occupation: '',
  is_senior_citizen: false,
  is_pwd: false,
  is_pregnant: false,
  is_child: false,
})

const residentForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
})

const assessmentForm = reactive({
  house_material: '',
  roof_material: '',
  flood_prone: false,
  storm_surge_prone: false,
  landslide_prone: false,
  coastal_zone: false,
})

const role = computed(() => authStore.user?.role)
const isSecretary = computed(() => role.value === 'Barangay Secretary')
const canCreateAssessment = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod'].includes(role.value))
const canEditFullAssessment = computed(() => ['Barangay Secretary', 'Barangay Kagawad/Tanod'].includes(role.value))
const canEditHealthFields = computed(() => role.value === 'Barangay Healthworker')

const latestIndicator = computed(() => {
  if (!household.value || !household.value.vulnerability_indicators.length) return null
  return household.value.vulnerability_indicators[0]
})

const activeMembers = computed(() => (household.value?.members || []).filter((member) => !member.is_archived))

const memberDerivedFlags = computed(() => ({
  has_senior_citizen: activeMembers.value.some((member) => member.is_senior_citizen),
  has_pwd: activeMembers.value.some((member) => member.is_pwd),
  has_pregnant_member: activeMembers.value.some((member) => member.is_pregnant),
  has_child: activeMembers.value.some((member) => member.is_child),
}))

function calculateAge(birthDateString) {
  const birthDate = new Date(birthDateString)
  if (Number.isNaN(birthDate.getTime())) return null
  const today = new Date()
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }
  return age
}

function handleBirthDateChange() {
  if (!memberForm.birth_date) return
  const calculatedAge = calculateAge(memberForm.birth_date)
  if (calculatedAge !== null) {
    memberForm.age = calculatedAge
  }
}

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

async function loadHousehold() {
  isLoading.value = true
  const response = await householdsApi.getHousehold(route.params.id)
  household.value = response.data
  if (latestIndicator.value) {
    Object.assign(assessmentForm, latestIndicator.value)
  }
  isLoading.value = false
}

onMounted(loadHousehold)

function resetMemberForm() {
  Object.assign(memberForm, {
    full_name: '',
    birth_date: '',
    age: null,
    sex: '',
    relationship: '',
    occupation: '',
    is_senior_citizen: false,
    is_pwd: false,
    is_pregnant: false,
    is_child: false,
  })
  editingMemberId.value = null
}

function toggleMemberForm() {
  if (showMemberForm.value) {
    showMemberForm.value = false
    resetMemberForm()
  } else {
    resetMemberForm()
    showMemberForm.value = true
  }
}

function startEditMember(member) {
  editingMemberId.value = member.member_id
  Object.assign(memberForm, {
    full_name: member.full_name,
    birth_date: member.birth_date || '',
    age: member.age,
    sex: member.sex,
    relationship: member.relationship,
    occupation: member.occupation || '',
    is_senior_citizen: member.is_senior_citizen,
    is_pwd: member.is_pwd,
    is_pregnant: member.is_pregnant,
    is_child: member.is_child,
  })
  showMemberForm.value = true
}

function cancelMemberForm() {
  showMemberForm.value = false
  resetMemberForm()
}

async function handleSaveMember() {
  const payload = { ...memberForm, birth_date: memberForm.birth_date || null }
  if (editingMemberId.value) {
    await householdsApi.updateMember(route.params.id, editingMemberId.value, payload)
  } else {
    await householdsApi.createMember(route.params.id, payload)
  }
  showMemberForm.value = false
  resetMemberForm()
  await loadHousehold()
}

async function handleArchiveMember(member) {
  if (!confirm(`Archive ${member.full_name}? This can be reversed later by an administrator.`)) return
  await householdsApi.archiveMember(route.params.id, member.member_id)
  await loadHousehold()
}

async function handleArchive() {
  if (!confirm('Archive this household? This can be reversed later by an administrator.')) return
  await householdsApi.archiveHousehold(route.params.id)
  router.push({ name: 'households' })
}

async function handleCreateResident() {
  isSavingResident.value = true
  residentFormError.value = ''
  try {
    await authApi.createResidentAccount({
      household_id: household.value.household_id,
      ...residentForm,
    })
    showResidentForm.value = false
    Object.assign(residentForm, { username: '', email: '', first_name: '', last_name: '', password: '' })
    await loadHousehold()
  } catch (error) {
    const data = error.response?.data
    residentFormError.value = data
      ? Object.values(data).flat().join(' ')
      : 'Failed to create Resident account.'
  } finally {
    isSavingResident.value = false
  }
}

async function handleCreateAssessment() {
  isSavingAssessment.value = true
  assessmentMessage.value = ''
  try {
    await householdsApi.createVulnerabilityIndicator(route.params.id, assessmentForm)
    assessmentSuccess.value = true
    assessmentMessage.value = 'Assessment saved.'
    await loadHousehold()
  } catch (error) {
    assessmentSuccess.value = false
    assessmentMessage.value = 'Failed to save assessment. Please check your input.'
  } finally {
    isSavingAssessment.value = false
  }
}

async function handleUpdateAssessment() {
  isSavingAssessment.value = true
  assessmentMessage.value = ''
  try {
    await householdsApi.updateVulnerabilityIndicator(route.params.id, latestIndicator.value.indicator_id, assessmentForm)
    assessmentSuccess.value = true
    assessmentMessage.value = 'Assessment updated.'
    await loadHousehold()
  } catch (error) {
    assessmentSuccess.value = false
    assessmentMessage.value = 'Failed to update assessment.'
  } finally {
    isSavingAssessment.value = false
  }
}
</script>