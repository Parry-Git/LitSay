<template>
  <div class="document-detail">
    <div class="document-header">
      <div class="back-button">
        <el-button @click="goBack" icon="ArrowLeft" size="small"
          >返回</el-button
        >
      </div>
      <h1 class="document-title">{{ document.title }}</h1>
      <div class="document-actions">
        <el-button type="primary" size="small" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑元数据
        </el-button>
        <el-button type="success" size="small" @click="handleDownload">
          <el-icon><Download /></el-icon>
          下载
        </el-button>
      </div>
    </div>

    <el-divider />

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="document-content">
      <el-descriptions title="文献信息" :column="2" border>
        <el-descriptions-item label="标题">{{
          document.title
        }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{
          document.authors?.join(", ") || "未知"
        }}</el-descriptions-item>
        <el-descriptions-item label="出版日期">{{
          document.publishDate || "未知"
        }}</el-descriptions-item>
        <el-descriptions-item label="文件类型">{{
          document.fileType || "PDF"
        }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{
          document.fileSize || "未知"
        }}</el-descriptions-item>
        <el-descriptions-item label="上传时间">{{
          document.uploadTime || "未知"
        }}</el-descriptions-item>
        <el-descriptions-item label="标签" :span="2">
          <el-tag
            v-for="(tag, index) in document.tags"
            :key="index"
            class="tag-item"
            size="small"
          >
            {{ tag }}
          </el-tag>
          <span v-if="!document.tags || document.tags.length === 0"
            >无标签</span
          >
        </el-descriptions-item>
        <el-descriptions-item label="摘要" :span="2">
          {{ document.abstract || "无摘要" }}
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="document.fileUrl" class="pdf-preview">
        <h2>文件预览</h2>
        <div class="pdf-container">
          <!-- 这里可以集成PDF预览组件 -->
          <el-empty v-if="!document.fileUrl" description="暂无预览" />
          <iframe
            v-else
            :src="document.fileUrl"
            width="100%"
            height="600px"
            frameborder="0"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Edit, Download } from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const documentId = ref(route.params.id);
const document = ref<any>({});

// 模拟获取文档详情
const fetchDocumentDetails = async () => {
  loading.value = true;
  try {
    // 在实际应用中，这里应该调用API获取文档详情
    // const response = await getDocumentDetails(documentId.value);
    // document.value = response.data.data;

    // 模拟数据
    setTimeout(() => {
      document.value = {
        id: documentId.value,
        title: "深度学习在自然语言处理中的应用研究",
        authors: ["张三", "李四", "王五"],
        abstract:
          "本文探讨了深度学习技术在自然语言处理领域的最新应用和进展。研究表明，基于神经网络的深度学习模型在多项NLP任务中取得了显著的效果提升。本文分析了各种模型架构的优缺点，并探讨了未来可能的研究方向。",
        publishDate: "2023-06-15",
        fileType: "PDF",
        fileSize: "2.3 MB",
        uploadTime: "2023-10-20 14:30:22",
        tags: ["深度学习", "NLP", "神经网络", "人工智能"],
        fileUrl: "https://example.com/sample.pdf",
      };
      loading.value = false;
    }, 1000);
  } catch (error) {
    console.error("获取文档详情失败", error);
    ElMessage.error("获取文档详情失败");
    loading.value = false;
  }
};

const goBack = () => {
  router.back();
};

const handleEdit = () => {
  router.push(`/document/${documentId.value}/edit`);
};

const handleDownload = () => {
  // 在实际应用中，这里应该调用API下载文档
  ElMessage.success("开始下载文档...");
};

onMounted(() => {
  fetchDocumentDetails();
});
</script>

<style scoped>
.document-detail {
  padding: 20px;
}

.document-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.back-button {
  margin-right: auto;
}

.document-title {
  font-size: 22px;
  font-weight: 500;
  color: #303133;
  margin: 0;
  flex-basis: 100%;
  order: -1;
  margin-bottom: 10px;
}

.document-actions {
  display: flex;
  gap: 10px;
}

.loading-container {
  padding: 20px 0;
}

.document-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.tag-item {
  margin-right: 8px;
  margin-bottom: 5px;
}

.pdf-preview {
  margin-top: 20px;
}

.pdf-container {
  margin-top: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}
</style>
