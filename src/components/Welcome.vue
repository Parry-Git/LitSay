<template>
  <div class="welcome-container">
    <el-card class="welcome-card">
      <div class="welcome-header">
        <el-icon :size="32" class="welcome-icon"><Document /></el-icon>
        <h1 class="welcome-title">欢迎使用文献管理系统</h1>
      </div>

      <div class="welcome-content">
        <p class="welcome-description">
          这是一个帮助您高效管理学术文献的平台，提供以下功能：
        </p>

        <div class="features-list">
          <div class="feature-item">
            <el-icon><FolderOpened /></el-icon>
            <span>文件分类管理</span>
          </div>
          <div class="feature-item">
            <el-icon><Upload /></el-icon>
            <span>便捷上传下载</span>
          </div>
          <div class="feature-item">
            <el-icon><Search /></el-icon>
            <span>全文检索</span>
          </div>
          <div class="feature-item">
            <el-icon><Share /></el-icon>
            <span>文献共享协作</span>
          </div>
        </div>
      </div>

      <div class="stats-container">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="stats-header">
              <el-icon><Files /></el-icon>
              <span>我的文件</span>
            </div>
          </template>
          <div class="stats-content">
            <div class="stats-number">{{ userStats.totalDocuments }}</div>
            <div class="stats-label">文件总数</div>
          </div>
        </el-card>
      </div>

      <div class="welcome-footer">
        <el-button type="primary" @click="goToUpload">
          <el-icon><Plus /></el-icon>
          上传新文献
        </el-button>
        <el-button @click="goToFiles">
          <el-icon><Document /></el-icon>
          查看我的文件
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  Document,
  FolderOpened,
  Upload,
  Search,
  Share,
  Plus,
  Files,
} from "@element-plus/icons-vue";
import { getUserStats } from "@/api/load";

const router = useRouter();

// 添加用户统计数据
const userStats = ref<any>({
  totalDocuments: 0,
  recentlyViewed: 0,
  totalFolders: 0,
});

// 获取用户统计数据
const fetchUserStats = async () => {
  try {
    const response = await getUserStats();
    userStats.value = response.data.data;
  } catch (error) {
    console.error("获取用户统计数据失败", error);
  }
};

const goToUpload = () => {
  router.push("/upload");
};

const goToFiles = () => {
  router.push("/folder/2"); // 导航到我的文献库
};

// 组件挂载时获取统计数据
onMounted(() => {
  fetchUserStats();
});
</script>

<style scoped>
.welcome-container {
  padding: 30px;
  max-width: 1500px;
  margin: 0 auto;
}

.welcome-card {
  border-radius: 8px;
}

.welcome-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.welcome-icon {
  color: #409eff;
  margin-right: 12px;
}

.welcome-title {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.welcome-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 20px;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 30px;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.feature-item .el-icon {
  font-size: 20px;
  color: #409eff;
  margin-right: 10px;
}

.stats-container {
  margin-bottom: 30px;
}

.stats-card {
  width: 200px;
}

.stats-header {
  display: flex;
  align-items: center;
}

.stats-header .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.stats-content {
  text-align: center;
  padding: 10px 0;
}

.stats-number {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.welcome-footer {
  display: flex;
  gap: 12px;
}
</style>
