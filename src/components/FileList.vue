<template>
  <div class="file-list-container">
    <h2>My Files</h2>
    <el-table :data="fileList" style="width: 100%">
      <el-table-column>
        <template #default="scope">
          <div class="file-item">
            <el-icon :size="24" class="file-icon">
              <component :is="getFileIcon(scope.row.type)" />
            </el-icon>
            <span class="file-name">{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="owner" label="Owner" width="180" />
      <el-table-column prop="lastModified" label="Last modified" width="180" />
      <el-table-column prop="size" label="File size" width="120" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Document, Folder, Picture } from "@element-plus/icons-vue";

const fileList = ref([
  {
    name: "Project Proposal.docx",
    type: "document",
    owner: "Me",
    lastModified: "2023-10-15",
    size: "256 KB",
  },
  {
    name: "Vacation Photos",
    type: "folder",
    owner: "Me",
    lastModified: "2023-09-22",
    size: "—",
  },
  {
    name: "Budget 2023.xlsx",
    type: "spreadsheet",
    owner: "John Doe",
    lastModified: "2023-10-10",
    size: "1.2 MB",
  },
  {
    name: "Profile Picture.jpg",
    type: "image",
    owner: "Me",
    lastModified: "2023-08-05",
    size: "3.4 MB",
  },
  {
    name: "Meeting Notes",
    type: "folder",
    owner: "Jane Smith",
    lastModified: "2023-10-18",
    size: "—",
  },
]);

const getFileIcon = (type: string) => {
  switch (type) {
    case "folder":
      return "Folder";
    case "image":
      return "Picture";
    default:
      return "Document";
  }
};
</script>

<style scoped>
.file-list-container {
  padding: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  color: #4285f4;
}

.file-name {
  font-size: 14px;
}
</style>
