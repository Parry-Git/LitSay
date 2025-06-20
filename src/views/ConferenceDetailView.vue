<template>
  <div class="conference-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- 会议信息 -->
    <div
      v-else-if="containerData && containerData.type === 'conference'"
      class="conference-content"
    >
      <div class="conference-header">
        <h1 class="conference-name">{{ containerData.name }}</h1>
      </div>

      <!-- 文献列表 -->
      <div class="section-container">
        <h2 class="section-title">
          会议论文
          <span class="count-badge">{{ containerData.documentCount }}</span>
        </h2>

        <div v-if="containerData.documents.length === 0" class="empty-state">
          <a-empty description="未收录任何会议论文" />
        </div>
        <div v-else class="documents-table-container">
          <a-table
            :columns="documentColumns"
            :data-source="containerData.documents"
            :pagination="{ pageSize: 10 }"
          >
            <!-- 标题列 -->
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'title'">
                <router-link
                  :to="`/document/${record.document_id}`"
                  class="document-title"
                >
                  {{ record.title }}
                </router-link>
              </template>

              <!-- 发布日期 -->
              <template v-else-if="column.key === 'date'">
                {{ formatDate(record.publication_date) || "--" }}
              </template>

              <!-- 会议日期 -->
              <template v-else-if="column.key === 'conference_time'">
                {{ formatDate(record.conference_time) || "--" }}
              </template>

              <!-- 会议地点 -->
              <template v-else-if="column.key === 'conference_locaton'">
                {{ record.conference_location || "--" }}
              </template>
            </template>
          </a-table>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <a-result
      v-else
      status="error"
      title="获取会议详情失败"
      sub-title="请检查网络连接或稍后再试"
    >
      <template #extra>
        <a-button type="primary" @click="fetchContainerData">重试</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { CalendarOutlined, EnvironmentOutlined } from "@ant-design/icons-vue";
import { getContainerDetails } from "@/api/load";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const containerData = ref<any>(null);
const error = ref<string | null>(null);

// 表格列定义
const documentColumns = [
  {
    title: "标题",
    dataIndex: "title",
    key: "title",
    ellipsis: true,
    width: "50%",
  },
  {
    title: "发布日期",
    dataIndex: "publication_date",
    key: "date",
    sorter: (a: any, b: any) =>
      new Date(a.publication_date || 0).getTime() -
      new Date(b.publication_date || 0).getTime(),
    width: "25%",
  },
  {
    title: "会议时间",
    dataIndex: "conference_time",
    key: "conference_time",
    ellipsis: true,
    width: "25%",
  },
  {
    title: "会议地点",
    dataIndex: "conference_location",
    key: "conference_location",
    ellipsis: true,
    width: "25%",
  },
];

// 格式化日期
const formatDate = (dateString: string | null): string => {
  if (!dateString) return "未知日期";

  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch (e) {
    return dateString;
  }
};

// 获取容器数据
const fetchContainerData = async (): Promise<void> => {
  const containerId = route.params.id;
  if (!containerId) {
    error.value = "ID未指定";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    const response = await getContainerDetails(containerId);

    if (response.data.code === 0) {
      containerData.value = response.data.data;

      // 检查类型是否为会议
      if (containerData.value.type !== "conference") {
        // 如果是期刊，跳转到期刊页面
        if (containerData.value.type === "journal") {
          router.replace(`/journal/${containerId}`);
          return;
        }

        // 其他类型显示错误
        error.value = "不是有效的会议";
      }

      document.title = `${containerData.value.name} - 会议详情 - LitSay`;
    } else {
      error.value = response.data.message || "获取数据失败";
    }
  } catch (err) {
    console.error("获取会议详情出错:", err);
    error.value = "网络错误，请稍后重试";
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchContainerData();
});
</script>

<style scoped>
.conference-detail-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.conference-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.conference-name {
  font-family: "Playfair Display", serif;
  font-size: 2.2rem;
  margin: 0 0 12px 0;
  color: #303133;
}

.conference-info {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.conference-time,
.conference-location {
  font-size: 16px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-container {
  margin-bottom: 40px;
}

.section-title {
  font-family: "Playfair Display", serif;
  font-size: 1.6rem;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

.count-badge {
  font-size: 0.9rem;
  background-color: #f0f2f5;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 10px;
  color: #606266;
}

.documents-table-container {
  margin-top: 16px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.document-title {
  color: #1890ff;
  font-weight: 500;
}

.folder-name {
  color: #52c41a;
}

.empty-state {
  padding: 40px 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* 引入Playfair Display字体 */
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&display=swap");
</style>
