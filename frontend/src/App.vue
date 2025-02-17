<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useAdminStore } from './stores/admin'

const adminStore = useAdminStore()

onMounted(() => {
  adminStore.checkAuth()
})
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100%;
}
</style> 