<template>
  <div class="folder-tree">
    <div class="folder-tree-header">
      <div class="title">文件夹</div>
      <a-button
        type="text"
        size="small"
        :loading="loading"
        @click="refreshFolderTree"
      >
        <template #icon>
          <reload-outlined />
        </template>
      </a-button>
    </div>

    <div class="folder-tree-content">
      <a-spin :spinning="loading">
        <a-tree
          v-if="treeData.length > 0"
          :tree-data="treeData"
          :default-expanded-keys="defaultExpandedKeys"
          :selected-keys="selectedKeys"
          @select="handleSelect"
          :replaceFields="{
            key: 'id',
            title: 'label',
            children: 'children',
          }"
          show-icon
          :switcherIcon="() => h(DownOutlined, { style: { fontSize: '10px' } })"
        >
          <template #icon="{ expanded }">
            <folder-filled v-if="expanded" class="folder-icon folder-open" />
            <folder-outlined v-else class="folder-icon folder-closed" />
          </template>

          <template #title="{ label, id }">
            <span v-if="editingKey === id">
              <a-input
                v-model:value="editingName"
                size="small"
                style="width: 100px"
                @pressEnter="handleRenameConfirm"
                @blur="handleRenameCancel"
                ref="editInput"
              />
            </span>
            <span v-else class="tree-node-title">
              {{ label }}
              <div class="node-actions">
                <a-dropdown :trigger="['click']">
                  <more-outlined
                    class="action-icon"
                    @click.stop="onNodeActionClick"
                  />
                  <template #overlay>
                    <a-menu @click="(e) => onMenuClick(e, id)">
                      <a-menu-item key="rename">
                        <edit-outlined /> 重命名
                      </a-menu-item>
                      <a-menu-item key="new">
                        <folder-add-outlined /> 添加子文件夹
                      </a-menu-item>
                      <a-menu-item key="delete" danger>
                        <delete-outlined /> 删除
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </div>
            </span>
          </template>
        </a-tree>
        <a-empty v-else description="暂无文件夹" />
      </a-spin>
    </div>

    <!-- Create folder dialog -->
    <a-modal
      v-model:visible="createModalVisible"
      title="新建文件夹"
      @ok="handleCreateFolder"
      :confirm-loading="confirmLoading"
    >
      <a-form :model="formState" layout="vertical">
        <a-form-item label="文件夹名称" required>
          <a-input
            v-model:value="formState.name"
            placeholder="请输入文件夹名称"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, onUnmounted, h } from "vue";
import { useRouter, useRoute } from "vue-router";
import { message, Modal } from "ant-design-vue";
import {
  FolderOutlined,
  FolderFilled,
  FolderAddOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  ReloadOutlined,
  DownOutlined,
} from "@ant-design/icons-vue";
import {
  getFolderStructure,
  createFolder,
  renameFolder,
  deleteFolder,
} from "@/api/load";
import { folderChangedBus } from "@/services/EventService";

// 路由相关
const router = useRouter();
const route = useRoute();

// 树数据
const treeData = ref<any[]>([]);
const loading = ref<boolean>(false);
const defaultExpandedKeys = ref<(string | number)[]>([]);
const selectedKeys = ref<(string | number)[]>([]);

// 编辑状态
const editingKey = ref<string | null>(null);
const editingName = ref<string>("");
const editInput = ref<HTMLInputElement | null>(null);

// 创建文件夹相关
const createModalVisible = ref<boolean>(false);
const confirmLoading = ref<boolean>(false);
const formState = ref({
  name: "",
  parentId: null as string | number | null,
});

// 获取文件夹树
const fetchFolderTree = async () => {
  loading.value = true;
  try {
    const response = await getFolderStructure();
    if (response && response.data && response.data.data) {
      treeData.value = response.data.data;

      // 自动展开第一层
      if (treeData.value.length > 0) {
        defaultExpandedKeys.value = [treeData.value[0].id];
      }

      // 根据当前路由选中当前文件夹
      if (route.params.id) {
        selectedKeys.value = [route.params.id];
      }
    }
  } catch (error) {
    console.error("获取文件夹结构失败", error);
    message.error("获取文件夹结构失败");
  } finally {
    loading.value = false;
  }
};

// 刷新文件夹树结构 - 用于手动刷新或接收到更新事件后刷新
const refreshFolderTree = () => {
  console.log("刷新文件夹树结构");
  fetchFolderTree();
};

// 选择文件夹
const handleSelect = (selectedKeys: (string | number)[], info: any) => {
  if (selectedKeys.length > 0) {
    const key = selectedKeys[0];
    router.push(`/folder/${key}`);
  }
};

// 点击节点操作图标
const onNodeActionClick = (e: Event) => {
  e.stopPropagation();
};

// 菜单点击处理
const onMenuClick = (e: any, nodeId: string | number) => {
  const { key } = e;

  switch (key) {
    case "new":
      formState.value.parentId = nodeId;
      formState.value.name = "";
      createModalVisible.value = true;
      break;
    case "rename":
      startRename(nodeId);
      break;
    case "delete":
      confirmDeleteFolder(nodeId);
      break;
  }
};

