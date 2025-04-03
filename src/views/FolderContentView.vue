<template>
  <div class="folder-content-view">
    <div class="folder-header">
      <h2>{{ currentFolder.label || "内容列表" }}</h2>
      <div class="folder-actions">
        <el-button type="primary" size="small" @click="handleAddFolder">
          <el-icon><FolderAdd /></el-icon>
          新建文件夹
        </el-button>
        <el-button type="success" size="small" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传文献
        </el-button>
      </div>
    </div>

    <el-divider />

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else>
      <div v-if="folderContents.length === 0" class="empty-folder">
        <el-empty description="此文件夹为空" />
      </div>
      <el-table
        v-else
        :data="folderContents"
        style="width: 100%"
        @row-click="handleItemClick"
      >
        <el-table-column width="60">
          <template #default="{ row }">
            <el-icon :size="24" class="content-icon">
              <Folder v-if="row.type === 'folder'" />
              <Document v-else />
            </el-icon>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="名称">
          <template #default="{ row }">
            <span
              class="item-name"
              :class="{ 'is-folder': row.type === 'folder' }"
            >
              {{ row.name }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="createTime" label="创建时间" width="180" />

        <el-table-column prop="info" label="信息" width="300">
          <template #default="{ row }">
            <span v-if="row.type === 'document' && row.info">
              {{ row.info }}
            </span>
            <span v-else>—</span>
          </template>
        </el-table-column>

        <el-table-column width="120">
          <template #default="{ row }">
            <el-dropdown
              trigger="click"
              @command="(cmd: CommandType) => handleCommand(cmd, row)"
            >
              <el-button type="text">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">重命名</el-dropdown-item>
                  <el-dropdown-item
                    v-if="row.type === 'document'"
                    command="download"
                    >下载</el-dropdown-item
                  >
                  <el-dropdown-item
                    v-if="row.type === 'document'"
                    command="metadata"
                    >编辑元数据</el-dropdown-item
                  >
                  <el-dropdown-item command="delete" divided type="danger"
                    >删除</el-dropdown-item
                  >
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 重命名对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名" width="30%">
      <el-form :model="renameForm">
        <el-form-item label="名称">
          <el-input v-model="renameForm.newName" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">确认</el-button>
      </template>
    </el-dialog>

    <!-- 新建文件夹对话框 -->
    <el-dialog v-model="newFolderDialogVisible" title="新建文件夹" width="30%">
      <el-form :model="newFolderForm">
        <el-form-item label="名称">
          <el-input v-model="newFolderForm.name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newFolderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateFolder">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Folder,
  Document,
  FolderAdd,
  Upload,
  MoreFilled,
} from "@element-plus/icons-vue";
import {
  getFolderContents,
  createFolder,
  deleteFolder,
  renameFolder,
  deleteDocument,
} from "@/api/load";

// 定义命令类型
type CommandType = "rename" | "download" | "metadata" | "delete";

// 路由和数据初始化
const route = useRoute();
const router = useRouter();
const loading = ref(true);
const currentFolderId = ref<string | number>(
  typeof route.params.id === "string" ? route.params.id : "root"
);
const currentFolder = ref<any>({});
const folderContents = ref<any[]>([]);

// 对话框相关状态
const renameDialogVisible = ref(false);
const newFolderDialogVisible = ref(false);
const renameForm = ref({ id: "", type: "", newName: "" });
const newFolderForm = ref({ name: "" });

// 获取当前文件夹内容
const fetchFolderContents = async () => {
  loading.value = true;
  try {
    const response = await getFolderContents(currentFolderId.value);
    const data = response.data.data;

    // 假设接口返回 { currentFolder: {...}, items: [...] }
    currentFolder.value = data.currentFolder || {};
    folderContents.value = data.items || [];

    // 如果currentFolder没有label字段，我们使用name字段
    if (
      currentFolder.value &&
      !currentFolder.value.label &&
      currentFolder.value.name
    ) {
      currentFolder.value.label = currentFolder.value.name;
    }
  } catch (error) {
    console.error("获取文件夹内容失败", error);
    ElMessage.error("获取文件夹内容失败");
    folderContents.value = [];
  } finally {
    loading.value = false;
  }
};

