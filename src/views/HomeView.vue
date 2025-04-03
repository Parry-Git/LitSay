<template>
  <div class="home">
    <FileList />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";
import FileList from "@/components/FileList.vue";

export default defineComponent({
  name: "HomeView",
  components: {
    FileList,
  },
});
</script>

<style scoped>
.home {
  width: 100%;
  height: 100%;
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
