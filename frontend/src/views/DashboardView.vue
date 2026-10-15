<template>
  <div class="space-y-6 pb-6">
    <!-- Breadcrumb & Page Header -->
    <header class="space-y-3">
      <nav class="flex items-center gap-2 text-xs font-semibold text-slate-500" aria-label="Breadcrumb">
        <router-link :to="{ name: 'dashboard' }" class="transition-colors hover:text-blue-600">SAFE-ALERT</router-link>
        <span class="text-slate-300" aria-hidden="true">/</span>
        <span class="text-slate-800">Dashboard</span>
      </nav>

      <div class="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 class="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Preparedness Dashboard</h1>
          <p class="mt-1 text-xs sm:text-sm font-medium text-slate-500">
            {{ locationDescription }}<span v-if="updatedAt"> · <span class="text-slate-400">Updated</span> {{ updatedAt }}</span>
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-2.5">
          <router-link
            to="/reports"
            class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border border-slate-200/90 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs transition-all hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <svg class="h-4 w-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            <span>View reports</span>
          </router-link>
          <router-link
            v-if="canCreateHousehold"
            to="/households/new"
            class="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            <span>New household</span>
          </router-link>
        </div>
      </div>

      <div v-if="roleDescription" class="inline-flex items-center gap-2 rounded-lg bg-blue-50/70 px-3 py-1.5 text-xs text-blue-900 border border-blue-100/70">
        <svg class="h-3.5 w-3.5 text-blue-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ roleDescription }}</span>
      </div>
    </header>

    <!-- Urgent Advisory / Broadcast Alert Banner -->
    <section
      v-if="urgentAnnouncement || pendingBroadcasts.length"
      class="flex flex-col gap-4 rounded-2xl border-l-4 border-l-amber-500 border border-amber-200/90 bg-gradient-to-r from-amber-50/90 via-amber-50/40 to-white p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5 shadow-xs"
      aria-label="Important system updates"
    >
      <div class="flex items-start gap-3.5">
        <span class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800 ring-1 ring-amber-200" aria-hidden="true">
          <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
        </span>
        <div class="min-w-0">
          <div class="flex items-center gap-2">
            <span class="inline-flex items-center rounded-md bg-amber-200/80 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-amber-900">Advisory Active</span>
            <p v-if="urgentAnnouncement" class="font-bold text-amber-950 text-sm sm:text-base">{{ urgentAnnouncement.title }}</p>
            <p v-else class="font-bold text-amber-950 text-sm sm:text-base">SMS broadcast awaiting authorization</p>
          </div>
          <p v-if="urgentAnnouncement" class="mt-1 line-clamp-2 text-xs sm:text-sm text-amber-900 leading-relaxed">{{ urgentAnnouncement.body }}</p>
          <p v-else class="mt-1 text-xs sm:text-sm text-amber-900 leading-relaxed">{{ pendingBroadcasts.length }} staged broadcast(s) are waiting for the BDRRMC Chairperson.</p>
          <p v-if="urgentAnnouncement && pendingBroadcasts.length" class="mt-1.5 text-xs font-medium text-amber-800">{{ pendingBroadcasts.length }} SMS broadcast(s) also await authorization.</p>
        </div>
      </div>
      <router-link
        v-if="canAuthorizeSms && pendingBroadcasts.length"
        to="/sms-notifications"
        class="inline-flex min-h-10 shrink-0 items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <span>Review authorization queue</span>
        <span aria-hidden="true">→</span>
      </router-link>
      <router-link
        v-else
        to="/announcements"
        class="inline-flex min-h-10 shrink-0 items-center justify-center rounded-xl border border-amber-300 bg-white px-4 py-2 text-xs font-semibold text-amber-950 shadow-xs transition-colors hover:bg-amber-50"
      >
        <span>View updates</span>
      </router-link>
    </section>

    <!-- 4 Key Readiness Metrics Cards -->
    <section class="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4" aria-label="Readiness metrics">
      <article
        v-for="metric in metrics"
        :key="metric.label"
        class="group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card transition-all duration-200 hover:border-slate-300 hover:shadow-card-hover"
      >
        <div class="flex items-start justify-between gap-3">
          <p class="text-xs font-bold uppercase tracking-wider text-slate-500">{{ metric.label }}</p>
          <span :class="metric.iconClass" class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ring-1 shadow-xs transition-transform group-hover:scale-105">
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" :d="metric.iconPath" />
            </svg>
          </span>
        </div>
        <p class="mt-4 text-3xl font-extrabold tracking-tight text-slate-900 tabular-nums">{{ metric.value }}</p>
        <p class="mt-1.5 text-xs font-medium text-slate-500">{{ metric.detail }}</p>
      </article>
    </section>

    <p v-if="loadWarning" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-900" role="status">
      {{ loadWarning }}
    </p>

    <!-- Readiness Analytics Section -->
    <section class="grid gap-5 xl:grid-cols-2" aria-label="Readiness analytics">
      <!-- CART Priority Distribution Donut -->
      <article class="min-w-0 rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">CART priority distribution</h2>
            <p class="mt-0.5 text-xs text-slate-500">Auto-computed on verified household assessments</p>
          </div>
          <span class="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 border border-emerald-200/60">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Live</span>
          </span>
        </div>

        <div v-if="canViewVulnerabilityDetails && assessedHouseholdCount" class="mt-6 flex flex-col items-center gap-6 sm:flex-row sm:justify-around">
          <!-- Circular Donut Chart -->
          <div
            class="relative h-44 w-44 shrink-0 rounded-full shadow-inner ring-4 ring-slate-100"
            :style="{ background: priorityDistributionGradient }"
            role="img"
            :aria-label="priorityChartLabel"
          >
            <div class="absolute inset-7 flex flex-col items-center justify-center rounded-full bg-white text-center shadow-xs">
              <span class="text-3xl font-extrabold text-slate-900 tabular-nums tracking-tight">{{ assessedHouseholdCount }}</span>
              <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Assessed</span>
            </div>
          </div>

          <!-- Priority Legend Breakdown -->
          <ul class="w-full max-w-xs space-y-2.5">
            <li
              v-for="item in priorityLegend"
              :key="item.label"
              class="flex items-center justify-between gap-4 rounded-xl p-2 text-xs font-medium transition-colors hover:bg-slate-50"
            >
              <span class="flex items-center gap-2.5 text-slate-700">
                <span :class="item.dot" class="h-3 w-3 rounded-full ring-2 ring-white shadow-xs" />
                <span class="font-semibold">{{ item.label }} priority</span>
              </span>
              <div class="flex items-center gap-2">
                <span class="font-bold text-slate-900 tabular-nums">{{ item.count }}</span>
                <span class="text-slate-400 tabular-nums text-[11px]">
                  ({{ assessedHouseholdCount ? Math.round((item.count / assessedHouseholdCount) * 100) : 0 }}%)
                </span>
              </div>
            </li>
            <li class="border-t border-slate-100 pt-2.5 text-right text-[11px] text-slate-400">
              {{ unassessedCount }} household(s) not yet assessed
            </li>
          </ul>
        </div>
        <p v-else class="mt-8 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
          {{ canViewVulnerabilityDetails ? 'No assessed household records yet.' : 'Household priority analytics are not available for this role.' }}
        </p>
      </article>

      <!-- Vulnerability by Purok Breakdown -->
      <article class="min-w-0 rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="border-b border-slate-100 pb-4">
          <h2 class="text-base font-bold text-slate-900">Vulnerability by purok</h2>
          <p class="mt-0.5 text-xs text-slate-500">Assessed households grouped by recorded purok zone</p>
        </div>

        <div v-if="canViewVulnerabilityDetails && purokStats.length" class="mt-6 space-y-3.5">
          <div
            v-for="group in purokStats"
            :key="group.name"
            class="grid grid-cols-[5.5rem_minmax(0,1fr)_2.5rem] items-center gap-3"
          >
            <span class="truncate text-xs font-semibold text-slate-700" :title="group.name">{{ group.name }}</span>
            <div
              class="h-4 overflow-hidden rounded-full bg-slate-100 shadow-inner"
              role="img"
              :aria-label="`${group.name}: ${group.high} high, ${group.medium} medium, ${group.low} low priority`"
            >
              <div class="flex h-full overflow-hidden rounded-full transition-all" :style="{ width: `${(group.total / maxPurokCount) * 100}%` }">
                <span class="bg-red-500 transition-all" :style="{ width: `${(group.high / group.total) * 100}%` }" title="High" />
                <span class="bg-amber-400 transition-all" :style="{ width: `${(group.medium / group.total) * 100}%` }" title="Medium" />
                <span class="bg-emerald-500 transition-all" :style="{ width: `${(group.low / group.total) * 100}%` }" title="Low" />
              </div>
            </div>
            <span class="text-right text-xs font-bold text-slate-800 tabular-nums">{{ group.total }}</span>
          </div>

          <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 text-[11px] text-slate-500">
            <div class="flex items-center gap-4">
              <span class="flex items-center gap-1.5 font-medium"><i class="h-2 w-2 rounded-full bg-red-500" />High</span>
              <span class="flex items-center gap-1.5 font-medium"><i class="h-2 w-2 rounded-full bg-amber-400" />Medium</span>
              <span class="flex items-center gap-1.5 font-medium"><i class="h-2 w-2 rounded-full bg-emerald-500" />Low</span>
            </div>
            <span class="text-slate-400">Total: {{ assessedHouseholdCount }} households</span>
          </div>
        </div>
        <p v-else class="mt-8 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
          {{ canViewVulnerabilityDetails ? 'Purok analytics will appear when assessed households are available.' : 'Household vulnerability details are not available for this role.' }}
        </p>
      </article>
    </section>

    <!-- Operational Section: Maps and Evacuation Centers -->
    <section class="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]" aria-label="Hazard maps and evacuation centers">
      <!-- Hazard Exposure Maps -->
      <article class="min-w-0 rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">Hazard exposure maps</h2>
            <p class="mt-0.5 text-xs text-slate-500">Project NOAH references and flood/surge overlays</p>
          </div>
          <router-link to="/hazard-maps" class="shrink-0 text-xs font-bold text-blue-600 transition-colors hover:text-blue-800">
            View all maps →
          </router-link>
        </div>

        <div v-if="hazardMaps.length" class="mt-5 space-y-3">
          <article
            v-for="hazardMap in hazardMaps.slice(0, 3)"
            :key="hazardMap.map_id"
            class="flex min-w-0 items-center gap-3.5 rounded-xl border border-slate-100 p-3 transition-colors hover:border-slate-200 hover:bg-slate-50/60"
          >
            <div
              v-if="hazardMap.map_image"
              class="relative h-14 w-16 shrink-0 rounded-lg overflow-hidden cursor-pointer group/img ring-1 ring-slate-200"
              title="Click to preview full map"
              @click="openMapPreview(hazardMap)"
            >
              <img :src="hazardMap.map_image" :alt="''" class="h-full w-full object-cover transition-transform group-hover/img:scale-110" />
              <div class="absolute inset-0 bg-slate-900/40 opacity-0 group-hover/img:opacity-100 transition-opacity flex items-center justify-center text-white">
                <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                </svg>
              </div>
            </div>
            <span v-else class="flex h-14 w-16 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-[11px] font-bold text-blue-700 ring-1 ring-blue-100">
              {{ hazardMap.hazard_type }}
            </span>
            <div class="min-w-0 flex-1 cursor-pointer" @click="openMapPreview(hazardMap)">
              <p class="truncate text-xs sm:text-sm font-semibold text-slate-800 hover:text-blue-600 transition-colors">{{ hazardMap.map_title }}</p>
              <p class="mt-0.5 text-[11px] text-slate-500 font-medium">{{ hazardMap.hazard_type }} · {{ hazardMap.source }}</p>
            </div>
            <button
              type="button"
              class="inline-flex min-h-8 shrink-0 items-center justify-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 shadow-xs hover:border-slate-300 hover:bg-slate-50 hover:text-blue-600 transition-colors"
              title="Preview full map"
              @click="openMapPreview(hazardMap)"
            >
              <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
              </svg>
              <span>Preview</span>
            </button>
            <router-link
              v-if="isInteractiveNoahMap(hazardMap)"
              :to="{ name: 'hazard-map-interactive', params: { id: hazardMap.map_id } }"
              class="inline-flex min-h-8 shrink-0 items-center justify-center rounded-lg bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700 transition-colors hover:bg-emerald-100"
            >
              Open map
            </router-link>
            <a
              v-else-if="hazardMap.map_url"
              :href="hazardMap.map_url"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex min-h-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700 transition-colors hover:bg-blue-100"
            >
              Open link
            </a>
          </article>
          <p v-if="hazardMaps.length > 3" class="text-right text-[11px] text-slate-400">
            +{{ hazardMaps.length - 3 }} more map reference(s) available
          </p>
        </div>
        <p v-else class="mt-6 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
          No hazard maps have been added for this area yet.
        </p>
      </article>

      <!-- Evacuation Centers Occupancy -->
      <article class="min-w-0 rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">Evacuation centers</h2>
            <p class="mt-0.5 text-xs text-slate-500">Live capacity and occupancy tracking</p>
          </div>
          <router-link to="/evacuation-centers" class="shrink-0 text-xs font-bold text-blue-600 transition-colors hover:text-blue-800">
            Manage centers →
          </router-link>
        </div>

        <div v-if="activeCentersList.length" class="mt-5 space-y-4">
          <div
            v-for="center in activeCentersList.slice(0, 5)"
            :key="center.center_id"
            class="space-y-1.5 rounded-xl p-2 transition-colors hover:bg-slate-50"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-xs sm:text-sm font-semibold text-slate-800">{{ center.name }}</p>
                <p class="mt-0.5 text-[11px] text-slate-400 truncate">{{ center.address }}</p>
              </div>
              <div class="shrink-0 text-right">
                <span class="text-xs sm:text-sm font-bold text-slate-900 tabular-nums">
                  {{ formatNumber(center.current_occupancy) }} / {{ formatNumber(center.capacity) }}
                </span>
                <span class="ml-1 text-[11px] font-semibold text-slate-500">({{ capacityPercentage(center) }}%)</span>
              </div>
            </div>
            <!-- Capacity Meter Bar -->
            <div class="h-2 overflow-hidden rounded-full bg-slate-100" role="img" :aria-label="`${center.name}: ${center.current_occupancy} of ${center.capacity} occupants`">
              <div :class="capacityBarClass(center)" class="h-full rounded-full transition-all duration-300" :style="{ width: `${capacityPercentage(center)}%` }" />
            </div>
          </div>
        </div>
        <p v-else class="mt-6 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
          No active evacuation centers are available.
        </p>
      </article>
    </section>

    <!-- Operational Updates, Quick Actions & SMS Staging -->
    <section class="grid items-start gap-5 xl:grid-cols-[1.15fr_0.85fr]" aria-label="Recent updates and quick actions">
      <!-- Recent System Updates Feed -->
      <article class="min-w-0 rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
        <div class="flex items-start justify-between gap-3 border-b border-slate-100 pb-4">
          <div>
            <h2 class="text-base font-bold text-slate-900">Recent system updates</h2>
            <p class="mt-0.5 text-xs text-slate-500">Announcements, warnings, and SMS broadcast activity</p>
          </div>
          <router-link to="/announcements" class="shrink-0 text-xs font-bold text-blue-600 transition-colors hover:text-blue-800">
            All updates →
          </router-link>
        </div>

        <ul v-if="recentUpdates.length" class="mt-3 divide-y divide-slate-100">
          <li v-for="item in recentUpdates" :key="item.id" class="flex gap-3 py-3.5 first:pt-2 last:pb-1">
            <span :class="item.iconClass" class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-xs font-bold ring-1 ring-black/5" aria-hidden="true">
              {{ item.icon }}
            </span>
            <div class="min-w-0 flex-1">
              <p class="text-xs sm:text-sm font-semibold text-slate-800">{{ item.title }}</p>
              <p class="mt-0.5 line-clamp-2 text-xs leading-relaxed text-slate-500">{{ item.detail }}</p>
              <p class="mt-1 text-[11px] font-medium text-slate-400">{{ relativeTime(item.date) }}</p>
            </div>
          </li>
        </ul>
        <p v-else class="mt-6 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
          No recent announcements or SMS broadcasts.
        </p>
      </article>

      <div class="space-y-5">
        <!-- Quick Actions Shortcuts -->
        <article class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
          <h2 class="text-base font-bold text-slate-900">Quick actions</h2>
          <p class="mt-0.5 text-xs text-slate-500">Operational shortcuts for {{ authStore.user?.role }}</p>
          <div class="mt-4 grid gap-2.5 sm:grid-cols-2">
            <router-link
              v-for="action in quickActions"
              :key="action.label"
              :to="action.to"
              class="group flex min-h-14 items-center gap-3 rounded-xl border border-slate-200/80 p-3 transition-all hover:border-blue-400 hover:bg-blue-50/50 hover:shadow-xs"
            >
              <span :class="action.iconClass" class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ring-1 ring-black/5 transition-transform group-hover:scale-105" aria-hidden="true">
                {{ action.icon }}
              </span>
              <span class="text-xs font-semibold text-slate-700 group-hover:text-blue-900">{{ action.label }}</span>
            </router-link>
          </div>
        </article>

        <!-- Awaiting Authorization Queue -->
        <article v-if="hasSmsAccess" class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
          <div class="flex items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div>
              <h2 class="text-base font-bold text-slate-900">Awaiting authorization</h2>
              <p class="mt-0.5 text-xs text-slate-500">Staged SMS broadcasts awaiting sign-off</p>
            </div>
            <span class="inline-flex items-center rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-900">
              {{ pendingBroadcasts.length }} pending
            </span>
          </div>

          <div v-if="pendingBroadcasts.length" class="mt-4 space-y-3">
            <div
              v-for="broadcast in pendingBroadcasts.slice(0, 3)"
              :key="broadcast.sms_id"
              class="rounded-xl border border-slate-200 bg-slate-50/50 p-3.5"
            >
              <p class="text-xs sm:text-sm font-semibold text-slate-900">{{ broadcast.subject }}</p>
              <p class="mt-1 text-[11px] text-slate-500 font-medium">{{ broadcast.recipient_type }} · Staged {{ relativeTime(broadcast.created_at) }}</p>
              <router-link
                to="/sms-notifications"
                class="mt-3 inline-flex min-h-8 items-center rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white shadow-xs transition-colors hover:bg-blue-700"
              >
                {{ canAuthorizeSms ? 'Review and authorize' : 'Review broadcast' }}
              </router-link>
            </div>
          </div>
          <p v-else class="mt-4 rounded-xl bg-slate-50 p-4 text-center text-xs text-slate-500">
            No emergency broadcasts are currently awaiting authorization.
          </p>
        </article>
      </div>
    </section>

    <!-- Top High Priority Households Table -->
    <section v-if="canViewVulnerabilityDetails" class="rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 shadow-card">
      <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <h2 class="text-base font-bold text-slate-900">Highest priority households</h2>
          <p class="mt-0.5 text-xs text-slate-500">Top households flagged for pre-emptive disaster evacuation</p>
        </div>
        <router-link to="/households" class="text-xs font-bold text-blue-600 transition-colors hover:text-blue-800">
          View all households →
        </router-link>
      </div>

      <div v-if="topPriorityHouseholds.length" class="mt-4 overflow-x-auto">
        <table class="w-full min-w-[600px] text-left text-xs sm:text-sm">
          <thead class="border-b border-slate-200/70 bg-slate-50/70 text-[11px] font-bold uppercase tracking-wider text-slate-500">
            <tr>
              <th class="py-3 px-3">Household #</th>
              <th class="py-3 px-3">Head of Family</th>
              <th class="py-3 px-3">Purok</th>
              <th class="py-3 px-3">Priority</th>
              <th class="py-3 px-3">Score</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="household in topPriorityHouseholds"
              :key="household.household_id"
              class="cursor-pointer transition-colors hover:bg-blue-50/40"
              tabindex="0"
              @click="openHousehold(household)"
              @keydown.enter="openHousehold(household)"
            >
              <td class="py-3 px-3 font-semibold text-slate-800">{{ household.household_number }}</td>
              <td class="py-3 px-3 text-slate-700">{{ household.head_of_family }}</td>
              <td class="py-3 px-3 text-slate-600">{{ household.purok }}</td>
              <td class="py-3 px-3">
                <span :class="priorityBadgeClass(household.evacuation_priority)" class="inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold">
                  {{ household.evacuation_priority }}
                </span>
              </td>
              <td class="py-3 px-3 font-semibold text-slate-800 tabular-nums">{{ household.priority_score }}%</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="mt-4 rounded-xl bg-slate-50 p-6 text-center text-xs text-slate-500">
        No assessed households yet.
      </p>
    </section>

    <!-- Quick Map Preview Modal Lightbox -->
    <Teleport to="body">
      <div
        v-if="previewMap"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-xs p-3 sm:p-6"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dashboard-map-preview-title"
        @keydown.esc="closeMapPreview"
        @click.self="closeMapPreview"
      >
        <section class="flex h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
          <!-- Modal Header -->
          <header class="flex items-center justify-between border-b border-slate-200 px-5 py-3.5">
            <div class="flex items-center gap-3 min-w-0">
              <span :class="hazardBadgeClass(previewMap.hazard_type)" class="inline-flex shrink-0 items-center rounded-full px-2.5 py-0.5 text-xs font-bold">
                {{ previewMap.hazard_type }}
              </span>
              <div class="min-w-0">
                <h2 id="dashboard-map-preview-title" class="truncate text-base font-bold text-slate-900">{{ previewMap.map_title }}</h2>
                <p class="text-[11px] text-slate-500 font-medium">Source: {{ previewMap.source }} · Official Hazard Reference</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                type="button"
                class="flex h-9 w-9 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-100 hover:text-slate-800 transition-colors"
                aria-label="Close preview"
                @click="closeMapPreview"
              >
                <span aria-hidden="true" class="text-2xl leading-none">&times;</span>
              </button>
            </div>
          </header>

          <!-- Modal Body / Map Image Display -->
          <div class="relative flex-1 overflow-auto bg-slate-900/95 flex flex-col items-center justify-center p-4">
            <div v-if="previewMap.map_image" class="relative max-h-full max-w-full flex items-center justify-center">
              <img
                :src="previewMap.map_image"
                :alt="`${previewMap.map_title} high resolution map preview`"
                class="max-h-[62vh] w-auto max-w-full rounded-lg object-contain shadow-2xl ring-1 ring-white/10"
              />
            </div>
            <div v-else class="text-center p-8 max-w-md bg-white rounded-2xl shadow-xl">
              <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 mb-3">
                <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m9 18-6 3V6l6-3 6 3 6-3v15l-6 3-6-3Zm0-15v15m6-12v15" />
                </svg>
              </div>
              <h3 class="text-base font-bold text-slate-900">Map Graphic File Not Attached</h3>
              <p class="mt-1 text-xs text-slate-500 leading-relaxed">
                This entry is cataloged as a digital reference. You can launch the interactive GIS layer or visit the source repository.
              </p>
            </div>

            <!-- Severity Legend Pill in Preview -->
            <div class="mt-3 flex items-center gap-4 rounded-full bg-slate-900/80 px-4 py-1.5 text-xs text-white border border-white/10 shadow-lg">
              <span class="font-bold text-[11px] uppercase tracking-wider text-slate-300">Severity:</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#facc15]" /> Low</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#fb923c]" /> Medium</span>
              <span class="flex items-center gap-1.5 font-medium"><span class="h-2.5 w-2.5 rounded-sm bg-[#ef4444]" /> High</span>
            </div>
          </div>

          <!-- Modal Footer Details & Navigation Options -->
          <footer class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-white px-5 py-3.5">
            <div class="min-w-0 max-w-md">
              <p v-if="previewMap.description" class="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                {{ previewMap.description }}
              </p>
              <p v-else class="text-xs text-slate-400">
                Official hazard boundary data verified for Baclayon, Bohol.
              </p>
            </div>

            <div class="flex items-center gap-2.5">
              <button
                type="button"
                class="rounded-xl border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                @click="closeMapPreview"
              >
                Close Preview
              </button>

              <a
                v-if="previewMap.map_url"
                :href="previewMap.map_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors"
              >
                <span>Open External Link</span>
                <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                  <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                </svg>
              </a>

              <router-link
                v-if="isInteractiveNoahMap(previewMap)"
                :to="{ name: 'hazard-map-interactive', params: { id: previewMap.map_id } }"
                class="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-emerald-700 transition-colors"
                @click="closeMapPreview"
              >
                <span>Launch Interactive GIS Map</span>
                <span aria-hidden="true">→</span>
              </router-link>
            </div>
          </footer>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as householdsApi from '@/services/householdsApi'
