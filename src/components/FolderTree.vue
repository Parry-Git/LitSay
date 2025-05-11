<template>
  <div class="folder-tree-container">
    <el-tree
      :data="folderData"
      :props="defaultProps"
      node-key="id"
      :default-expanded-keys="[2]"
      :highlight-current="true"
      :expand-on-click-node="false"
      @node-click="handleNodeClick"
      v-loading="loading"
    >
      <template #default="{ node, data }">
        <div class="custom-tree-node">
          <el-icon :size="18" class="folder-icon">
            <Folder v-if="!node.expanded && data.children" />
            <FolderOpened v-else-if="node.expanded && data.children" />
            <Document v-else />
          </el-icon>
          <span class="folder-label">{{ node.label }}</span>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Folder, FolderOpened, Document } from "@element-plus/icons-vue";
import { getFolderStructure } from "@/api/load";
import { ElMessage } from "element-plus";

const router = useRouter();
const loading = ref(false);

// 初始化为空数组，等待数据加载
const folderData = ref<any[]>([]);

const defaultProps = {
  children: "children",
  label: "label",
};

// 获取文件夹结构的函数
const fetchFolderStructure = async () => {
  loading.value = true;
  try {
    // 直接使用 API 函数，它会根据环境自动选择数据源
    const response = await getFolderStructure();
    folderData.value = response.data.data || [];
  } catch (error) {
    console.error("获取文件夹结构失败", error);
    ElMessage.error("获取文件夹结构失败");
    // 如果获取失败，至少提供基本结构
    folderData.value = [
      {
        id: 1,
        label: "Home",
        icon: "home",
      },
      {
        id: 2,
        label: "我的文献库",
        icon: "folder",
        children: [],
      },
    ];
  } finally {
    loading.value = false;
  }
};

const handleNodeClick = (data: any) => {
  // 检测点击的是否为Home节点
  if (data.id === 1 && (data.label === "Home" || data.label === "首页")) {
    // 导航到home路由
    router.push("/");
  } else {
    // 对于其他文件夹节点，导航到文件夹内容页面
    router.push(`/folder/${data.id}`);
  }
};

// 组件挂载时获取文件夹结构
onMounted(() => {
  fetchFolderStructure();
});
</script>

<style scoped>
.folder-tree-container {
  padding: 8px 0;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  height: 24px;
}

.folder-icon {
  margin-right: 6px;
  color: #606266;
}

.folder-label {
  font-size: 14px;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #e6f1fc;
  color: #409eff;
}

:deep(.el-tree-node__content) {
  height: 32px;
}
</style>
