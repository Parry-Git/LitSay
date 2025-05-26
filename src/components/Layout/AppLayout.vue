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
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #suffix>
            <el-popover
              placement="bottom-end"
              :width="400"
              trigger="click"
              v-model:visible="showAdvancedSearch"
              popper-class="advanced-search-popover"
              @show="handlePopoverShow"
              @hide="handlePopoverHide"
            >
              <!-- 高级搜索表单 -->
              <template #default>
                <div class="advanced-search-form">
                  <h3 class="advanced-search-title">高级搜索</h3>

                  <el-form
                    :model="advancedSearchForm"
                    label-position="top"
                    size="small"
                  >
                    <!-- 按关键字搜索字段 -->
                    <el-form-item label="关键字类型">
                      <el-checkbox-group
                        v-model="advancedSearchForm.searchFields"
                      >
                        <el-checkbox label="title">标题</el-checkbox>
                        <el-checkbox label="author">作者</el-checkbox>
                        <el-checkbox label="doi">DOI号</el-checkbox>
                        <el-checkbox label="affiliation">作者单位</el-checkbox>
                        <el-checkbox label="conference">会议名</el-checkbox>
                      </el-checkbox-group>
                    </el-form-item>

                    <!-- 发布时间范围 -->
                    <el-form-item label="发布时间范围">
                      <el-date-picker
                        v-model="advancedSearchForm.dateRange"
                        type="daterange"
                        range-separator="至"
                        start-placeholder="开始日期"
                        end-placeholder="结束日期"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        style="width: 100%"
                      />
                    </el-form-item>

                    <!-- 文件类型 -->
                    <el-form-item label="文献类型">
                      <el-select
                        v-model="advancedSearchForm.documentType"
                        placeholder="选择文献类型"
                        style="width: 100%"
                        clearable
                      >
                        <el-option label="论文" value="paper" />
                        <el-option label="期刊" value="journal" />
                        <el-option label="会议报告" value="conference" />
                        <el-option label="书籍" value="book" />
                        <el-option label="其他" value="other" />
                      </el-select>
                    </el-form-item>

                    <!-- 作者数量 -->
                    <el-form-item label="作者数量">
                      <el-select
                        v-model="advancedSearchForm.authorCount"
                        placeholder="作者数量"
                        style="width: 100%"
                        clearable
                      >
                        <el-option label="单作者" value="single" />
                        <el-option label="2-3名作者" value="few" />
                        <el-option label="4名以上作者" value="many" />
                      </el-select>
                    </el-form-item>

                    <!-- 上传时间范围 -->
                    <el-form-item label="上传时间范围">
                      <el-select
                        v-model="advancedSearchForm.uploadTime"
                        placeholder="选择上传时间"
                        style="width: 100%"
                        clearable
                      >
                        <el-option label="最近一周" value="lastWeek" />
                        <el-option label="最近一个月" value="lastMonth" />
                        <el-option label="最近三个月" value="lastThreeMonths" />
                        <el-option label="最近半年" value="lastSixMonths" />
                        <el-option label="最近一年" value="lastYear" />
                      </el-select>
                    </el-form-item>

                    <div class="form-actions">
                      <el-button @click="resetAdvancedSearch">重置</el-button>
                      <el-button type="primary" @click="performAdvancedSearch"
                        >搜索</el-button
                      >
                    </div>
                  </el-form>
                </div>
              </template>
            </el-popover>
          </template>
        </el-input>
      </div>

      <!-- 修改的头部右侧区域 -->
      <div class="header-right">
        <!-- 用户方框和下拉菜单 -->
        <a-dropdown :trigger="['click']" placement="bottomRight">
          <div class="user-info-trigger">
            <div class="username-box">
              {{ truncatedUsername }}
            </div>
            <down-outlined />
          </div>

          <template #overlay>
            <a-menu>
              <a-menu-item key="profile" @click="showUserDrawer = true">
                <template #icon><user-outlined /></template>
                个人资料
              </a-menu-item>
              <a-menu-item key="settings">
                <template #icon><setting-outlined /></template>
                设置
              </a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout" @click="handleLogout">
                <template #icon><logout-outlined /></template>
                退出登录
              </a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </header>

    <!-- 主内容区域 -->
    <div class="app-main">
      <!-- 侧边栏导航 -->
      <aside class="app-sidebar">
        <div class="new-button-container">
          <a-button type="primary" class="new-button" @click="goToUpload">
            <template #icon><plus-outlined /></template>
            上传文献
          </a-button>
        </div>

        <!-- 文件夹树形导航 -->
        <FolderTree class="folder-tree" />

        <!-- 统计按钮 -->
        <div class="stats-button-container">
          <a-button class="stats-button" type="text" block @click="goToStats">
            <template #icon><bar-chart-outlined /></template>
            统计分析
          </a-button>
        </div>
      </aside>

      <!-- 内容区域 -->
      <main class="app-content">
        <slot></slot>
      </main>
    </div>

    <!-- 用户控制浮窗 -->
    <a-drawer
      title="个人资料"
      :visible="showUserDrawer"
      @close="showUserDrawer = false"
      placement="right"
      :width="360"
      :mask-style="{ backgroundColor: 'rgba(0, 0, 0, 0.45)' }"
    >
      <div class="user-profile">
        <div class="user-profile-header">
          <div class="profile-username-box">
            {{ userInfo.username || "未登录用户" }}
          </div>
          <div class="profile-info">
            <h2>{{ userInfo.username || "未登录用户" }}</h2>
            <p>{{ userInfo.role === "admin" ? "管理员" : "普通用户" }}</p>
          </div>
        </div>

        <a-divider />

        <div class="profile-details">
          <h3>账号信息</h3>

          <a-descriptions :column="1">
            <a-descriptions-item label="用户名">
              {{ userInfo.username || "未登录" }}
            </a-descriptions-item>
            <a-descriptions-item label="用户角色">
              {{ userInfo.role === "admin" ? "管理员" : "普通用户" }}
            </a-descriptions-item>
            <a-descriptions-item label="ID">
              {{ userInfo.id || "N/A" }}
            </a-descriptions-item>
            <a-descriptions-item label="创建时间">
              {{ userInfo.createdAt || "未知" }}
            </a-descriptions-item>
          </a-descriptions>
        </div>

        <a-divider />

        <div class="profile-actions">
          <a-button type="primary" block @click="handleEditProfile"
            >编辑资料</a-button
          >
          <a-button style="margin-top: 16px" block @click="handleChangePassword"
            >修改密码</a-button
          >
          <a-button
            type="danger"
            style="margin-top: 16px"
            block
            @click="handleLogout"
          >
            退出登录
          </a-button>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, reactive, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  Search,
  Plus,
  Folder,
  Document,
  Loading,
  Filter,
} from "@element-plus/icons-vue";

