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
          <a-button
            type="primary"
            @click="showReferenceStyleModal"
            style="background-color: #fa8c16; border-color: #fa8c16"
          >
            <template #icon><book-outlined /></template>
            参考文献表
          </a-button>
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
                  <file-text-outlined v-else class="document-icon" />
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

    <a-modal
      v-model:visible="referenceStyleVisible"
      title="选择参考文献格式"
      @ok="generateReferences"
      okText="生成参考文献"
      cancelText="取消"
    >
      <a-radio-group v-model:value="selectedReferenceStyle">
        <a-radio value="gbt7714"
          >China National Standard GB/T 7714-2015</a-radio
        >
        <a-radio value="apa">American Psychological Association (APA)</a-radio>
      </a-radio-group>
      <div class="style-info" v-if="selectedReferenceStyle">
        <a-alert
          :message="getReferenceStyleInfo(selectedReferenceStyle)"
          type="info"
          show-icon
        />
      </div>
    </a-modal>

    <a-modal
      v-model:visible="referenceResultVisible"
      title="参考文献列表"
      width="800px"
      @ok="copyToClipboard"
      okText="复制到剪贴板"
      cancelText="关闭"
    >
      <a-spin :spinning="generatingReferences">
        <div v-if="referenceList.length" class="reference-list-container">
          <a-typography>
            <a-typography-title :level="4">
              已生成 {{ referenceList.length }} 条参考文献
            </a-typography-title>
            <a-typography-paragraph>
              <span class="format-label">格式：</span>
              <a-tag color="blue">{{
                selectedReferenceStyle === "gbt7714" ? "GB/T 7714-2015" : "APA"
              }}</a-tag>
            </a-typography-paragraph>
          </a-typography>
          <a-divider />
          <div class="references-content">
            <!-- 修改列表渲染方式 -->
            <div v-if="selectedReferenceStyle === 'gbt7714'">
              <div
                v-for="(ref, index) in referenceList"
                :key="index"
                class="reference-item-gbt"
              >
                <span class="reference-number-gbt">[{{ index + 1 }}]</span>
                <span v-html="ref"></span>
              </div>
            </div>
            <ol v-else>
              <li v-for="(ref, index) in referenceList" :key="index">
                <div v-html="ref"></div>
              </li>
            </ol>
          </div>
        </div>
        <a-empty v-else description="未找到可用于生成参考文献的文献" />
      </a-spin>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { message } from "ant-design-vue";
import {
  FolderOutlined,
  FileTextOutlined,
  FolderAddOutlined,
  UploadOutlined,
  EditOutlined,
  DownloadOutlined,
  SettingOutlined,
  DeleteOutlined,
  MoreOutlined,
  BookOutlined,
} from "@ant-design/icons-vue";
import {
  getFolderContents,
  createFolder,
  deleteFolder,
  renameFolder,
  deleteDocument,
} from "@/api/load";
import { generateReferenceList } from "@/api/reference"; // 导入新的API函数

// 定义表格列
const columns = [
  {
    title: "名称",
    dataIndex: "name",
    key: "name",
    ellipsis: true,
  },
  {
    title: "操作",
    dataIndex: "actions",
    key: "actions",
    width: 80,
    align: "center",
  },
];

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const processing = ref(false);
const currentFolderId = ref<string | number>(
  typeof route.params.id === "string" ? route.params.id : "root"
);
const currentFolder = ref<any>({});
const folderContents = ref<any[]>([]);

const renameDialogVisible = ref(false);
const newFolderDialogVisible = ref(false);
const deleteDialogVisible = ref(false);
const renameForm = reactive({ id: "", type: "", newName: "" });
const newFolderForm = reactive({ name: "" });
const deleteItemName = ref("");
const deleteItemInfo = reactive({ id: "", type: "" });

const referenceStyleVisible = ref(false);
const selectedReferenceStyle = ref<string>("gbt7714"); // 默认选择国标格式
const referenceResultVisible = ref(false);
const generatingReferences = ref(false);
const referenceList = ref<string[]>([]);

const getItemDisplayName = (item: any): string => {
  return (
    item.name ||
    item.label ||
    `未命名${item.type === "folder" ? "文件夹" : "文献"}`
  );
};

const getFolderDisplayName = (): string => {
  if (currentFolder.value) {
    if (currentFolder.value.name || currentFolder.value.label) {
      return currentFolder.value.name || currentFolder.value.label;
    }
  }

  const id = currentFolderId.value;
  if (id === 1 || id === "1") return "首页";
  if (id === 2 || id === "2") return "我的文献库";
  if (id === "root") return "根目录";

  return `文件夹 ${id}`;
};

