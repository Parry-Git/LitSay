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
        <el-tag v-if="useRegex" size="small" closable @close="clearRegexSearch">
          正则表达式搜索
        </el-tag>
        <el-tag
          v-if="keywordsAnd.length > 0"
          size="small"
          closable
          @close="clearKeywordsAnd"
        >
          关键词(与): {{ keywordsAnd.join(", ") }}
        </el-tag>
        <el-tag
          v-if="keywordsOr.length > 0"
          size="small"
          closable
          @close="clearKeywordsOr"
        >
          关键词(或): {{ keywordsOr.join(", ") }}
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

      <div class="search-filters" v-if="!isAdvancedSearch">
        <el-radio-group
          v-model="activeFilter"
          size="small"
          @change="filterResults"
        >
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="document">文献</el-radio-button>
          <el-radio-button label="author">作者</el-radio-button>
          <el-radio-button label="institution">机构</el-radio-button>
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
      <div v-else class="results-container">
        <!-- 文献结果 -->
        <div
          v-if="showCategoryResults('document').length > 0"
          class="result-category"
        >
          <div class="category-header">
            <FileOutlined class="category-icon document-icon" />
            <h3>文献</h3>
          </div>
          <div class="result-items">
            <div
              v-for="item in showCategoryResults('document')"
              :key="'doc-' + item.id"
              class="result-item"
              @click="handleItemClick(item)"
            >
              <div class="item-content">
                <div class="item-title">{{ item.name }}</div>
                <div class="item-path" v-if="item.path">{{ item.path }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 作者结果 - 仅在非高级搜索时显示 -->
        <div
          v-if="!isAdvancedSearch && showCategoryResults('author').length > 0"
          class="result-category"
        >
          <div class="category-header">
            <UserOutlined class="category-icon author-icon" />
            <h3>作者</h3>
          </div>
          <div class="result-items">
            <div
              v-for="item in showCategoryResults('author')"
              :key="'author-' + item.id"
              class="result-item"
              @click="handleItemClick(item)"
            >
              <div class="item-content">
                <div class="item-title">{{ item.name }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 机构结果 - 仅在非高级搜索时显示 -->
        <div
          v-if="
            !isAdvancedSearch && showCategoryResults('institution').length > 0
          "
          class="result-category"
        >
          <div class="category-header">
            <BankOutlined class="category-icon institution-icon" />
            <h3>机构</h3>
          </div>
          <div class="result-items">
            <div
              v-for="item in showCategoryResults('institution')"
              :key="'inst-' + item.id"
              class="result-item"
              @click="handleItemClick(item)"
            >
              <div class="item-content">
                <div class="item-title">{{ item.name }}</div>
                <div class="item-path" v-if="item.path">{{ item.path }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Document, Folder } from "@element-plus/icons-vue";
import { searchLibrary } from "@/api/load";
import {
  FileOutlined,
  UserOutlined,
  BankOutlined,
} from "@ant-design/icons-vue";

interface SearchResult {
  id: string | number;
  name: string;
  type: "document" | "folder" | "author" | "institution";
  matchField?: string;
  path?: string;
}

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const searchQuery = ref("");
const searchResults = ref<SearchResult[]>([]);
const activeFilter = ref("all");

const searchFields = ref<string[]>([]);
const dateRange = ref({ from: "", to: "" });
const documentType = ref("");
const authorCount = ref("");
const uploadTime = ref("");
const useRegex = ref(false);
const keywordsAnd = ref<string[]>([]);
const keywordsOr = ref<string[]>([]);

const hasAdvancedFilters = computed(() => {
  return (
    searchFields.value.length > 0 ||
    dateRange.value.from ||
    dateRange.value.to ||
    documentType.value ||
    authorCount.value ||
    uploadTime.value ||
    useRegex.value ||
    keywordsAnd.value.length > 0 ||
    keywordsOr.value.length > 0
  );
});

const isAdvancedSearch = computed(() => {
  return (
    useRegex.value ||
    dateRange.value.from ||
    dateRange.value.to ||
    keywordsAnd.value.length > 0 ||
    keywordsOr.value.length > 0 ||
    documentType.value ||
    authorCount.value ||
    uploadTime.value
  );
});

const filteredResults = computed(() => {
  let results = searchResults.value;

  if (isAdvancedSearch.value) {
    results = results.filter((item) => item.type === "document");
  } else if (activeFilter.value !== "all") {
    results = results.filter((item) => item.type === activeFilter.value);
  }

  return results;
});

const showCategoryResults = (category: string) => {
  if (isAdvancedSearch.value && category !== "document") {
    return [];
  }

  if (activeFilter.value !== "all" && activeFilter.value !== category) {
    return [];
  }
  return searchResults.value.filter((item) => item.type === category);
};

const performSearch = async () => {
  // if (!searchQuery.value) return;

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
      regex: useRegex.value,
      keywordsAnd: keywordsAnd.value,
      keywordsOr: keywordsOr.value,
    };
    console.log("搜索值:", searchQuery.value);

    const response = await searchLibrary(searchQuery.value, searchParams);
    searchResults.value = response.data.data?.results || [];
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

      // 解析高级搜索参数 - 精简版
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
      useRegex.value = newQuery.regex === "1";
      keywordsAnd.value = newQuery.keywordsAnd
        ? (newQuery.keywordsAnd as string).split(",")
        : [];
      keywordsOr.value = newQuery.keywordsOr
        ? (newQuery.keywordsOr as string).split(",")
        : [];

      performSearch();
    }
  },
  { deep: true }
);

