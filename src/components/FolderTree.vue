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

<script lang="ts">
import { defineComponent, ref } from "vue";
import { Folder, FolderOpened, Document } from "@element-plus/icons-vue";

export default defineComponent({
  name: "FolderTree",
  components: {
    Folder,
    FolderOpened,
    Document,
  },
  setup() {
    const folderData = ref([
      {
        id: 1,
        label: "Home",
        icon: "home",
      },
      {
        id: 2,
        label: "My Drive",
        icon: "folder",
        children: [
          {
            id: 21,
            label: "Colab Notebooks",
            icon: "folder",
            children: [],
          },
          {
            id: 22,
            label: "UMich EECS 498-007...",
            icon: "folder",
            children: [
              {
                id: 221,
                label: "2019_A4_pytorch",
                icon: "folder",
                children: [
                  {
                    id: 2211,
                    label: "A1",
                    icon: "folder",
                  },
                  {
                    id: 2212,
                    label: "A2",
                    icon: "folder",
                  },
                  {
                    id: 2213,
                    label: "A3",
                    icon: "folder",
                  },
                  {
                    id: 2214,
                    label: "A4",
                    icon: "folder",
                  },
                  {
                    id: 2215,
                    label: "A5",
                    icon: "folder",
                  },
                  {
                    id: 2216,
                    label: "A6",
                    icon: "folder",
                  },
                ],
              },
            ],
          },
        ],
      },
    ]);

    const defaultProps = {
      children: "children",
      label: "label",
    };

    const handleNodeClick = (data: any) => {
      console.log(data);
      // 这里可以添加点击文件夹时的逻辑，例如加载文件列表等
    };

    return {
      folderData,
      defaultProps,
      handleNodeClick,
    };
  },
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
