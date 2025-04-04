<template>
  <div class="search-result-view">
    <div class="search-header">
      <h2>搜索结果: "{{ searchQuery }}"</h2>
      <div class="search-filters">
        <el-radio-group
          v-model="activeFilter"
          size="small"
          @change="filterResults"
        >
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="document">文献</el-radio-button>
          <el-radio-button label="folder">文件夹</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <el-divider />

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else>
      <div v-if="filteredResults.length === 0" class="empty-results">
        <el-empty description="没有找到匹配的结果" />
      </div>
      <el-table
        v-else
        :data="filteredResults"
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

        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag
              :type="row.type === 'folder' ? 'warning' : 'primary'"
              size="small"
            >
              {{ row.type === "folder" ? "文件夹" : "文献" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="匹配字段" width="150">
          <template #default="{ row }">
            <span v-if="row.matchField">
              {{ getMatchFieldLabel(row.matchField) }}
            </span>
            <span v-else>多字段</span>
          </template>
        </el-table-column>

        <el-table-column label="位置" width="220">
          <template #default="{ row }">
            <span v-if="row.path">{{ row.path }}</span>
            <span v-else>—</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="searchResults.length > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="searchResults.length"
          layout="prev, pager, next"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Folder, Document } from "@element-plus/icons-vue";
import { searchLibrary } from "@/api/load";

// 定义搜索结果类型
interface SearchResult {
  id: string | number;
  name: string;
  type: "document" | "folder";
  matchField?:
    | "title"
    | "author"
    | "doi"
    | "affiliation"
    | "conference"
    | "foldername";
  path?: string;
}

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const searchQuery = ref("");
const searchResults = ref<SearchResult[]>([]);
const activeFilter = ref("all");
const currentPage = ref(1);
const pageSize = ref(10);

// 根据筛选条件过滤结果
const filteredResults = computed(() => {
  let results = searchResults.value;

  // 应用类型筛选
  if (activeFilter.value !== "all") {
    results = results.filter((item) => item.type === activeFilter.value);
  }

  // 计算分页
  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;

  return results.slice(startIndex, endIndex);
});

// 监听查询参数变化
watch(
  () => route.query.q,
  (newQuery) => {
    if (newQuery) {
      searchQuery.value = newQuery as string;
      performSearch();
    }
  }
);

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value) return;

  loading.value = true;

  try {
    const response = await searchLibrary(searchQuery.value);
    searchResults.value = response.data.results || [];
    currentPage.value = 1; // 重置分页
  } catch (error) {
    console.error("搜索失败", error);
    ElMessage.error("搜索失败，请稍后重试");
    searchResults.value = [];
  } finally {
    loading.value = false;
  }
};

// 筛选结果
const filterResults = () => {
  currentPage.value = 1; // 切换筛选时重置页码
};

// 处理点击项目
const handleItemClick = (row: SearchResult) => {
  if (row.type === "folder") {
    router.push(`/folder/${row.id}`);
  } else {
    router.push(`/document/${row.id}`);
  }
};

// 获取匹配字段标签
const getMatchFieldLabel = (field?: string): string => {
  switch (field) {
    case "title":
      return "文献标题";
    case "author":
      return "作者";
    case "doi":
      return "DOI号";
    case "affiliation":
      return "作者单位";
    case "conference":
      return "会议名";
    case "foldername":
      return "文件夹名";
    default:
      return "多字段";
  }
};

// 组件挂载时执行搜索
onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q as string;
    performSearch();
  }
});
</script>

<style scoped>
.search-result-view {
  padding: 20px;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.empty-results {
  padding: 40px 0;
  display: flex;
  justify-content: center;
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
