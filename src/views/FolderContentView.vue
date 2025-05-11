<template>
  <div class="folder-content-view">
    <a-page-header
      class="folder-header"
      :title="getFolderDisplayName()"
      :sub-title="currentFolder.path || ''"
      @back="goBack"
    >
      <template #extra>
        <a-space>
          <a-button type="primary" @click="handleAddFolder">
            <template #icon><folder-add-outlined /></template>
            新建文件夹
          </a-button>
          <a-button type="primary" @click="handleUpload">
            <template #icon><upload-outlined /></template>
            上传文献
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <a-divider style="margin: 12px 0" />

    <div class="folder-content">
      <a-spin :spinning="loading" tip="加载中...">
        <a-empty
          v-if="!loading && folderContents.length === 0"
          description="此文件夹为空"
        />

        <a-table
          v-else
          :dataSource="folderContents"
          :columns="columns"
          :pagination="false"
          :rowKey="(record) => record.id"
          :row-class-name="() => 'folder-row'"
        >
          <!-- 自定义图标和名称列 -->
          <template #bodyCell="{ column, record }">
            <!-- 图标+名称列 -->
            <template v-if="column.dataIndex === 'name'">
              <div class="item-name-cell" @click="handleItemClick(record)">
                <a-space>
                  <folder-outlined
                    v-if="record.type === 'folder'"
                    class="folder-icon"
                  />
                  <file-pdf-outlined v-else class="document-icon" />
                  <span
                    class="item-name"
                    :class="{ 'is-folder': record.type === 'folder' }"
                  >
                    {{ getItemDisplayName(record) }}
                  </span>
                </a-space>
              </div>
            </template>

            <!-- 操作列 -->
            <template v-if="column.dataIndex === 'actions'">
              <a-dropdown :trigger="['click']" @click.stop>
                <a class="ant-dropdown-link" @click.stop>
                  <more-outlined />
                </a>
                <template #overlay>
                  <a-menu @click="({ key }) => handleMenuClick(key, record)">
                    <a-menu-item key="rename">
                      <edit-outlined /> 重命名
                    </a-menu-item>
                    <a-menu-item
                      v-if="record.type === 'document'"
                      key="download"
                    >
                      <download-outlined /> 下载
                    </a-menu-item>
                    <a-menu-item
                      v-if="record.type === 'document'"
                      key="metadata"
                    >
                      <setting-outlined /> 编辑元数据
                    </a-menu-item>
                    <a-menu-divider />
                    <a-menu-item key="delete" danger>
                      <delete-outlined /> 删除
                    </a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </template>
          </template>
        </a-table>
      </a-spin>
    </div>

    <!-- 重命名对话框 -->
    <a-modal
      v-model:visible="renameDialogVisible"
      title="重命名"
      @ok="confirmRename"
      :okButtonProps="{ loading: processing }"
    >
      <a-form :model="renameForm">
        <a-form-item
          label="新名称"
          :rules="[{ required: true, message: '请输入名称' }]"
        >
          <a-input
            v-model:value="renameForm.newName"
            placeholder="请输入新名称"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 新建文件夹对话框 -->
    <a-modal
      v-model:visible="newFolderDialogVisible"
      title="新建文件夹"
      @ok="confirmCreateFolder"
      :okButtonProps="{ loading: processing }"
    >
      <a-form :model="newFolderForm">
        <a-form-item
          label="文件夹名称"
          :rules="[{ required: true, message: '请输入文件夹名称' }]"
        >
          <a-input
            v-model:value="newFolderForm.name"
            placeholder="请输入文件夹名称"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 删除确认对话框 -->
    <a-modal
      v-model:visible="deleteDialogVisible"
      title="确认删除"
      @ok="confirmDeleteItem"
      :okButtonProps="{ loading: processing, danger: true }"
      okText="删除"
      cancelText="取消"
    >
      <p>确定要删除"{{ deleteItemName }}"吗？此操作不可撤销。</p>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { message } from "ant-design-vue";
