<template>
  <div class="home">
    <Welcome class="welcome-section" />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import Welcome from "@/components/Welcome.vue";

export default defineComponent({
  name: "HomeView",
  components: {
    Welcome,
  },
});
</script>

<style scoped>
.home {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.home-container {
  background-color: #fff;
  border-radius: 8px;
  padding: 16px;
}

.home-header {
  margin-bottom: 16px;
}

.home-title {
  font-size: 22px;
  font-weight: 500;
  color: #202124;
  margin: 0;
}
</style>
