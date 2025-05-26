<template>
  <div class="author-detail-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- 作者信息 -->
    <div v-else-if="authorData" class="author-content">
      <div class="author-header">
        <h1 class="author-name">{{ authorData.name }}</h1>
        <div v-if="authorData.email" class="author-email">
          <mail-outlined /> {{ authorData.email }}
        </div>
      </div>

      <!-- 机构列表 -->
      <div class="section-container">
        <h2 class="section-title">所属机构</h2>
        <div v-if="authorData.institutions.length === 0" class="empty-state">
          <a-empty description="未关联任何机构" />
        </div>
        <div v-else class="institutions-list">
          <a-list :data-source="authorData.institutions">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #title>
                    <router-link
                      :to="`/institution/${item.institution_id}`"
                      class="institution-name"
                    >
                      {{ item.institution_name }}
                    </router-link>
                  </template>
                  <template #description>
                    <span v-if="item.institution_location">
                      <environment-outlined /> {{ item.institution_location }}
                    </span>
                    <span v-else>暂无位置信息</span>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </div>

      <!-- 文章列表 -->
      <div class="section-container">
        <h2 class="section-title">
          参与文献
          <span class="count-badge">{{ authorData.documentCount }}</span>
        </h2>

        <div v-if="authorData.documents.length === 0" class="empty-state">
          <a-empty description="未关联任何文献" />
        </div>
        <div v-else class="documents-table-container">
          <a-table
            :columns="documentColumns"
            :data-source="authorData.documents"
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

              <!-- 文件夹列 -->
              <template v-else-if="column.key === 'folder'">
                <router-link
                  :to="`/folder/${record.directory_id}`"
                  class="folder-name"
                >
                  {{ record.directory_name }}
                </router-link>
              </template>

              <!-- 角色列 -->
              <template v-else-if="column.key === 'sequence'">
                <a-tag
                  :color="getSequenceColor(record.sequence)"
                  class="sequence-tag"
                >
                  {{ formatSequence(record.sequence) }}
                </a-tag>
              </template>

              <!-- 日期列 -->
              <template v-else-if="column.key === 'date'">
                {{ formatDate(record.publication_date) }}
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
      title="获取作者详情失败"
      sub-title="请检查网络连接或稍后再试"
    >
      <template #extra>
        <a-button type="primary" @click="fetchAuthorData">重试</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { MailOutlined, EnvironmentOutlined } from "@ant-design/icons-vue";
import { getAuthorDetails } from "@/api/load";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const authorData = ref<any>(null);
const error = ref<string | null>(null);

// 表格列定义
const documentColumns = [
  {
    title: "标题",
    dataIndex: "title",
    key: "title",
    ellipsis: true,
    width: "40%",
  },
  {
    title: "角色",
    dataIndex: "sequence",
    key: "sequence",
    width: "15%",
  },
  {
    title: "发布日期",
    dataIndex: "publication_date",
    key: "date",
    sorter: (a: any, b: any) =>
      new Date(a.publication_date || 0).getTime() -
      new Date(b.publication_date || 0).getTime(),
    width: "20%",
  },
  {
    title: "所在文件夹",
    dataIndex: "directory_name",
    key: "folder",
    ellipsis: true,
    width: "25%",
  },
];

// 格式化序列/角色
const formatSequence = (sequence: string): string => {
  const sequenceMap: Record<string, string> = {
    first: "第一作者",
    corresponding: "通讯作者",
    additional: "合作作者",
    other: "其他",
  };
  return sequenceMap[sequence] || "其他";
};

// 获取序列/角色的颜色
const getSequenceColor = (sequence: string): string => {
  const colorMap: Record<string, string> = {
    first: "blue",
    corresponding: "purple",
    additional: "green",
    other: "default",
  };
  return colorMap[sequence] || "default";
};

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

// 获取作者数据
const fetchAuthorData = async (): Promise<void> => {
  const authorId = route.params.id;
  if (!authorId) {
    error.value = "作者ID未指定";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    const response = await getAuthorDetails(authorId);

    if (response.data.code === 0) {
      authorData.value = response.data.data;
      document.title = `${authorData.value.name} - 作者详情 - LitSay`;
    } else {
      error.value = response.data.message || "获取作者数据失败";
    }
  } catch (err) {
    console.error("获取作者详情出错:", err);
    error.value = "网络错误，请稍后重试";
  } finally {
    loading.value = false;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchAuthorData();
});
</script>

<style scoped>
.author-detail-container {
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

.author-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.author-name {
  font-family: "Playfair Display", serif;
  font-size: 2.2rem;
  margin: 0 0 12px 0;
  color: #303133;
}

.author-email {
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

.institutions-list {
  margin-top: 16px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.institution-name {
  font-size: 16px;
  font-weight: 500;
  color: #1890ff;
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

.sequence-tag {
  font-size: 0.85rem;
}

/* 引入Playfair Display字体 */
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&display=swap");
</style>