// 修改导入方式，直接导入所需图标
import UserOutlined from "@ant-design/icons-vue/UserOutlined";
import SettingOutlined from "@ant-design/icons-vue/SettingOutlined";
import LogoutOutlined from "@ant-design/icons-vue/LogoutOutlined";
import DownOutlined from "@ant-design/icons-vue/DownOutlined";
import BarChartOutlined from "@ant-design/icons-vue/BarChartOutlined";
import PlusOutlined from "@ant-design/icons-vue/PlusOutlined";

import FolderTree from "@/components/FolderTree.vue";
import { searchLibrary } from "@/api/load";
import { logout } from "@/api/auth";
import { useEventBus } from "@vueuse/core";

// 添加这一行解决showUserDrawer未定义的问题
const showUserDrawer = ref(false);

// 注册图标组件，使其在模板中可用
const icons = {
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DownOutlined,
  BarChartOutlined,
  PlusOutlined,
};

// 定义搜索结果类型
interface SearchResult {
  id: string | number;
  name: string;
  type: "document" | "folder";
  matchField?: string; // 修改为接受任意字符串
  path?: string;
}

// 定义高级搜索表单类型
interface AdvancedSearchForm {
  searchFields: string[];
  dateRange: [string, string] | null;
  documentType: string | null;
  authorCount: string | null;
  uploadTime: string | null;
}

// 用户信息类型
interface UserInfo {
  username: string;
  role: string;
  id: string;
  createdAt?: string;
}

const router = useRouter();
const searchQuery = ref("");
const showAdvancedSearch = ref(false);

// 移除搜索结果相关的变量
// const searching = ref(false);
// const searchResults = ref<SearchResult[]>([]);
// const showSearchResults = ref(false);
// let hideResultsTimeout: number | null = null;

// 高级搜索相关
const advancedSearchForm = ref<AdvancedSearchForm>({
  searchFields: ["title", "author", "doi"],
  dateRange: null,
  documentType: null,
  authorCount: null,
  uploadTime: null,
});

// 用户信息
const userInfo = reactive<UserInfo>({
  username: "",
  role: "",
  id: "",
});

// 计算缩略后的用户名
const truncatedUsername = computed(() => {
  if (!userInfo.username) return "用户";
  return userInfo.username.length > 8
    ? `${userInfo.username.substring(0, 8)}...`
    : userInfo.username;
});

// 添加登录状态的计算属性
const isLoggedIn = computed(() => {
  return localStorage.getItem("token") !== null;
});

// 获取用户信息
const getUserInfo = () => {
  // 从 localStorage 获取用户信息
  const storedUserInfo = localStorage.getItem("userInfo");
  if (storedUserInfo) {
    try {
      const parsedInfo = JSON.parse(storedUserInfo);
      userInfo.username = parsedInfo.username || "";
      userInfo.role = parsedInfo.role || "";
      userInfo.id = parsedInfo.id || "";
      userInfo.createdAt = parsedInfo.createdAt || "2023-01-01";
    } catch (e) {
      console.error("解析用户信息失败", e);
    }
  }
};

// 添加导航到上传页面的方法
const goToUpload = () => {
  router.push("/upload");
};

// 添加导航到统计页面的方法
const goToStats = () => {
  router.push("/stats");
};

