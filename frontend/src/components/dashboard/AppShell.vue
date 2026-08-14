<template>
  <div class="flex h-screen overflow-hidden bg-slate-50">
    <Sidebar />

    <div class="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
      <TopBar />
      <main class="min-h-0 flex-1 overflow-x-hidden overflow-y-auto bg-[#f6f8fc] p-4 sm:p-6 lg:p-8">
        <div class="mx-auto w-full max-w-7xl">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import Sidebar from '@/components/dashboard/Sidebar.vue'
import TopBar from '@/components/dashboard/TopBar.vue'
</script>