import {
  FolderOutlined,
  FilePdfOutlined,
  FolderAddOutlined,
  UploadOutlined,
  EditOutlined,
  DownloadOutlined,
  SettingOutlined,
  DeleteOutlined,
  MoreOutlined,
} from "@ant-design/icons-vue";
import {
  getFolderContents,
  createFolder,
  deleteFolder,
  renameFolder,
  deleteDocument,
} from "@/api/load";

// 定义表格列
const columns = [
  {
    title: "名称",
    dataIndex: "name",
    key: "name",
    ellipsis: true,
  },
  {
    title: "创建时间",
    dataIndex: "createTime",
    key: "createTime",
    width: 250,
  },
  {
    title: "操作",
    dataIndex: "actions",
    key: "actions",
    width: 80,
    align: "center",
  },
];

// 路由和数据初始化
const route = useRoute();
const router = useRouter();
const loading = ref(true);
const processing = ref(false);
const currentFolderId = ref<string | number>(
  typeof route.params.id === "string" ? route.params.id : "root"
);
const currentFolder = ref<any>({});
const folderContents = ref<any[]>([]);

// 对话框相关状态
const renameDialogVisible = ref(false);
const newFolderDialogVisible = ref(false);
const deleteDialogVisible = ref(false);
const renameForm = reactive({ id: "", type: "", newName: "" });
const newFolderForm = reactive({ name: "" });
const deleteItemName = ref("");
const deleteItemInfo = reactive({ id: "", type: "" });

// 获取文件/文件夹显示名称
const getItemDisplayName = (item: any): string => {
  return (
    item.name ||
    item.label ||
    `未命名${item.type === "folder" ? "文件夹" : "文献"}`
  );
};

// 获取当前文件夹显示名称 - 修改为无参数方法
const getFolderDisplayName = (): string => {
  if (currentFolder.value) {
    if (currentFolder.value.name || currentFolder.value.label) {
      return currentFolder.value.name || currentFolder.value.label;
    }
  }

  // 为一些常见ID提供默认名称
  const id = currentFolderId.value;
  if (id === 1 || id === "1") return "首页";
  if (id === 2 || id === "2") return "我的文献库";
  if (id === "root") return "根目录";

  return `文件夹 ${id}`;
};

// 获取当前文件夹内容 - 修改为处理新的数据结构
const fetchFolderContents = async () => {
  loading.value = true;
  try {
    const response = await getFolderContents(currentFolderId.value);
    console.log("Folder contents response:", response);

    // 处理不同的响应数据结构
    if (response && response.data && response.data.data) {
      // 标准API响应
      const data = response.data.data;

      if (data.currentFolder && data.items) {
        // 新结构: 包含currentFolder和items字段
        currentFolder.value = data.currentFolder;
        folderContents.value = data.items || [];
      } else if (Array.isArray(data)) {
        // 兼容旧结构: 直接是数组
        folderContents.value = data;
        currentFolder.value = { id: currentFolderId.value };
      } else if (typeof data === "object") {
        // 可能是其他结构
        if (Array.isArray(data.items)) {
          folderContents.value = data.items;
          currentFolder.value = data.currentFolder || {
            id: currentFolderId.value,
          };
        } else {
          folderContents.value = Array.isArray(data) ? data : [];
          currentFolder.value = { id: currentFolderId.value };
        }
      } else {
        folderContents.value = [];
        currentFolder.value = { id: currentFolderId.value };
      }
    } else if (
      response &&
      response.currentFolder &&
      Array.isArray(response.items)
    ) {
      // 直接返回了对象结构 {currentFolder, items}
      currentFolder.value = response.currentFolder;
      folderContents.value = response.items;
    } else if (Array.isArray(response)) {
      // 直接返回了数组
      folderContents.value = response;
      currentFolder.value = { id: currentFolderId.value };
    } else {
      folderContents.value = [];
      currentFolder.value = { id: currentFolderId.value };
    }

    // 确保每个项目都有合适的键用于展示
    folderContents.value = folderContents.value.map((item) => ({
      ...item,
      key: item.id || `${item.type}-${Date.now()}-${Math.random()}`,
    }));
  } catch (error) {
    console.error("获取文件夹内容失败", error);
    message.error("获取文件夹内容失败");
    folderContents.value = [];
    currentFolder.value = { id: currentFolderId.value };
  } finally {
    loading.value = false;
  }
};