import * as evacuationCentersApi from '@/services/evacuationCentersApi'
import * as announcementsApi from '@/services/announcementsApi'
import * as mapsApi from '@/services/mapsApi'
import { NOAH_HAZARD_LAYERS } from '@/services/noahHazardLayers'

const authStore = useAuthStore()
const router = useRouter()
const households = ref([])
const centers = ref([])
const announcements = ref([])
const hazardMaps = ref([])
const smsNotifications = ref([])
const previewMap = ref(null)
const updatedAt = ref('')
const loadIssues = ref([])

const role = computed(() => authStore.user?.role)
const roleDescriptions = {
  'Barangay Secretary': 'Coordinate barangay readiness, household records, and emergency updates.',
  'BDRRMC Chairperson': 'Review response information and authorize staged emergency broadcasts.',
  'MDRRMO Officer': 'Monitor municipal-level readiness information across both barangays.',
  'Barangay Kagawad/Tanod': 'Review field assessments and evacuation center readiness.',
  'Barangay Healthworker': 'Review household vulnerability information for your assigned purok.',
  Resident: 'Review evacuation information and public safety updates for your household.',
}
const roleDescription = computed(() => roleDescriptions[role.value] || '')
const locationDescription = computed(() => {
  const barangay = authStore.user?.barangay_name
  return barangay ? `Baclayon, Bohol · Barangay ${barangay}` : 'Municipality of Baclayon, Bohol · All barangays'
})
const canCreateHousehold = computed(() => role.value === 'Barangay Secretary')
const canViewHouseholds = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer', 'Resident',
].includes(role.value))
const canViewVulnerabilityDetails = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'MDRRMO Officer',
].includes(role.value))
const hasSmsAccess = computed(() => role.value !== 'Resident')
const canAuthorizeSms = computed(() => role.value === 'BDRRMC Chairperson')
const canManageAnnouncements = computed(() => ['Barangay Secretary', 'MDRRMO Officer'].includes(role.value))
const canViewReports = computed(() => [
  'Barangay Secretary', 'Barangay Kagawad/Tanod', 'Barangay Healthworker', 'BDRRMC Chairperson', 'MDRRMO Officer', 'Resident',
].includes(role.value))

