<template>
  <div class="search-result-view">
    <div class="search-header">
      <h2>搜索结果: "{{ searchQuery }}"</h2>

      <!-- 高级搜索标签 -->
      <div class="search-tags" v-if="hasAdvancedFilters">
        <span class="filter-label">高级筛选:</span>
        <el-tag
          v-if="searchFields.length > 0"
          size="small"
          closable
          @close="clearSearchFields"
        >
          字段: {{ formatSearchFields(searchFields) }}
        </el-tag>
        <el-tag
          v-if="dateRange.from || dateRange.to"
          size="small"
          closable
          @close="clearDateRange"
        >
          日期: {{ formatDateRange(dateRange) }}
        </el-tag>
        <el-tag
          v-if="documentType"
          size="small"
          closable
          @close="clearDocumentType"
        >
          类型: {{ formatDocumentType(documentType) }}
        </el-tag>
        <el-tag
          v-if="authorCount"
          size="small"
          closable
          @close="clearAuthorCount"
        >
          作者: {{ formatAuthorCount(authorCount) }}
        </el-tag>
        <el-tag
          v-if="uploadTime"
          size="small"
          closable
          @close="clearUploadTime"
        >
          上传时间: {{ formatUploadTime(uploadTime) }}
        </el-tag>
        <el-button
          v-if="hasAdvancedFilters"
          type="text"
          size="small"
          @click="clearAllFilters"
        >
          清除全部
        </el-button>
      </div>

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
  matchField?: string; // 修改为接受任意字符串，而不是限定的联合类型
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

// 高级搜索相关参数
const searchFields = ref<string[]>([]);
const dateRange = ref({ from: "", to: "" });
const documentType = ref("");
const authorCount = ref("");
const uploadTime = ref("");

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

// 判断是否有高级筛选
const hasAdvancedFilters = computed(() => {
  return (
    searchFields.value.length > 0 ||
    dateRange.value.from ||
    dateRange.value.to ||
    documentType.value ||
    authorCount.value ||
    uploadTime.value
  );
});

// 执行搜索 (支持高级搜索参数)
const performSearch = async () => {
  if (!searchQuery.value) return;

  loading.value = true;

  try {
    // 构建高级搜索参数
    const searchParams = {
      fields: searchFields.value,
      dateFrom: dateRange.value.from,
      dateTo: dateRange.value.to,
      type: documentType.value,
      authors: authorCount.value,
      uploadTime: uploadTime.value,
    };

    const response = await searchLibrary(searchQuery.value, searchParams);
    searchResults.value = response.data.data?.results || [];
    currentPage.value = 1; // 重置分页
  } catch (error) {
    console.error("搜索失败", error);
    ElMessage.error("搜索失败，请稍后重试");
    searchResults.value = [];
  } finally {
    loading.value = false;
  }
};

// 监听查询参数变化
watch(
  () => route.query,
  (newQuery) => {
    if (newQuery.q) {
      searchQuery.value = newQuery.q as string;

      // 解析高级搜索参数
      searchFields.value = newQuery.fields
        ? (newQuery.fields as string).split(",")
        : [];
      dateRange.value = {
        from: (newQuery.dateFrom as string) || "",
        to: (newQuery.dateTo as string) || "",
      };
      documentType.value = (newQuery.type as string) || "";
      authorCount.value = (newQuery.authors as string) || "";
      uploadTime.value = (newQuery.uploadTime as string) || "";

      performSearch();
    }
  },
  { deep: true }
);

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

// 格式化搜索字段
const formatSearchFields = (fields: string[]) => {
  if (fields.length === 0) return "";

  const fieldMap: { [key: string]: string } = {
    title: "标题",
    author: "作者",
    doi: "DOI号",
    affiliation: "作者单位",
    conference: "会议名",
  };

  return fields.map((f) => fieldMap[f] || f).join(", ");
};

// 格式化日期范围
const formatDateRange = (range: { from: string; to: string }) => {
  if (!range.from && !range.to) return "";
  if (range.from && range.to) return `${range.from} 至 ${range.to}`;
  if (range.from) return `${range.from} 之后`;
  return `${range.to} 之前`;
};

// 格式化文档类型
const formatDocumentType = (type: string) => {
  const typeMap: { [key: string]: string } = {
    paper: "论文",
    journal: "期刊",
    conference: "会议报告",
    book: "书籍",
    other: "其他",
  };
  return typeMap[type] || type;
};

// 格式化作者数量
const formatAuthorCount = (count: string) => {
  const countMap: { [key: string]: string } = {
    single: "单作者",
    few: "2-3名作者",
    many: "4名以上作者",
  };
  return countMap[count] || count;
};

// 格式化上传时间
const formatUploadTime = (time: string) => {
  const timeMap: { [key: string]: string } = {
    lastWeek: "最近一周",
    lastMonth: "最近一个月",
    lastThreeMonths: "最近三个月",
    lastSixMonths: "最近半年",
    lastYear: "最近一年",
  };
  return timeMap[time] || time;
};

// 清除搜索字段筛选
const clearSearchFields = () => {
  searchFields.value = [];
  updateSearch();
};

// 清除日期范围筛选
const clearDateRange = () => {
  dateRange.value = { from: "", to: "" };
  updateSearch();
};

// 清除文档类型筛选
const clearDocumentType = () => {
  documentType.value = "";
  updateSearch();
};

// 清除作者数量筛选
const clearAuthorCount = () => {
  authorCount.value = "";
  updateSearch();
};

// 清除上传时间筛选
const clearUploadTime = () => {
  uploadTime.value = "";
  updateSearch();
};

// 清除所有筛选
const clearAllFilters = () => {
  searchFields.value = [];
  dateRange.value = { from: "", to: "" };
  documentType.value = "";
  authorCount.value = "";
  uploadTime.value = "";
  updateSearch();
};

// 更新搜索，保留当前关键词
const updateSearch = () => {
  router.push({
    path: "/search",
    query: {
      q: searchQuery.value,
      ...(searchFields.value.length
        ? { fields: searchFields.value.join(",") }
        : {}),
      ...(dateRange.value.from ? { dateFrom: dateRange.value.from } : {}),
      ...(dateRange.value.to ? { dateTo: dateRange.value.to } : {}),
      ...(documentType.value ? { type: documentType.value } : {}),
      ...(authorCount.value ? { authors: authorCount.value } : {}),
      ...(uploadTime.value ? { uploadTime: uploadTime.value } : {}),
    },
  });
};

// 组件挂载时执行搜索
onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q as string;

    // 解析高级搜索参数
    searchFields.value = route.query.fields
      ? (route.query.fields as string).split(",")
      : [];
    dateRange.value = {
      from: (route.query.dateFrom as string) || "",
      to: (route.query.dateTo as string) || "",
    };
    documentType.value = (route.query.type as string) || "";
    authorCount.value = (route.query.authors as string) || "";
    uploadTime.value = (route.query.uploadTime as string) || "";

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

/* 高级搜索标签样式 */
.search-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0;
  align-items: center;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 5px;
}
</style>