// 处理回车键搜索 - 修改为直接跳转到搜索结果页面
const handleSearch = () => {
  if (searchQuery.value.trim()) {
    // 直接跳转到搜索结果页面
    router.push({
      path: "/search",
      query: { q: searchQuery.value },
    });
  }
};

// 执行高级搜索
const performAdvancedSearch = () => {
  // 构建高级搜索查询参数
  const advancedParams = {
    q: searchQuery.value,
    fields: advancedSearchForm.value.searchFields.join(","),
    dateFrom: advancedSearchForm.value.dateRange?.[0] || "",
    dateTo: advancedSearchForm.value.dateRange?.[1] || "",
    type: advancedSearchForm.value.documentType || "",
    authors: advancedSearchForm.value.authorCount || "",
    uploadTime: advancedSearchForm.value.uploadTime || "",
  };

  // 跳转到搜索结果页面，带上高级搜索参数
  router.push({
    path: "/search",
    query: advancedParams,
  });

  showAdvancedSearch.value = false;
};

// 重置高级搜索表单
const resetAdvancedSearch = () => {
  advancedSearchForm.value = {
    searchFields: ["title", "author", "doi"],
    dateRange: null,
    documentType: null,
    authorCount: null,
    uploadTime: null,
  };
};

// 处理Popover显示
const handlePopoverShow = () => {
  // 显示高级搜索时，防止搜索结果浮层显示
  // showSearchResults.value = false;
};

// 处理Popover隐藏
const handlePopoverHide = () => {
  // 可以添加一些额外的逻辑
};

// 保留获取匹配字段标签的方法，可能在其他地方使用
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

// 处理登出
const handleLogout = async () => {
  try {
    // 判断是否为管理员
    const isAdmin = userInfo.role === "admin";

    await logout();

    // 清除显示的用户信息
    userInfo.username = "";
    userInfo.role = "";
    userInfo.id = "";
    userInfo.createdAt = "";

    // 关闭用户抽屉如果已打开
    showUserDrawer.value = false;

    ElMessage.success(isAdmin ? "管理员退出成功" : "退出成功");
    router.push("/login");
  } catch (error) {
    console.error("登出失败", error);
    ElMessage.error("登出失败，请重试");

    // 即使API调用失败，也尝试重定向到登录页面
    router.push("/login");
  }
};

// 编辑个人资料
const handleEditProfile = () => {
  ElMessage.info("编辑个人资料功能开发中...");
};

// 修改密码
const handleChangePassword = () => {
  ElMessage.info("修改密码功能开发中...");
};

// 创建一个事件总线用于跨组件通信
const folderChangedBus = useEventBus("folder-changed");

// 组件挂载时获取用户信息
onMounted(() => {
  getUserInfo();
});
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Helvetica Neue", Arial, sans-serif;
}

.app-header {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  height: 64px;
  background-color: #ffffff;
}

.header-left {
  display: flex;
  align-items: center;
  width: 220px;
}

.logo {
  height: 40px;
  width: 40px;
}

.logo-text {
  font-size: 18px;
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

/* 头部右侧样式 */
.header-right {
  display: flex;
  align-items: center;
}

.user-info-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info-trigger:hover {
  background-color: #f0f2f5;
}

/* 用户名方框样式 */
.username-box {
  height: 32px;
  padding: 0 10px;
  background-color: #f0f2f5;
  color: rgba(0, 0, 0, 0.85);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  font-size: 14px;
  border: 1px solid #e8e8e8;
  min-width: 80px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 用户资料抽屉样式 */
.user-profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

/* 个人资料页面中的用户名方框 */
.profile-username-box {
  height: 64px;
  width: 64px;
  background-color: #f0f2f5;
  color: rgba(0, 0, 0, 0.85);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 16px;
  font-weight: 500;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  text-overflow: ellipsis;
}

.profile-info h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.profile-info p {
  margin: 4px 0 0;
  color: rgba(0, 0, 0, 0.45);
}

.profile-details {
  margin-bottom: 24px;
}

.profile-details h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

/* 侧边栏样式 */
.app-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.app-sidebar {
  width: 220px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
}

.new-button-container {
  padding: 16px 12px 8px;
}

.new-button {
  width: 100%;
  border-radius: 6px;
  height: 36px;
  font-size: 14px;
  font-weight: 500;
}

.folder-tree {
  flex: 1;
  margin-top: 8px;
}

/* 统计按钮容器 */
.stats-button-container {
  padding: 8px 12px 16px;
  border-top: 1px solid #eaeaea;
}

.stats-button {
  height: 40px;
  text-align: left;
  font-size: 14px;
  color: #333;
  transition: background-color 0.3s;
}

.stats-button:hover {
  background-color: #e6f7ff;
  color: #1890ff;
}

.app-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #ffffff;
}

/* 高级搜索按钮样式 */
.advanced-search-button {
  margin-left: 5px;
  color: #606266;
}

.advanced-search-button:hover {
  color: #409eff;
}

/* 高级搜索表单样式 */
.advanced-search-form {
  padding: 0 10px;
}

.advanced-search-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 20px 0;
  text-align: center;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

:deep(.advanced-search-popover) {
  padding: 20px 0;
}
</style>