const householdCount = computed(() => households.value.length)
const priorityCounts = computed(() => ({
  High: households.value.filter((household) => household.evacuation_priority === 'High').length,
  Medium: households.value.filter((household) => household.evacuation_priority === 'Medium').length,
  Low: households.value.filter((household) => household.evacuation_priority === 'Low').length,
}))
const assessedHouseholdCount = computed(() => priorityCounts.value.High + priorityCounts.value.Medium + priorityCounts.value.Low)
const unassessedCount = computed(() => households.value.filter((household) => !household.evacuation_priority).length)
const topPriorityHouseholds = computed(() => households.value
  .filter((household) => household.evacuation_priority)
  .slice()
  .sort((a, b) => (Number(b.priority_score) || 0) - (Number(a.priority_score) || 0))
  .slice(0, 10))
const totalResidents = computed(() => households.value.reduce((total, household) => total + (Number(household.total_members) || 0), 0))
const activeCentersList = computed(() => centers.value.filter((center) => center.status === 'Active'))
const activeCenters = computed(() => activeCentersList.value.length)
const totalCapacity = computed(() => activeCentersList.value.reduce((total, center) => total + (Number(center.capacity) || 0), 0))
const occupiedCapacity = computed(() => activeCentersList.value.reduce((total, center) => total + (Number(center.current_occupancy) || 0), 0))
const capacityUsed = computed(() => totalCapacity.value ? Math.min(100, Math.round((occupiedCapacity.value / totalCapacity.value) * 100)) : null)
const deliveryStats = computed(() => {
  const logs = smsNotifications.value.flatMap((notification) => notification.logs || [])
  const delivered = logs.filter((log) => log.delivery_status === 'Delivered').length
  const failed = logs.filter((log) => log.delivery_status === 'Failed').length
  const simulated = logs.filter((log) => log.delivery_status === 'Simulated').length
  const decided = delivered + failed
  return { delivered, failed, simulated, rate: decided ? Math.round((delivered / decided) * 1000) / 10 : null }
})