// 开始重命名
const startRename = (nodeId: string | number) => {
  // 查找节点名称
  const findNode = (nodes: any[], id: string | number): any => {
    for (const node of nodes) {
      if (node.id === id) {
        return node;
      }
      if (node.children) {
        const found = findNode(node.children, id);
        if (found) return found;
      }
    }
    return null;
  };

  const node = findNode(treeData.value, nodeId);
  if (node) {
    editingKey.value = nodeId;
    editingName.value = node.label;

    nextTick(() => {
      if (editInput.value) {
        editInput.value.focus();
      }
    });
  }
};

// 确认重命名
const handleRenameConfirm = async () => {
  if (!editingKey.value || !editingName.value.trim()) {
    handleRenameCancel();
    return;
  }

  try {
    const response = await renameFolder({
      folderId: editingKey.value,
      newName: editingName.value.trim(),
    });

    if (response?.data?.code === 0) {
      message.success("重命名成功");

      // 注意：不需要在这里调用 refreshFolderTree，因为 renameFolder API 会触发事件
    } else {
      message.error(response?.data?.message || "重命名失败");
    }
  } catch (error) {
    console.error("重命名文件夹失败:", error);
    message.error("重命名失败");
  } finally {
    editingKey.value = null;
  }
};

// 取消重命名
const handleRenameCancel = () => {
  editingKey.value = null;
  editingName.value = "";
};

// 处理创建文件夹
const handleCreateFolder = async () => {
  if (!formState.value.name) {
    message.warning("请输入文件夹名称");
    return;
  }

  confirmLoading.value = true;

  try {
    const response = await createFolder({
      parentId: formState.value.parentId || 1,
      name: formState.value.name,
    });

    if (response?.data?.code === 0) {
      message.success("创建文件夹成功");
      createModalVisible.value = false;

      // 注意：不需要在这里调用 refreshFolderTree，因为 createFolder API 会触发事件
    } else {
      message.error(response?.data?.message || "创建文件夹失败");
    }
  } catch (error) {
    console.error("创建文件夹失败:", error);
    message.error("创建文件夹失败");
  } finally {
    confirmLoading.value = false;
  }
};

// 确认删除文件夹
const confirmDeleteFolder = (folderId: string | number) => {
  Modal.confirm({
    title: "确认删除",
    content: "删除文件夹将同时删除其下的所有内容，且不可恢复，确认继续？",
    okType: "danger",
    onOk: async () => {
      try {
        const response = await deleteFolder(folderId);

        if (response?.data?.code === 0) {
          message.success("删除成功");

          // 如果当前路由是被删除的文件夹，则跳转回根目录
          if (route.params.id === folderId) {
            router.push("/");
          }

          // 注意：不需要在这里调用 refreshFolderTree，因为 deleteFolder API 会触发事件
        } else {
          message.error(response?.data?.message || "删除失败");
        }
      } catch (error) {
        console.error("删除文件夹失败:", error);
        message.error("删除失败");
      }
    },
  });
};

// 监听文件夹变化事件
onMounted(() => {
  // 初始加载文件夹结构
  fetchFolderTree();

  // 订阅文件夹结构变更事件
  folderChangedBus.on(() => {
    console.log("FolderTree 组件收到文件夹结构变更事件，正在刷新...");
    refreshFolderTree();
  });
});

// 清理事件监听
onUnmounted(() => {
  folderChangedBus.off();
});
</script>

<style scoped>
.folder-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Helvetica Neue", Arial, sans-serif;
}

.folder-tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.folder-tree-header .title {
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.folder-tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.tree-node-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: 13px;
  color: #333;
}

.node-actions {
  display: none;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.node-actions:hover {
  opacity: 1;
}

.tree-node-title:hover .node-actions {
  display: inline-block;
}

.action-icon {
  cursor: pointer;
  padding: 2px;
}

/* 设置文件夹图标颜色 */
.folder-icon {
  font-size: 14px;
}

.folder-closed {
  color: #91a7ff;
}

.folder-open {
  color: #4263eb;
}

/* 调整树的整体样式 */
:deep(.ant-tree) {
  font-size: 13px;
  background: transparent;
}

/* 减少缩进距离 */
:deep(.ant-tree-treenode) {
  padding: 0 0 2px 0 !important;
  margin: 0;
  line-height: 24px;
}

/* 优化树节点内容 */
:deep(.ant-tree-node-content-wrapper) {
  min-height: 24px;
  line-height: 24px;
  padding: 0 6px !important;
  transition: background-color 0.2s;
}

:deep(.ant-tree-switcher) {
  width: 18px;
  height: 24px;
  line-height: 24px;
  margin-right: 0;
}

/* 使树节点更紧凑 */
:deep(.ant-tree-indent-unit) {
  width: 12px !important;
}

/* 选中状态样式 */
:deep(.ant-tree-node-selected) {
  background-color: #e6f7ff !important;
}

:deep(.ant-tree-node-content-wrapper:hover) {
  background-color: #f5f5f5;
}
</style>
