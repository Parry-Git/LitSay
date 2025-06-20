<script setup lang="ts">
import { notifyFolderStructureChanged } from '@/services/EventService';
// ...existing imports...

// 可以在组件内部直接调用通知函数
const manuallyRefreshFolder = () => {
  notifyFolderStructureChanged();
};
</script>
