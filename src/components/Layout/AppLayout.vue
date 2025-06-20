<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-left">
        <img src="@/assets/logo3.png" alt="Drive Logo" class="logo" />
        <span class="logo-text">文献一言</span>
      </div>
      <div class="header-center" ref="headerCenterRef">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文献、作者、DOI号等"
          prefix-icon="Search"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
          :disabled="showAdvancedSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #suffix>
            <el-button
              type="text"
              class="advanced-search-button"
              @click="toggleAdvancedSearch"
              :title="showAdvancedSearch ? '关闭高级搜索' : '打开高级搜索'"
            >
              <el-icon><Filter /></el-icon>
            </el-button>
          </template>
        </el-input>

        <a-popover
          placement="bottomRight"
          trigger="click"
          v-model:visible="showAdvancedSearch"
          :overlay-style="{ width: '380px' }"
          :get-popup-container="getPopupContainer"
        >
          <template #content>
            <div class="advanced-search-form-ant">
              <h3 class="advanced-search-title">高级搜索</h3>

              <a-form layout="vertical" :model="advancedSearchForm">
                <!-- 搜索内容 -->
                <a-form-item label="搜索内容">
                  <a-input-group compact>
                    <a-input
                      v-model:value="advancedSearchForm.query"
                      placeholder="输入搜索内容"
                      style="width: calc(100% - 92px)"
                    />
                    <a-tooltip title="启用正则表达式搜索">
                      <a-switch
                        v-model:checked="advancedSearchForm.useRegex"
                        checked-children="正则"
                        un-checked-children="普通"
                        class="regex-switch"
                      />
                    </a-tooltip>
                  </a-input-group>
                </a-form-item>

                <!-- 发布时间范围 -->
                <a-form-item label="发布时间范围">
                  <a-range-picker
                    v-model:value="dateRangeValue"
                    style="width: 100%"
                    format="YYYY-MM-DD"
                    :get-popup-container="(triggerNode) => getPopupContainer()"
                    @change="handleDateRangeChange"
                  />
                </a-form-item>

                <!-- 关键字 AND 搜索 -->
                <a-form-item label="包含以下所有关键词（与）">
                  <a-select
                    v-model:value="advancedSearchForm.keywordsAnd"
                    mode="tags"
                    style="width: 100%"
                    placeholder="输入关键词后按回车添加"
                    :get-popup-container="(triggerNode) => getPopupContainer()"
                    :disabled="hasOrKeywords"
                    @keydown.enter.prevent="(e) => handleKeywordEnter(e, 'and')"
                  >
                    <template
                      v-if="advancedSearchForm.keywordsAnd.length === 0"
                    >
                      <a-select-option value="使用AND搜索" disabled>
                        请输入关键词，按Enter添加
                      </a-select-option>
                    </template>
                  </a-select>
                </a-form-item>

                <!-- 关键字 OR 搜索 -->
                <a-form-item label="包含以下任一关键词（或）">
                  <a-select
                    v-model:value="advancedSearchForm.keywordsOr"
                    mode="tags"
                    style="width: 100%"
                    placeholder="输入关键词后按回车添加"
                    :get-popup-container="(triggerNode) => getPopupContainer()"
                    :disabled="hasAndKeywords"
                    @keydown.enter.prevent="(e) => handleKeywordEnter(e, 'or')"
                  >
                    <template v-if="advancedSearchForm.keywordsOr.length === 0">
                      <a-select-option value="使用OR搜索" disabled>
                        请输入关键词，按Enter添加
                      </a-select-option>
                    </template>
                  </a-select>
                </a-form-item>

                <!-- 操作按钮 -->
                <div class="form-actions">
                  <a-button @click="resetAdvancedSearch">重置</a-button>
                  <a-button type="primary" @click="performAdvancedSearch"
                    >搜索</a-button
                  >
                </div>
              </a-form>
            </div>
          </template>
          <template #trigger>
            <span></span>
            <!-- 空的trigger模板，使用按钮点击触发 -->
          </template>
        </a-popover>
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
              <a-menu-item v-if="isAdmin" key="manage" @click="goToAdmin">
                <template #icon><team-outlined /></template>
                用户管理
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

    <!-- 用户控制浮窗 - 修复挂载问题 -->
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
          <div class="profile-info">
            <h2>{{ userInfo.username || "未登录用户" }}</h2>
            <p>{{ userInfo.role ? "管理员" : "普通用户" }}</p>
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
              {{ userInfo.role ? "管理员" : "普通用户" }}
            </a-descriptions-item>
            <a-descriptions-item label="ID">
              {{ userInfo.id || "N/A" }}
            </a-descriptions-item>
          </a-descriptions>
        </div>

        <a-divider />

        <div class="profile-actions">
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
import dayjs from "dayjs";

