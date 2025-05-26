<template>
  <div class="institution-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- 机构信息 -->
    <div v-else-if="institutionData" class="institution-content">
      <div class="institution-header">
        <h1 class="institution-name">{{ institutionData.name }}</h1>
        <div v-if="institutionData.location" class="institution-location">
          <environment-outlined /> {{ institutionData.location }}
        </div>
      </div>

      <!-- 作者列表 -->
      <div class="section-container">
        <h2 class="section-title">
          相关作者
          <span class="count-badge">{{ institutionData.authorCount }}</span>
        </h2>

        <div v-if="institutionData.authors.length === 0" class="empty-state">
          <a-empty description="未关联任何作者" />
        </div>
        <div v-else class="authors-grid">
          <a-row :gutter="[16, 16]">
            <a-col
              :xs="24"
              :sm="12"
              :md="8"
              v-for="author in institutionData.authors"
              :key="author.author_id"
            >
              <router-link :to="`/author/${author.author_id}`">
                <a-card hoverable class="author-card">
                  <template #title>{{ author.author_name }}</template>
                  <template #extra>
                    <right-outlined />
                  </template>
                  <a-card-meta v-if="author.author_email">
                    <template #description>
                      <div class="author-email">
                        <mail-outlined /> {{ author.author_email }}
                      </div>
                    </template>
                  </a-card-meta>
                </a-card>
              </router-link>
            </a-col>
          </a-row>
        </div>
      </div>
    </div>

    <!-- 错误状态 -->
    <a-result
      v-else
      status="error"
      title="获取机构详情失败"
      sub-title="请检查网络连接或稍后再试"
    >
      <template #extra>
        <a-button type="primary" @click="fetchInstitutionData">重试</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  MailOutlined,
  EnvironmentOutlined,
  RightOutlined,
} from "@ant-design/icons-vue";
import { getInstitutionDetails } from "@/api/load";

const route = useRoute();
const loading = ref(true);
const institutionData = ref<any>(null);
const error = ref<string | null>(null);

// 获取机构数据
const fetchInstitutionData = async (): Promise<void> => {
  const institutionId = route.params.id;
  if (!institutionId) {
    error.value = "机构ID未指定";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    const response = await getInstitutionDetails(institutionId);

    if (response.data.code === 0) {
      institutionData.value = response.data.data;
      document.title = `${institutionData.value.name} - 机构详情 - LitSay`;
    } else {
      error.value = response.data.message || "获取机构数据失败";
    }
  } catch (err) {
    console.error("获取机构详情出错:", err);
    error.value = "网络错误，请稍后重试";
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchInstitutionData();
});
</script>

<style scoped>
.institution-detail-container {
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

.institution-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.institution-name {
  font-family: "Playfair Display", serif;
  font-size: 2.2rem;
  margin: 0 0 12px 0;
  color: #303133;
}

.institution-location {
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

.authors-grid {
  margin-top: 16px;
}

.author-card {
  transition: all 0.3s;
}

.author-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
}

.author-email {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
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