const metrics = computed(() => [
  {
    label: 'Households encoded',
    value: canViewHouseholds.value ? formatNumber(householdCount.value) : '—',
    detail: canViewHouseholds.value ? `${formatNumber(assessedHouseholdCount.value)} classified by CART` : 'Not available for this role',
    iconClass: 'bg-blue-50 text-blue-600 ring-blue-100',
    iconPath: 'm3 10 9-6 9 6v10H3V10Zm6 10v-6h6v6',
  },
  {
    label: 'High-priority households',
    value: canViewHouseholds.value ? formatNumber(priorityCounts.value.High) : '—',
    detail: canViewHouseholds.value ? `${householdCount.value ? ((priorityCounts.value.High / householdCount.value) * 100).toFixed(1) : 0}% of encoded households` : 'Not available for this role',
    iconClass: 'bg-red-50 text-red-600 ring-red-100',
    iconPath: 'M12 3 4.5 6v5.5c0 4.5 3.1 7.7 7.5 9.5 4.4-1.8 7.5-5 7.5-9.5V6L12 3Zm0 5v5m0 3h.01',
  },
  {
    label: 'Evacuation capacity used',
    value: capacityUsed.value === null ? '—' : `${capacityUsed.value}%`,
    detail: totalCapacity.value ? `${formatNumber(occupiedCapacity.value)} of ${formatNumber(totalCapacity.value)} places occupied` : `${activeCenters.value} active center(s) · capacity not recorded`,
    iconClass: 'bg-amber-50 text-amber-700 ring-amber-100',
    iconPath: 'M4 20h16M6 20V8l6-4 6 4v12m-9-8h.01M12 12h.01m3 0h.01m-6 4h.01m3 0h.01m3 0h.01',
  },
  {
    label: 'SMS delivery rate',
    value: hasSmsAccess.value && deliveryStats.value.rate !== null ? `${deliveryStats.value.rate}%` : '—',
    detail: hasSmsAccess.value ? `${deliveryStats.value.delivered} delivered · ${deliveryStats.value.failed} failed${deliveryStats.value.simulated ? ` · ${deliveryStats.value.simulated} simulated` : ''}` : 'Not available for this role',
    iconClass: 'bg-emerald-50 text-emerald-700 ring-emerald-100',
    iconPath: 'M4 5h16v11H8l-4 4V5Zm4 4h8m-8 3h5',
  },
])

