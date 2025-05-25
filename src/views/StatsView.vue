<template>
  <div class="stats-view">
    <h1 class="stats-title">文献统计分析</h1>

    <div class="stats-cards">
      <!-- 文献总数 -->
      <a-card class="stats-card">
        <template #title>
          <div class="card-title"><file-text-outlined /> 文献总数</div>
        </template>
        <div class="card-content">
          <div class="stats-number">{{ statsData.totalDocuments || 0 }}</div>
          <div class="stats-desc">收藏的文献总数</div>
        </div>
      </a-card>

      <!-- 文件夹总数 -->
      <a-card class="stats-card">
        <template #title>
          <div class="card-title"><folder-outlined /> 文件夹总数</div>
        </template>
        <div class="card-content">
          <div class="stats-number">{{ statsData.totalFolders || 0 }}</div>
          <div class="stats-desc">创建的文件夹数</div>
        </div>
      </a-card>

      <!-- 最近浏览 -->
      <a-card class="stats-card">
        <template #title>
          <div class="card-title"><eye-outlined /> 最近浏览</div>
        </template>
        <div class="card-content">
          <div class="stats-number">{{ statsData.recentlyViewed || 0 }}</div>
          <div class="stats-desc">最近30天浏览的文献</div>
        </div>
      </a-card>

      <!-- 存储空间 -->
      <a-card class="stats-card">
        <template #title>
          <div class="card-title"><database-outlined /> 存储空间</div>
        </template>
        <div class="card-content">
          <div class="stats-number">{{ statsData.storageUsed || "0 MB" }}</div>
          <div class="stats-desc">
            已使用 / {{ statsData.storageTotal || "5 GB" }}
          </div>
          <a-progress
            :percent="statsData.storagePercentage || 0"
            :stroke-color="{ from: '#108ee9', to: '#87d068' }"
            size="small"
          />
        </div>
      </a-card>
    </div>

    <div class="stats-charts">
      <div class="chart-row">
        <!-- 文献类型分布图 -->
        <a-card class="chart-card" title="文献类型分布">
          <div class="chart-placeholder">
            <bar-chart-outlined />
            <span>加载中...</span>
          </div>
        </a-card>

        <!-- 文献年份分布图 -->
        <a-card class="chart-card" title="文献年份分布">
          <div class="chart-placeholder">
            <line-chart-outlined />
            <span>加载中...</span>
          </div>
        </a-card>
      </div>

      <!-- 最近活动 -->
      <a-card title="最近活动" class="activity-card">
        <a-list
          :data-source="statsData.recentActivities || []"
          :loading="loading"
        >
          <a-list-item
            v-for="(item, index) in statsData.recentActivities"
            :key="index"
          >
            <a-list-item-meta>
              <template #avatar>
                <a-avatar
                  :icon="getActivityIcon(item.type)"
                  :style="{ backgroundColor: getActivityColor(item.type) }"
                />
              </template>
              <template #title>
                {{ getActivityTitle(item) }}
              </template>
              <template #description>
                <span>{{ item.time }}</span>
                <span v-if="item.folder"> · 位置: {{ item.folder }}</span>
              </template>
            </a-list-item-meta>
          </a-list-item>
          <template v-if="!statsData.recentActivities?.length">
            <div class="empty-activities">
              <inbox-outlined />
              <span>暂无活动记录</span>
            </div>
          </template>
        </a-list>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getUserStats } from "@/api/load";
import {
  FileTextOutlined,
  FolderOutlined,
  EyeOutlined,
  DatabaseOutlined,
  BarChartOutlined,
  LineChartOutlined,
  InboxOutlined,
  UploadOutlined,
  EyeInvisibleOutlined,
  DownloadOutlined,
  FolderAddOutlined,
} from "@ant-design/icons-vue";

const loading = ref(true);
const statsData = ref<any>({});

// 获取用户统计数据
const fetchStats = async () => {
  try {
    loading.value = true;
    const response = await getUserStats();
    statsData.value = response.data.data || {};
  } catch (error) {
    console.error("获取统计数据失败", error);
  } finally {
    loading.value = false;
  }
};

// 获取活动图标
const getActivityIcon = (type: string) => {
  switch (type) {
    case "upload":
      return UploadOutlined;
    case "view":
      return EyeOutlined;
    case "download":
      return DownloadOutlined;
    case "create_folder":
      return FolderAddOutlined;
    default:
      return InboxOutlined;
  }
};

// 获取活动颜色
const getActivityColor = (type: string) => {
  switch (type) {
    case "upload":
      return "#1890ff";
    case "view":
      return "#52c41a";
    case "download":
      return "#722ed1";
    case "create_folder":
      return "#faad14";
    default:
      return "#bfbfbf";
  }
};

// 获取活动标题
const getActivityTitle = (item: any) => {
  switch (item.type) {
    case "upload":
      return `上传了文献 "${item.documentName}"`;
    case "view":
      return `查看了文献 "${item.documentName}"`;
    case "download":
      return `下载了文献 "${item.documentName}"`;
    case "create_folder":
      return `创建了文件夹 "${item.folderName}"`;
    default:
      return "未知活动";
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.stats-view {
  padding: 20px;
}

.stats-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #262626;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stats-card {
  height: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  font-weight: 500;
  gap: 8px;
}

.card-content {
  padding: 8px 0;
}

.stats-number {
  font-size: 32px;
  font-weight: 600;
  color: #1890ff;
}

.stats-desc {
  margin-top: 8px;
  color: #8c8c8c;
  font-size: 13px;
}

.stats-charts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 16px;
}

.chart-card {
  height: 300px;
}

.chart-placeholder {
  height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #d9d9d9;
  font-size: 16px;
  gap: 16px;
}

.chart-placeholder :deep(svg) {
  font-size: 48px;
}

.activity-card {
  margin-top: 8px;
}

.empty-activities {
  padding: 24px 0;
  text-align: center;
  color: #bfbfbf;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-activities :deep(svg) {
  font-size: 32px;
}
</style>