// 修改导入方式，直接导入所需图标
import UserOutlined from "@ant-design/icons-vue/UserOutlined";
import SettingOutlined from "@ant-design/icons-vue/SettingOutlined";
import LogoutOutlined from "@ant-design/icons-vue/LogoutOutlined";
import DownOutlined from "@ant-design/icons-vue/DownOutlined";
import BarChartOutlined from "@ant-design/icons-vue/BarChartOutlined";
import PlusOutlined from "@ant-design/icons-vue/PlusOutlined";
import TeamOutlined from "@ant-design/icons-vue/TeamOutlined";

import FolderTree from "@/components/FolderTree.vue";
import { searchLibrary } from "@/api/load";
import { logout } from "@/api/auth";
import { useEventBus } from "@vueuse/core";

// const goToManage = () => {
//   // 假设管理中心的路由是 /manage
//   router.push("/manage");
// };

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
  TeamOutlined,
};

const isAdmin = computed(() => {
  return userInfo.role;
});

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
  query: string;
  useRegex: boolean;
  searchFields: string[];
  dateRange: [string, string] | null;
  documentType: string | null;
  keywordsAnd: string[];
  keywordsOr: string[];
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

// 高级搜索相关
const advancedSearchForm = ref<AdvancedSearchForm>({
  query: "",
  useRegex: false,
  searchFields: ["title", "author", "doi"],
  dateRange: null,
  documentType: null,
  keywordsAnd: [],
  keywordsOr: [],
  authorCount: null,
  uploadTime: null,
});

// 为Ant Design的日期选择器添加dayjs值
const dateRangeValue = ref<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([
  null,
  null,
]);

const goToAdmin = () => {
  router.push("/admin");
};

