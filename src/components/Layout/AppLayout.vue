<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <img src="@/assets/logo.png" alt="Drive Logo" class="logo" />
        <span class="logo-text">文献管理</span>
      </div>
      <div class="header-center">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文献、作者、DOI号等"
          prefix-icon="Search"
          class="search-input"
          @keyup.enter="handleSearch"
          @focus="showSearchResults = true"
          @blur="hideSearchResultsDelayed"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <!-- 搜索结果浮层 -->
        <div v-show="showSearchResults && searchQuery" class="search-results">
          <div v-if="searching" class="search-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在搜索...</span>
          </div>
          <div
            v-else-if="searchResults.length === 0 && searchQuery"
            class="no-results"
          >
            未找到匹配"{{ searchQuery }}"的结果
          </div>
          <ul v-else class="results-list">
            <li
              v-for="(result, index) in searchResults"
              :key="index"
              @click="navigateToResult(result)"
              class="result-item"
            >
              <el-icon :size="18" class="result-icon">
                <Folder v-if="result.type === 'folder'" />
                <Document v-else />
              </el-icon>
              <div class="result-content">
                <div class="result-name">{{ result.name }}</div>
                <div class="result-info">
                  <span class="result-type">{{
                    getResultTypeLabel(result.type)
                  }}</span>
                  <span v-if="result.matchField" class="result-match">
                    匹配: {{ getMatchFieldLabel(result.matchField) }}
                  </span>
                </div>
              </div>
            </li>
          </ul>
          <div v-if="searchResults.length > 0" class="view-all">
            <el-button
              type="text"
              @click="viewAllResults"
              class="view-all-button"
            >
              查看全部结果
            </el-button>
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-tooltip content="Settings" placement="bottom">
          <el-button circle>
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="Apps" placement="bottom">
          <el-button circle>
            <el-icon><Grid /></el-icon>
          </el-button>
        </el-tooltip>
        <el-avatar :size="32" class="user-avatar">U</el-avatar>
      </div>
    </header>

    <!-- 主内容区域 -->
    <div class="app-main">
      <!-- 侧边栏导航 -->
      <aside class="app-sidebar">
        <div class="new-button-container">
          <el-button type="primary" class="new-button" @click="goToUpload">
            <el-icon><Plus /></el-icon>
            New
          </el-button>
        </div>

        <!-- 文件夹树形导航 -->
        <FolderTree class="folder-tree" />

        <!-- 快捷导航菜单 -->
        <div class="quick-links">
          <el-menu default-active="1" class="sidebar-menu">
            <el-menu-item index="3">
              <el-icon><Monitor /></el-icon>
              <span>Computers</span>
            </el-menu-item>
            <el-menu-item index="4">
              <el-icon><Share /></el-icon>
              <span>Shared with me</span>
            </el-menu-item>
            <el-menu-item index="5">
              <el-icon><Clock /></el-icon>
              <span>Recent</span>
            </el-menu-item>
            <el-menu-item index="6">
              <el-icon><Star /></el-icon>
              <span>Starred</span>
            </el-menu-item>
          </el-menu>
        </div>
      </aside>

      <!-- 内容区域 -->
      <main class="app-content">
        <slot></slot>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import {
  Search,
  Setting,
  Grid,
  Plus,
  Monitor,
  Share,
  Clock,
  Star,
  Folder,
  Document,
  Loading,
} from "@element-plus/icons-vue";
import FolderTree from "@/components/FolderTree.vue";
import { searchLibrary } from "@/api/load";
import { ElMessage } from "element-plus";

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

const router = useRouter();
const searchQuery = ref("");
const searching = ref(false);
const searchResults = ref<SearchResult[]>([]);
const showSearchResults = ref(false);
let hideResultsTimeout: number | null = null;

// 添加导航到上传页面的方法
const goToUpload = () => {
  router.push("/upload");
};

// 删除实时搜索功能，仅保留回车键搜索
// 处理回车键搜索
const handleSearch = async () => {
  if (searchQuery.value.trim()) {
    await performSearch();

    // 如果没有结果，显示空结果提示
    if (searchResults.value.length === 0) {
      showSearchResults.value = true;
    }

    // 如果搜索结果超过5个，自动跳转到搜索结果页
    if (searchResults.value.length > 5) {
      viewAllResults();
    }
  }
};

// 执行搜索
const performSearch = async () => {
  searching.value = true;

  try {
    const response = await searchLibrary(searchQuery.value);
    searchResults.value = response.data.results || [];
    showSearchResults.value = true; // 显示搜索结果
  } catch (error) {
    console.error("搜索失败", error);
    ElMessage.error("搜索失败，请稍后重试");
    searchResults.value = [];
  } finally {
    searching.value = false;
  }
};

// 导航到结果
const navigateToResult = (result: SearchResult) => {
  if (result.type === "folder") {
    router.push(`/folder/${result.id}`);
  } else {
    router.push(`/document/${result.id}`);
  }
  showSearchResults.value = false;
};

// 查看全部结果
const viewAllResults = () => {
  router.push({
    path: "/search",
    query: { q: searchQuery.value },
  });
  showSearchResults.value = false;
};

// 获取结果类型标签
const getResultTypeLabel = (type: string): string => {
  switch (type) {
    case "folder":
      return "文件夹";
    case "document":
      return "文献";
    default:
      return "未知类型";
  }
};

// 获取匹配字段标签
const getMatchFieldLabel = (field?: string): string => {
  switch (field) {
    case "title":
      return "标题";
    case "author":
      return "作者";
    case "doi":
      return "DOI";
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

// 延迟隐藏搜索结果
const hideSearchResultsDelayed = () => {
  hideResultsTimeout = window.setTimeout(() => {
    showSearchResults.value = false;
  }, 200);
};

// 清理组件销毁前的超时
onUnmounted(() => {
  if (hideResultsTimeout) {
    clearTimeout(hideResultsTimeout);
  }
});
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
  width: 240px;
}

.logo {
  height: 40px;
  width: 40px;
}

.logo-text {
  font-size: 22px;
  font-weight: 500;
  margin-left: 8px;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  position: relative;
}

.search-input {
  width: 60%;
  max-width: 720px;
}

/* 搜索结果样式 */
.search-results {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: calc(60% - 2px);
  max-width: 718px;
  background-color: white;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 10;
  margin-top: 2px;
  max-height: 400px;
  overflow-y: auto;
}

.search-loading,
.no-results {
  padding: 15px;
  text-align: center;
  color: #909399;
}

.search-loading .el-icon {
  margin-right: 5px;
}

.results-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.result-item {
  padding: 10px 15px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.result-icon {
  color: #409eff;
  margin-right: 10px;
}

.result-content {
  flex: 1;
}

.result-name {
  font-weight: 500;
}

.result-info {
  font-size: 12px;
  color: #909399;
  margin-top: 3px;
}

.result-type {
  background-color: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
}

.result-match {
  color: #67c23a;
}

.view-all {
  padding: 10px;
  text-align: center;
  border-top: 1px solid #ebeef5;
}

.view-all-button {
  color: #409eff;
}

/* 其他已有样式保持不变 */
.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 240px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  padding-top: 16px;
}

.new-button-container {
  padding: 0 16px 16px 16px;
}

.new-button {
  width: 100%;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.sidebar-menu {
  border-right: none;
}

.folder-tree {
  margin-bottom: 16px;
}

.quick-links {
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
}

.app-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.el-menu-item {
  height: 40px;
  line-height: 40px;
}
</style>