// 筛选结果 - 移除重置页码的代码
const filterResults = () => {
  // 切换筛选不再重置页码
  // currentPage.value = 1;
};

// 处理点击项目
const handleItemClick = (row: SearchResult) => {
  if (row.type === "document") {
    router.push(`/document/${row.id}`);
  } else if (row.type === "author") {
    router.push(`/author/${row.id}`);
  } else if (row.type === "institution") {
    router.push(`/institution/${row.id}`);
  }
  // 其他类型暂不处理点击事件
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

// 清除正则表达式搜索
const clearRegexSearch = () => {
  useRegex.value = false;
  updateSearch();
};

// 清除关键词（与）搜索
const clearKeywordsAnd = () => {
  keywordsAnd.value = [];
  updateSearch();
};

// 清除关键词（或）搜索
const clearKeywordsOr = () => {
  keywordsOr.value = [];
  updateSearch();
};

// 清除所有筛选
const clearAllFilters = () => {
  searchFields.value = [];
  dateRange.value = { from: "", to: "" };
  documentType.value = "";
  authorCount.value = "";
  uploadTime.value = "";
  useRegex.value = false;
  keywordsAnd.value = [];
  keywordsOr.value = [];
  updateSearch();
};

// 更新搜索，保留当前关键词
const updateSearch = () => {
  router.push({
    path: "/search",
    query: {
      q: searchQuery.value,
      ...(useRegex.value ? { regex: "1" } : {}),
      ...(searchFields.value.length
        ? { fields: searchFields.value.join(",") }
        : {}),
      ...(dateRange.value.from ? { dateFrom: dateRange.value.from } : {}),
      ...(dateRange.value.to ? { dateTo: dateRange.value.to } : {}),
      ...(keywordsAnd.value.length
        ? { keywordsAnd: keywordsAnd.value.join(",") }
        : {}),
      ...(keywordsOr.value.length
        ? { keywordsOr: keywordsOr.value.join(",") }
        : {}),
      ...(documentType.value ? { type: documentType.value } : {}),
      ...(authorCount.value ? { authors: authorCount.value } : {}),
      ...(uploadTime.value ? { uploadTime: uploadTime.value } : {}),
    },
  });
};

// 组件挂载时执行搜索
onMounted(() => {
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
  useRegex.value = route.query.regex === "true";
  keywordsAnd.value = route.query.keywordsAnd
    ? (route.query.keywordsAnd as string).split(",")
    : [];
  keywordsOr.value = route.query.keywordsOr
    ? (route.query.keywordsOr as string).split(",")
    : [];

  performSearch();
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

/* 分类结果样式 */
.results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-category {
  margin-bottom: 10px;
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #f0f0f0;
}

.category-icon {
  margin-right: 8px;
  font-size: 18px;
}

.document-icon {
  color: #1890ff;
}

.author-icon {
  color: #52c41a;
}

.institution-icon {
  color: #722ed1;
}

.category-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #202124;
}

.result-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  padding: 12px 16px;
  border-radius: 4px;
  transition: background-color 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  border-bottom: 1px dashed #f5f5f5;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.item-content {
  flex: 1;
}

.item-title {
  font-weight: 500;
  color: #1890ff;
  margin-bottom: 4px;
}

.item-path {
  font-size: 12px;
  color: #909399;
}

/* 移除分页容器样式 */
/* .pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
} */

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