// 处理日期范围变化
const handleDateRangeChange = (
  dates: [dayjs.Dayjs | null, dayjs.Dayjs | null],
  dateStrings: [string, string]
) => {
  advancedSearchForm.value.dateRange =
    dateStrings[0] && dateStrings[1] ? (dateStrings as [string, string]) : null;
};

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
  // console.log(localStorage);
  const storedUserInfo = localStorage.getItem("userInfo");
  // console.log(storedUserInfo);
  if (storedUserInfo) {
    try {
      const parsedInfo = JSON.parse(storedUserInfo);
      userInfo.username = parsedInfo.username || "";
      userInfo.role = parsedInfo.role || "";
      userInfo.id = parsedInfo.id || "";
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

// 添加计算属性检查是否有"与"关键词
const hasAndKeywords = computed(() => {
  return advancedSearchForm.value.keywordsAnd.length > 0;
});

// 添加计算属性检查是否有"或"关键词
const hasOrKeywords = computed(() => {
  return advancedSearchForm.value.keywordsOr.length > 0;
});

// 处理关键词输入时的Enter键事件
const handleKeywordEnter = (e: KeyboardEvent, type: "and" | "or") => {
  // 阻止默认行为，避免清除已输入的关键词
  e.preventDefault();

  // 获取输入框元素
  const target = e.target as HTMLInputElement;
  const value = target.value?.trim();

  // 如果有有效输入且不是空白字符
  if (value && value.length > 0) {
    // 根据类型添加到对应的关键词数组
    if (type === "and") {
      if (!advancedSearchForm.value.keywordsAnd.includes(value)) {
        advancedSearchForm.value.keywordsAnd.push(value);
      }
    } else {
      if (!advancedSearchForm.value.keywordsOr.includes(value)) {
        advancedSearchForm.value.keywordsOr.push(value);
      }
    }

    // 清空输入值，准备下一次输入
    target.value = "";
  }
};

// 重置高级搜索表单 - 更新现有函数
const resetAdvancedSearch = () => {
  advancedSearchForm.value = {
    query: "",
    useRegex: false,
    searchFields: ["title", "author", "doi"],
    dateRange: null,
    documentType: null,
    keywordsAnd: [],
    keywordsOr: [],
    authorCount: null,
    uploadTime: null,
  };

  // 重置日期选择器
  dateRangeValue.value = [null, null];
};

// 切换高级搜索表单的显示状态
const toggleAdvancedSearch = () => {
  showAdvancedSearch.value = !showAdvancedSearch.value;
  if (showAdvancedSearch.value) {
    // 如果打开高级搜索，将当前搜索词转移到表单中
    advancedSearchForm.value.query = searchQuery.value;
    searchQuery.value = "";

    // 如果有日期范围，转换为dayjs对象
    if (advancedSearchForm.value.dateRange) {
      dateRangeValue.value = [
        dayjs(advancedSearchForm.value.dateRange[0]),
        dayjs(advancedSearchForm.value.dateRange[1]),
      ];
    }
  }
};

// 执行高级搜索 - 更新现有函数
const performAdvancedSearch = () => {
  // 构建高级搜索查询参数
  const advancedParams = {
    q: advancedSearchForm.value.query,
    regex: advancedSearchForm.value.useRegex ? "1" : "0",
    dateFrom: advancedSearchForm.value.dateRange?.[0] || "",
    dateTo: advancedSearchForm.value.dateRange?.[1] || "",
    keywordsAnd: advancedSearchForm.value.keywordsAnd?.join(",") || "",
    keywordsOr: advancedSearchForm.value.keywordsOr?.join(",") || "",
  };

  // 修改验证逻辑：允许空搜索内容，但必须至少有一个筛选条件
  if (
    !advancedParams.q.trim() &&
    !advancedParams.keywordsAnd &&
    !advancedParams.keywordsOr &&
    !advancedParams.dateFrom &&
    !advancedParams.dateTo
  ) {
    ElMessage.warning("请至少输入搜索内容、关键词或选择日期范围");
    return;
  }
  console.log("执行高级搜索，参数：", advancedParams);

  // 跳转到搜索结果页面，带上高级搜索参数
  router.push({
    path: "/search",
    query: advancedParams,
  });

  showAdvancedSearch.value = false;
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
  console.log("info:", userInfo);
};

// 修改密码
const handleChangePassword = () => {
  ElMessage.info("修改密码功能开发中...");
};

// 创建一个事件总线用于跨组件通信
const folderChangedBus = useEventBus("folder-changed");

// 添加DOM引用
const headerCenterRef = ref<HTMLElement | null>(null);

// 添加获取弹窗容器的方法
const getPopupContainer = () => {
  // 首先尝试使用ref引用
  if (headerCenterRef.value) {
    return headerCenterRef.value;
  }

  // 如果ref未设置，尝试使用querySelector
  const headerCenter = document.querySelector(".header-center");
  if (headerCenter) {
    return headerCenter as HTMLElement;
  }

  // 最后回退到body
  return document.body;
};

// 确保在组件挂载后才获取用户信息
onMounted(() => {
  getUserInfo();
  console.log("AppLayout组件已挂载，用户信息:", userInfo);
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
  height: 32px;
}

.advanced-search-button:hover {
  color: #409eff;
}

/* 高级搜索表单样式 - Ant Design版本 */
.advanced-search-form-ant {
  padding: 12px;
}

.advanced-search-form-ant .advanced-search-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 16px 0;
  text-align: center;
}

.advanced-search-form-ant .form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 8px;
}

/* 正则表达式开关样式 */
.regex-switch {
  width: 90px;
}

/* 确保popover位于正确位置 */
:deep(.ant-popover-inner) {
  background: white;
  box-shadow: 0 3px 6px -4px rgba(0, 0, 0, 0.12),
    0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 9px 28px 8px rgba(0, 0, 0, 0.05);
}

/* Ant表单元素样式调整 */
:deep(.ant-form-item) {
  margin-bottom: 16px;
}

:deep(.ant-input-group) {
  display: flex;
  align-items: center;
}

:deep(.ant-switch) {
  margin-left: 8px;
}

/* 添加禁用状态的说明样式 */
:deep(.ant-select-disabled) .ant-select-selection-placeholder {
  color: #ff7875;
}

:deep(.ant-select-disabled) {
  background-color: rgba(250, 250, 250, 0.8);
  cursor: not-allowed;
}
</style>