// 处理点击文件夹或文档事件
const handleItemClick = (row: any) => {
  if (row.type === "folder") {
    // 导航到子文件夹
    router.push(`/folder/${row.id}`);
  } else {
    // 对于文档，可以打开预览或详情页
    router.push(`/document/${row.id}`);
  }
};

// 处理下拉菜单命令
const handleCommand = (command: CommandType, row: any) => {
  switch (command) {
    case "rename":
      openRenameDialog(row);
      break;
    case "download":
      downloadDocument(row.id);
      break;
    case "metadata":
      router.push(`/document/${row.id}/edit`);
      break;
    case "delete":
      confirmDelete(row);
      break;
  }
};

// 打开重命名对话框
const openRenameDialog = (item: any) => {
  renameForm.value = {
    id: item.id,
    type: item.type,
    newName: item.name,
  };
  renameDialogVisible.value = true;
};

// 确认重命名
const confirmRename = async () => {
  try {
    if (renameForm.value.type === "folder") {
      await renameFolder({
        folderId: renameForm.value.id,
        newName: renameForm.value.newName,
      });
    } else {
      // 如果是文档，需要使用updateDocumentMetadata接口，这里简化处理
      // await updateDocumentMetadata(renameForm.value.id, { title: renameForm.value.newName });
    }
    ElMessage.success("重命名成功");
    fetchFolderContents(); // 刷新内容
  } catch (error) {
    console.error("重命名失败", error);
    ElMessage.error("重命名失败");
  } finally {
    renameDialogVisible.value = false;
  }
};

// 确认删除
const confirmDelete = (item: any) => {
  ElMessageBox.confirm(`确定要删除 ${item.name} 吗？`, "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        if (item.type === "folder") {
          await deleteFolder(item.id);
        } else {
          await deleteDocument(item.id);
        }
        ElMessage.success("删除成功");
        fetchFolderContents(); // 刷新内容
      } catch (error) {
        console.error("删除失败", error);
        ElMessage.error("删除失败");
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 处理添加文件夹
const handleAddFolder = () => {
  newFolderForm.value = { name: "" };
  newFolderDialogVisible.value = true;
};

// 确认创建文件夹
const confirmCreateFolder = async () => {
  try {
    await createFolder({
      parentId: currentFolderId.value,
      name: newFolderForm.value.name,
    });
    ElMessage.success("文件夹创建成功");
    fetchFolderContents(); // 刷新内容
  } catch (error) {
    console.error("创建文件夹失败", error);
    ElMessage.error("创建文件夹失败");
  } finally {
    newFolderDialogVisible.value = false;
  }
};

// 处理上传文献
const handleUpload = () => {
  router.push({
    path: "/upload",
    query: { folderId: currentFolderId.value.toString() },
  });
};

// 处理下载文档
const downloadDocument = (documentId: string | number) => {
  // 实现文档下载逻辑，可能需要调用后端接口
  ElMessage.info("开始下载文档...");
};

// 监听路由参数变化，重新获取文件夹内容
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
      // 确保 newId 是字符串而不是字符串数组
      currentFolderId.value = Array.isArray(newId) ? newId[0] : newId;
      fetchFolderContents();
    }
  }
);

// 组件挂载时获取数据
onMounted(() => {
  fetchFolderContents();
});
</script>

<style scoped>
.folder-content-view {
  padding: 20px;
}

.folder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.folder-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px 0;
}

.empty-folder {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.content-icon {
  color: #4285f4;
}

.item-name {
  font-weight: 500;
}

.item-name.is-folder {
  color: #4285f4;
  cursor: pointer;
}

.item-name.is-folder:hover {
  text-decoration: underline;
}
</style>
