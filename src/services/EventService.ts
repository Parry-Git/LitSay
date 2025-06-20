import { ref } from "vue";
import { useEventBus } from "@vueuse/core";

// 创建全局可访问的事件总线
export const folderChangedBus = useEventBus<void>("folder-changed");

// 触发文件夹更新事件
export function notifyFolderStructureChanged() {
  // console.log("触发文件夹结构更新事件");
  folderChangedBus.emit();
}