const priorityLegend = computed(() => [
  { label: 'High', count: priorityCounts.value.High, dot: 'bg-red-500' },
  { label: 'Medium', count: priorityCounts.value.Medium, dot: 'bg-amber-400' },
  { label: 'Low', count: priorityCounts.value.Low, dot: 'bg-emerald-500' },
])
const priorityDistributionGradient = computed(() => {
  const total = assessedHouseholdCount.value
  if (!total) return 'conic-gradient(#e2e8f0 0% 100%)'
  const highEnd = priorityCounts.value.High / total * 100
  const mediumEnd = highEnd + priorityCounts.value.Medium / total * 100
  return `conic-gradient(#ef4444 0% ${highEnd}%, #f59e0b ${highEnd}% ${mediumEnd}%, #10b981 ${mediumEnd}% 100%)`
})
const priorityChartLabel = computed(() => `Priority distribution: ${priorityCounts.value.High} high, ${priorityCounts.value.Medium} medium, ${priorityCounts.value.Low} low`)

const purokStats = computed(() => {
  const groups = new Map()
  for (const household of households.value) {
    if (!household.evacuation_priority) continue
    const name = household.purok || 'Unassigned'
    if (!groups.has(name)) groups.set(name, { name, high: 0, medium: 0, low: 0, total: 0 })
    const group = groups.get(name)
    const key = household.evacuation_priority.toLowerCase()
    if (key in group) {
      group[key] += 1
      group.total += 1
    }
  }
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true })).slice(0, 8)
})
const maxPurokCount = computed(() => Math.max(1, ...purokStats.value.map((group) => group.total)))

