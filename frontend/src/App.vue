<template>
  <router-view v-if="!route.meta.requiresAuth" />
  <AppShell v-else>
    <router-view />
  </AppShell>
</template>
 
<script setup>
import { useRoute } from 'vue-router'
import AppShell from '@/components/dashboard/AppShell.vue'

const route = useRoute()
</script>