// 返回上级目录
const goBack = () => {
  router.back();
};

// 处理点击文件夹或文档事件
const handleItemClick = (row: any) => {
  if (row.type === "folder") {
    // 导航到子文件夹
    router.push(`/folder/${row.id}`);
  } else {
    // 对于文档，打开详情页
    router.push(`/document/${row.id}`);
  }
};

// 处理菜单点击
const handleMenuClick = (key: string, row: any) => {
  switch (key) {
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
      openDeleteDialog(row);
      break;
  }
};

// 打开重命名对话框
const openRenameDialog = (item: any) => {
  renameForm.id = item.id;
  renameForm.type = item.type;
  renameForm.newName = getItemDisplayName(item);
  renameDialogVisible.value = true;
};

// 确认重命名
const confirmRename = async () => {
  if (!renameForm.newName.trim()) {
    message.warning("名称不能为空");
    return;
  }

  processing.value = true;
  try {
    if (renameForm.type === "folder") {
      await renameFolder({
        folderId: renameForm.id,
        newName: renameForm.newName,
      });
    } else {
      // 如果是文档，使用updateDocumentMetadata接口
      // 实际实现时需要根据API调整
    }
    message.success("重命名成功");
    fetchFolderContents(); // 刷新内容
    renameDialogVisible.value = false;
  } catch (error) {
    console.error("重命名失败", error);
    message.error("重命名失败");
  } finally {
    processing.value = false;
  }
};

// 打开删除确认对话框
const openDeleteDialog = (item: any) => {
  deleteItemName.value = getItemDisplayName(item);
  deleteItemInfo.id = item.id;
  deleteItemInfo.type = item.type;
  deleteDialogVisible.value = true;
};

// 确认删除项目
const confirmDeleteItem = async () => {
  processing.value = true;
  try {
    if (deleteItemInfo.type === "folder") {
      await deleteFolder(deleteItemInfo.id);
    } else {
      await deleteDocument(deleteItemInfo.id);
    }
    message.success("删除成功");
    fetchFolderContents(); // 刷新内容
    deleteDialogVisible.value = false;
  } catch (error) {
    console.error("删除失败", error);
    message.error("删除失败");
  } finally {
    processing.value = false;
  }
};

// 处理添加文件夹
const handleAddFolder = () => {
  newFolderForm.name = "";
  newFolderDialogVisible.value = true;
};

// 确认创建文件夹
const confirmCreateFolder = async () => {
  if (!newFolderForm.name.trim()) {
    message.warning("文件夹名称不能为空");
    return;
  }

  processing.value = true;
  try {
    await createFolder({
      parentId: currentFolderId.value,
      name: newFolderForm.name,
    });
    message.success("文件夹创建成功");
    fetchFolderContents(); // 刷新内容
    newFolderDialogVisible.value = false;
  } catch (error) {
    console.error("创建文件夹失败", error);
    message.error("创建文件夹失败");
  } finally {
    processing.value = false;
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
  // 文档下载逻辑
  message.info("开始下载文档...");
};

// 监听路由参数变化
watch(
  () => route.params.id,
  (newId) => {
    if (newId) {
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
  padding: 16px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
    0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.folder-header {
  padding: 0;
  margin-bottom: 16px;
}

.folder-content {
  margin-top: 16px;
}

/* 表格行样式 */
:deep(.folder-row) {
  cursor: pointer;
  transition: background-color 0.3s;
}

:deep(.folder-row:hover) {
  background-color: #f5f5f5;
}

.item-name-cell {
  cursor: pointer;
  padding: 8px 0;
  display: flex;
  align-items: center;
}

.folder-icon {
  color: #1890ff;
  font-size: 18px;
}

.document-icon {
  color: #f56a00;
  font-size: 18px;
}

.item-name {
  padding-left: 8px;
}

.item-name.is-folder {
  color: #1890ff;
  font-weight: 500;
}

/* 覆盖ant下拉菜单的样式，确保事件不冲突 */
:deep(.ant-dropdown-link) {
  padding: 5px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

:deep(.ant-dropdown-link:hover) {
  background-color: rgba(0, 0, 0, 0.03);
}
</style>