const urgentAnnouncement = computed(() => announcements.value.find((announcement) => {
  const urgent = (announcement.categories || []).some((category) => ['Emergency', 'Alert'].includes(category.category))
  const notExpired = !announcement.expires_at || new Date(announcement.expires_at) > new Date()
  return urgent && notExpired
}) || null)
const pendingBroadcasts = computed(() => smsNotifications.value.filter((notification) => notification.status === 'Pending'))
const recentUpdates = computed(() => [
  ...announcements.value.map((announcement) => ({
    id: `announcement-${announcement.announcement_id}`,
    title: announcement.title,
    detail: announcement.body,
    date: announcement.created_at,
    icon: 'AN',
    iconClass: 'bg-amber-50 text-amber-800 ring-amber-100',
  })),
  ...smsNotifications.value.map((notification) => ({
    id: `sms-${notification.sms_id}`,
    title: `${notification.subject} · ${notification.status}`,
    detail: `${notification.recipient_type} recipients · ${notification.sent_count} sent · ${notification.failed_count} failed`,
    date: notification.created_at,
    icon: 'SMS',
    iconClass: 'bg-blue-50 text-blue-700 ring-blue-100',
  })),
].filter((item) => item.date).sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 5))

const quickActions = computed(() => {
  const actions = []
  if (canCreateHousehold.value) actions.push({ label: 'Add household', to: '/households/new', icon: 'HH', iconClass: 'bg-blue-50 text-blue-700 ring-blue-100' })
  if (canManageAnnouncements.value) actions.push({ label: 'Post announcement', to: '/announcements/new', icon: 'AN', iconClass: 'bg-amber-50 text-amber-700 ring-amber-100' })
  if (role.value === 'Barangay Secretary') actions.push({ label: 'Stage SMS alert', to: '/sms-notifications', icon: 'SMS', iconClass: 'bg-cyan-50 text-cyan-800 ring-cyan-100' })
  if (canAuthorizeSms.value) actions.push({ label: 'Authorize SMS', to: '/sms-notifications', icon: 'OK', iconClass: 'bg-emerald-50 text-emerald-700 ring-emerald-100' })
  if (role.value === 'Barangay Kagawad/Tanod') actions.push({ label: 'Update center occupancy', to: '/evacuation-centers', icon: 'EC', iconClass: 'bg-orange-50 text-orange-700 ring-orange-100' })
  if (role.value === 'Barangay Secretary') actions.push({ label: 'Manage accounts', to: '/accounts', icon: 'UA', iconClass: 'bg-blue-50 text-blue-700 ring-blue-100' })
  if (canViewReports.value) actions.push({ label: 'Generate reports', to: '/reports', icon: 'PDF', iconClass: 'bg-slate-100 text-slate-700 ring-slate-200' })
  return actions
})

