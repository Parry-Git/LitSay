<template>
  <router-view v-slot="{ Component }">
    <component :is="Component" v-if="$route.meta.fullScreen" />
    <AppLayout v-else>
      <component :is="Component" />
    </AppLayout>
  </router-view>
</template>

<script setup lang="ts">
import AppLayout from "@/components/Layout/AppLayout.vue";
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
