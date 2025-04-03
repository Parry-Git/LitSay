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
</style>