const fetchFolderContents = async () => {
  loading.value = true;
  try {
    const response = await getFolderContents(currentFolderId.value);
    // console.log("Folder contents response:", response);

    if (response && response.data && response.data.data) {
      const data = response.data.data;

      if (data.currentFolder && data.items) {
        currentFolder.value = data.currentFolder;
        folderContents.value = data.items || [];
      } else if (Array.isArray(data)) {
        folderContents.value = data;
        currentFolder.value = { id: currentFolderId.value };
      } else if (typeof data === "object") {
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
      currentFolder.value = response.currentFolder;
      folderContents.value = response.items;
    } else if (Array.isArray(response)) {
      folderContents.value = response;
      currentFolder.value = { id: currentFolderId.value };
    } else {
      folderContents.value = [];
      currentFolder.value = { id: currentFolderId.value };
    }

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

const goBack = () => {
  router.back();
};

const handleItemClick = (row: any) => {
  if (row.type === "folder") {
    router.push(`/folder/${row.id}`);
  } else {
    router.push(`/document/${row.id}`);
  }
};

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

const openRenameDialog = (item: any) => {
  renameForm.id = item.id;
  renameForm.type = item.type;
  renameForm.newName = getItemDisplayName(item);
  renameDialogVisible.value = true;
};

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

const openDeleteDialog = (item: any) => {
  deleteItemName.value = getItemDisplayName(item);
  deleteItemInfo.id = item.id;
  deleteItemInfo.type = item.type;
  deleteDialogVisible.value = true;
};

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

const handleAddFolder = () => {
  newFolderForm.name = "";
  newFolderDialogVisible.value = true;
};

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

const handleUpload = () => {
  router.push({
    path: "/upload",
    query: { folderId: currentFolderId.value.toString() },
  });
};

const downloadDocument = (documentId: string | number) => {
  message.info("开始下载文档...");
};

// 显示参考文献格式选择对话框
const showReferenceStyleModal = () => {
  referenceStyleVisible.value = true;
};

// 获取参考文献格式的详细描述
const getReferenceStyleInfo = (style: string): string => {
  if (style === "gbt7714") {
    return "中国国家标准 GB/T 7714-2015 格式，适用于中文学术论文";
  } else if (style === "apa") {
    return "American Psychological Association (APA) 格式，适用于英文学术论文";
  }
  return "";
};

// 生成参考文献
const generateReferences = async () => {
  if (!currentFolderId.value) {
    message.error("无法获取当前文件夹ID");
    return;
  }

  referenceStyleVisible.value = false;
  referenceResultVisible.value = true;
  generatingReferences.value = true;

  try {
    const response = await generateReferenceList(
      currentFolderId.value,
      selectedReferenceStyle.value
    );

    if (response.data?.code === 0) {
      referenceList.value = response.data.data || [];
      if (referenceList.value.length === 0) {
        message.info("当前文件夹中没有可用于生成参考文献的文献");
      }
    } else {
      message.error(response.data?.message || "生成参考文献失败");
      referenceList.value = [];
    }
  } catch (error) {
    console.error("生成参考文献出错", error);
    message.error("生成参考文献失败，请重试");
    referenceList.value = [];
  } finally {
    generatingReferences.value = false;
  }
};

const copyToClipboard = async () => {
  if (referenceList.value.length === 0) {
    message.warning("没有可复制的参考文献");
    return;
  }

  try {
    let formattedText = "";
    if (selectedReferenceStyle.value === "gbt7714") {
      formattedText = referenceList.value
        .map((ref, index) => `[${index + 1}] ${ref.replace(/<[^>]*>?/gm, "")}`) // 移除HTML标签
        .join("\n\n");
    } else {
      formattedText = referenceList.value
        .map((ref, index) => `${index + 1}. ${ref.replace(/<[^>]*>?/gm, "")}`) // 移除HTML标签
        .join("\n\n");
    }

    // 创建临时textarea元素以复制带格式的文本
    const textarea = document.createElement("textarea");
    textarea.value = formattedText;
    document.body.appendChild(textarea);
    textarea.select();

    const success = document.execCommand("copy");
    document.body.removeChild(textarea);

    if (success) {
      message.success("参考文献已复制到剪贴板");
      referenceResultVisible.value = false;
    } else {
      message.error("复制失败，请手动选择并复制");
    }
  } catch (error) {
    console.error("复制到剪贴板失败", error);
    message.error("复制到剪贴板失败");
  }
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

/* 添加参考文献相关样式 */
.style-info {
  margin-top: 16px;
}

.reference-list-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.references-content {
  max-height: 400px;
  overflow-y: auto;
  margin-top: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 16px 24px;
  background-color: #fafafa;
}

.references-content ol {
  padding-left: 20px;
}

.references-content li {
  margin-bottom: 12px;
  line-height: 1.6;
}

/* GB/T 7714 参考文献列表项样式 */
.reference-item-gbt {
  margin-bottom: 12px;
  line-height: 1.6;
  display: flex; /* 使用flex布局以便对齐 */
  align-items: flex-start; /* 顶部对齐 */
}

.reference-number-gbt {
  margin-right: 8px; /* 序号和内容之间的间距 */
  white-space: nowrap; /* 防止序号换行 */
}

.format-label {
  font-weight: 500;
}
</style>