const loadWarning = computed(() => loadIssues.value.length ? `Some dashboard data could not be loaded: ${loadIssues.value.join(', ')}.` : '')

function formatNumber(value) {
  return new Intl.NumberFormat().format(Number(value) || 0)
}

function formatDate(value) {
  if (!value) return ''
  return new Intl.DateTimeFormat('en-PH', { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Manila' }).format(new Date(value))
}

function relativeTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Recently'
  const minutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000))
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} hr${hours === 1 ? '' : 's'} ago`
  const days = Math.floor(hours / 24)
  return `${days} day${days === 1 ? '' : 's'} ago`
}

function capacityPercentage(center) {
  const capacity = Number(center.capacity) || 0
  return capacity ? Math.min(100, Math.round((Number(center.current_occupancy || 0) / capacity) * 100)) : 0
}

function capacityBarClass(center) {
  const percentage = capacityPercentage(center)
  if (percentage >= 90) return 'bg-red-500'
  if (percentage >= 70) return 'bg-amber-500'
  return 'bg-emerald-500'
}

function isInteractiveNoahMap(hazardMap) {
  return hazardMap.source === 'Project NOAH' && Boolean(NOAH_HAZARD_LAYERS[hazardMap.hazard_type])
}

function priorityBadgeClass(priority) {
  if (priority === 'High') return 'bg-red-100 text-red-700'
  if (priority === 'Medium') return 'bg-amber-100 text-amber-800'
  return 'bg-emerald-100 text-emerald-700'
}

function openHousehold(household) {
  router.push({ name: 'household-detail', params: { id: household.household_id } })
}

function openMapPreview(map) {
  previewMap.value = map
}

function closeMapPreview() {
  previewMap.value = null
}

function handleKeydown(event) {
  if (event.key === 'Escape' && previewMap.value) {
    closeMapPreview()
  }
}

function hazardBadgeClass(hazardType) {
  const map = {
    Flood: 'bg-blue-100 text-blue-800',
    'Storm Surge': 'bg-cyan-100 text-cyan-800',
    Landslide: 'bg-amber-100 text-amber-800',
    Earthquake: 'bg-red-100 text-red-800',
  }
  return map[hazardType] || 'bg-slate-100 text-slate-700'
}

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  const requests = [
    householdsApi.listHouseholds(),
    evacuationCentersApi.listCenters(),
    announcementsApi.listAnnouncements(),
    mapsApi.listHazardMaps(),
  ]
  if (hasSmsAccess.value) requests.push(announcementsApi.listSmsNotifications())
  const results = await Promise.allSettled(requests)
  const [householdResult, centerResult, announcementResult, mapResult] = results
  loadIssues.value = []
  if (householdResult.status === 'fulfilled') households.value = householdResult.value.data
  else loadIssues.value.push('households')
  if (centerResult.status === 'fulfilled') centers.value = centerResult.value.data
  else loadIssues.value.push('evacuation centers')
  if (announcementResult.status === 'fulfilled') announcements.value = announcementResult.value.data
  else loadIssues.value.push('announcements')
  if (mapResult.status === 'fulfilled') hazardMaps.value = mapResult.value.data
  else loadIssues.value.push('hazard maps')
  if (hasSmsAccess.value) {
    const smsResult = results[4]
    if (smsResult.status === 'fulfilled') smsNotifications.value = smsResult.value.data
    else loadIssues.value.push('SMS broadcasts')
  }
  updatedAt.value = formatDate(new Date())
})
</script>
