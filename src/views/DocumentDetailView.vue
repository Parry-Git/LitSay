<template>
  <div class="document-detail-container">
    <!-- 笔记编辑对话框 - 移到条件渲染链外部 -->
    <a-modal
      v-model:visible="showNoteEditor"
      title="编辑笔记"
      width="800px"
      @ok="saveNote"
      :okButtonProps="{ loading: savingNote }"
    >
      <a-tabs v-model:activeKey="noteTabActiveKey">
        <a-tab-pane key="edit" tab="编辑">
          <a-textarea
            v-model:value="editingNoteContent"
            :rows="15"
            placeholder="支持Markdown格式..."
          />
          <div class="markdown-tips">
            <p>支持Markdown格式，例如：</p>
            <ul>
              <li># 一级标题</li>
              <li>**粗体**</li>
              <li>*斜体*</li>
              <li>- 列表项</li>
              <li>[链接](http://example.com)</li>
            </ul>
          </div>
        </a-tab-pane>
        <a-tab-pane key="preview" tab="预览">
          <div class="note-preview" v-html="renderedEditingNote"></div>
        </a-tab-pane>
      </a-tabs>
    </a-modal>

    <!-- 条件渲染链保持完整 -->
    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" />
    </div>

    <!-- 文档详情内容 -->
    <div v-else-if="documentData" class="document-content">
      <!-- 文档标题和操作栏 -->
      <div class="document-header">
        <h1 class="document-title">{{ documentData.title }}</h1>
        <div class="document-actions">
          <a-button type="primary" @click="handleEdit">编辑</a-button>
          <a-button type="danger" @click="confirmDelete">删除</a-button>
        </div>
      </div>

      <!-- 基本信息卡片 -->
      <a-card class="info-card">
        <a-row :gutter="[16, 24]">
          <!-- 评星功能 - 移动到作者信息之前 -->
          <a-col :span="24">
            <div class="info-section">
              <h3 class="section-title">
                <star-outlined class="section-icon" /> 评分
              </h3>
              <div class="stars-container">
                <a-rate v-model:value="stars" @change="handleStarsChange" />
                <a-button
                  type="link"
                  size="small"
                  @click="saveStars"
                  :loading="savingStars"
                  v-if="starsChanged"
                >
                  保存评分
                </a-button>
              </div>
            </div>
          </a-col>

          <!-- 作者信息部分 - 改为列表，每位作者可点击 -->
          <a-col :span="24">
            <div class="info-section">
              <h3 class="section-title">
                <team-outlined class="section-icon" /> 作者
              </h3>
              <div class="authors-list">
                <a-tag
                  v-for="(author, index) in documentData.authors"
                  :key="index"
                  class="author-tag clickable"
                  :color="getAuthorColor(documentData.sequence?.[index])"
                  @click="navigateToAuthor(index)"
                >
                  {{ author }}
                  <small
                    v-if="documentData.sequence?.[index]"
                    class="author-role"
                  >
                    ({{ formatAuthorRole(documentData.sequence[index]) }})
                  </small>
                </a-tag>
              </div>
            </div>
          </a-col>

          <!-- 期刊/会议信息 - 添加点击跳转 -->
          <a-col :span="12" v-if="documentData.journal">
            <div class="info-section">
              <h3 class="section-title">
                <book-outlined class="section-icon" /> 期刊
              </h3>
              <a class="journal-name clickable" @click="navigateToJournal()">
                {{ documentData.journal }}
              </a>
            </div>
          </a-col>

          <a-col :span="12" v-if="documentData.conference">
            <div class="info-section">
              <h3 class="section-title">
                <global-outlined class="section-icon" /> 会议
              </h3>
              <a
                class="conference-name clickable"
                @click="navigateToConference()"
              >
                {{ documentData.conference }}
              </a>
            </div>
          </a-col>

          <!-- DOI信息 -->
          <a-col :span="12" v-if="documentData.doi">
            <div class="info-section">
              <h3 class="section-title">
                <number-outlined class="section-icon" /> DOI
              </h3>
              <a
                :href="`https://doi.org/${documentData.doi}`"
                target="_blank"
                class="doi-link"
              >
                {{ documentData.doi }}
              </a>
            </div>
          </a-col>

          <!-- 发布日期 -->
          <a-col :span="12" v-if="documentData.publishDate">
            <div class="info-section">
              <h3 class="section-title">
                <calendar-outlined class="section-icon" /> 发布日期
              </h3>
              <p>{{ formatDate(documentData.publishDate) }}</p>
            </div>
          </a-col>

          <!-- 文件夹位置 -->
          <a-col :span="12" v-if="documentData.folderName">
            <div class="info-section">
              <h3 class="section-title">
                <folder-outlined class="section-icon" /> 文件夹
              </h3>
              <router-link
                :to="`/folder/${documentData.folderId}`"
                class="folder-link"
              >
                {{ documentData.folderName }}
              </router-link>
            </div>
          </a-col>

          <!-- 关键词列表 -->
          <a-col
            :span="24"
            v-if="documentData.keywords && documentData.keywords.length"
          >
            <div class="info-section">
              <h3 class="section-title">
                <tags-outlined class="section-icon" /> 关键词
              </h3>
              <div class="keywords-list">
                <a-tag
                  v-for="(keyword, index) in documentData.keywords"
                  :key="index"
                >
                  {{ keyword }}
                </a-tag>
              </div>
            </div>
          </a-col>

          <!-- 上传时间 -->
          <a-col :span="24" v-if="documentData.uploadTime">
            <div class="meta-info">
              上传于: {{ formatDate(documentData.uploadTime, true) }}
            </div>
          </a-col>
        </a-row>
      </a-card>

      <!-- 笔记部分 -->
      <div class="notes-section">
        <h2 class="section-header">
          笔记
          <a-button
            type="primary"
            size="small"
            @click="showNoteEditor = true"
            style="margin-left: 12px"
          >
            编辑笔记
          </a-button>
        </h2>
        <a-card class="note-card">
          <div
            v-if="documentData.note"
            class="note-content"
            v-html="renderedNote"
          ></div>
          <a-empty v-else description="暂无笔记" />
        </a-card>
      </div>

      <!-- 文件预览部分 - 如果有的话 -->
      <div class="preview-section" v-if="documentData.local_url">
        <h2 class="section-header">文档预览</h2>
        <div class="preview-container">
          <iframe
            v-if="isPdfUrl(documentData.local_url)"
            :src="`${baseUrl}/uploads/${documentData.local_url}`"
            class="pdf-preview"
          ></iframe>
          <div v-else class="preview-placeholder">
            <file-pdf-outlined class="pdf-icon" />
            <p>此文档类型无法预览</p>
            <a-button
              type="primary"
              :href="`${baseUrl}/uploads/${documentData.local_url}`"
              target="_blank"
            >
              打开文档
            </a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载失败状态 -->
    <a-result
      v-else
      status="error"
      title="加载失败"
      sub-title="无法获取文档详情信息"
    >
      <template #extra>
        <a-button type="primary" @click="fetchDocumentData">重试</a-button>
        <a-button @click="goBack">返回</a-button>
      </template>
    </a-result>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { message, Modal } from "ant-design-vue";
import MarkdownIt from "markdown-it";
import {
  FileOutlined,
  DeleteOutlined,
  EditOutlined,
  BookOutlined,
  TeamOutlined,
  GlobalOutlined,
  NumberOutlined,
  CalendarOutlined,
  TagsOutlined,
  FolderOutlined,
  FilePdfOutlined,
  StarOutlined,
} from "@ant-design/icons-vue";

import {
  getDocumentDetails,
  deleteDocument,
  updateDocumentMetadata,
} from "@/api/load";
import { API_BASE_URL } from "@/api/config";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const documentData = ref<any>(null);
const baseUrl = API_BASE_URL || "";

// 评星相关状态
const stars = ref(0);
const initialStars = ref(0);
const starsChanged = computed(() => stars.value !== initialStars.value);
const savingStars = ref(false);

// 笔记相关状态
const showNoteEditor = ref(false);
const editingNoteContent = ref("");
const noteTabActiveKey = ref("edit");
const savingNote = ref(false);

// Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
});

// 渲染 Markdown 笔记
const renderedNote = computed(() => {
  if (!documentData.value?.note) return "";
  return md.render(documentData.value.note);
});

// 渲染编辑中的笔记预览
const renderedEditingNote = computed(() => {
  if (!editingNoteContent.value) return "";
  return md.render(editingNoteContent.value);
});

// 获取文档数据
const fetchDocumentData = async () => {
  const documentId = route.params.id;
  if (!documentId) {
    message.error("文档ID无效");
    return;
  }

  loading.value = true;
  try {
    const response = await getDocumentDetails(documentId);
    if (response.data && response.data.code === 0) {
      documentData.value = response.data.data;
      document.title = `${documentData.value.title} - LitSay`;

      // 初始化评星
      stars.value = documentData.value.stars || 0;
      initialStars.value = stars.value;

      // 初始化笔记内容
      editingNoteContent.value = documentData.value.note || "";
    } else {
      message.error(response.data?.message || "获取文档详情失败");
    }
  } catch (error) {
    console.error("获取文档详情出错", error);
    message.error("获取文档详情失败，请稍后重试");
  } finally {
    loading.value = false;
  }
};

// 编辑文档
const handleEdit = () => {
  router.push(`/document/${route.params.id}/edit`);
};

// 确认删除
const confirmDelete = () => {
  Modal.confirm({
    title: "确认删除",
    content: "删除后数据无法恢复，确认继续吗？",
    okText: "删除",
    okType: "danger",
    cancelText: "取消",
    onOk: async () => {
      try {
        const response = await deleteDocument(route.params.id);
        if (response.data && response.data.code === 0) {
          message.success("文档已删除");
          router.replace(`/folder/${documentData.value.folderId}`);
        } else {
          message.error(response.data?.message || "删除文档失败");
        }
      } catch (error) {
        console.error("删除文档出错", error);
        message.error("删除文档失败，请稍后重试");
      }
    },
  });
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 处理评星变更
const handleStarsChange = (value) => {
  console.log("评星变更为:", value);
  stars.value = value;
};

// 保存评星
const saveStars = async () => {
  console.log("保存评星:", stars.value);
  savingStars.value = true;
  try {
    await updateDocumentMetadata(route.params.id, { stars: stars.value });
    message.success("评分已保存");
    initialStars.value = stars.value; // 更新初始值，使starsChanged计算属性返回false
  } catch (error) {
    console.error("保存评分失败", error);
    message.error("保存评分失败，请稍后重试");
  } finally {
    savingStars.value = false;
  }
};

// 保存笔记
const saveNote = async () => {
  console.log("保存笔记");
  savingNote.value = true;
  try {
    await updateDocumentMetadata(route.params.id, {
      note: editingNoteContent.value,
    });
    documentData.value.note = editingNoteContent.value;
    message.success("笔记已保存");
    showNoteEditor.value = false;
  } catch (error) {
    console.error("保存笔记失败", error);
    message.error("保存笔记失败，请稍后重试");
  } finally {
    savingNote.value = false;
  }
};

// 添加新的导航函数，并包含调试输出
const navigateToAuthor = (index: number) => {
  console.log(
    "点击作者:",
    documentData.value?.authors?.[index],
    "索引:",
    index
  );

  // 直接从author_ids数组获取作者ID
  const authorId = documentData.value?.author_ids?.[index];

  if (authorId) {
    console.log("导航到作者详情页:", authorId);
    router.push(`/author/${authorId}`);
  } else {
    console.log("未找到作者ID");
    message.info("作者详情暂无法访问");
  }
};

const navigateToJournal = () => {
  console.log("点击期刊:", documentData.value?.journal);

  // 使用container_id而不是在document对象上查找
  const containerId = documentData.value?.container_id;
  if (containerId && documentData.value?.journal) {
    console.log("导航到期刊详情页:", containerId);
    router.push(`/journal/${containerId}`);
  } else {
    console.log("未找到容器ID");
    message.info("期刊详情暂无法访问");
  }
};

const navigateToConference = () => {
  console.log("点击会议:", documentData.value?.conference);

  // 使用container_id而不是在document对象上查找
  const containerId = documentData.value?.container_id;
  if (containerId && documentData.value?.conference) {
    console.log("导航到会议详情页:", containerId);
    router.push(`/conference/${containerId}`);
  } else {
    console.log("未找到容器ID");
    message.info("会议详情暂无法访问");
  }
};

// 格式化作者角色
const formatAuthorRole = (role: string) => {
  const roleMap: { [key: string]: string } = {
    first: "第一作者",
    corresponding: "通讯作者",
    additional: "合作作者",
    other: "其他",
  };
  return roleMap[role] || "其他";
};

// 根据作者角色获取颜色
const getAuthorColor = (role: string) => {
  const colorMap: { [key: string]: string } = {
    first: "blue",
    corresponding: "purple",
    additional: "green",
    other: "default",
  };
  return colorMap[role] || "default";
};

// 格式化日期
const formatDate = (dateStr: string, includeTime = false) => {
  if (!dateStr) return "";
  try {
    const date = new Date(dateStr);
    if (includeTime) {
      return date.toLocaleString("zh-CN");
    }
    return date.toLocaleDateString("zh-CN");
  } catch (e) {
    return dateStr;
  }
};

// 检查是否是PDF URL
const isPdfUrl = (url: string) => {
  if (!url) return false;
  return url.toLowerCase().endsWith(".pdf");
};

onMounted(() => {
  fetchDocumentData();
});
</script>

<style scoped>
.document-detail-container {
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

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.document-title {
  font-family: "Playfair Display", serif;
  font-size: 2.2rem;
  margin: 0;
  flex: 1;
  color: #303133;
}

.document-actions {
  display: flex;
  gap: 10px;
}

.info-card {
  margin-bottom: 24px;
}

.info-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  color: #555;
}

.section-icon {
  margin-right: 6px;
}

.authors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.author-tag {
  margin-right: 8px;
  padding: 6px 10px;
  font-size: 14px;
}

.author-role {
  opacity: 0.8;
  margin-left: 4px;
}

.keywords-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-info {
  color: #909399;
  font-size: 13px;
  margin-top: 10px;
}

.section-header {
  font-family: "Playfair Display", serif;
  font-size: 1.6rem;
  margin: 30px 0 15px;
  color: #303133;
  display: flex;
  align-items: center;
}

.notes-section {
  margin-top: 20px;
}

.note-card {
  margin-bottom: 24px;
}

.note-content {
  line-height: 1.6;
  color: #606266;
}

/* Markdown 样式 */
.note-content :deep(h1),
.note-preview :deep(h1) {
  font-size: 1.8em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.note-content :deep(h2),
.note-preview :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.note-content :deep(h3),
.note-preview :deep(h3) {
  font-size: 1.25em;
}

.note-content :deep(ul),
.note-preview :deep(ul),
.note-content :deep(ol),
.note-preview :deep(ol) {
  padding-left: 1.2em;
  margin: 1em 0;
}

.note-content :deep(code),
.note-preview :deep(code) {
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-size: 85%;
  padding: 0.2em 0.4em;
  font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, monospace;
}

.note-content :deep(blockquote),
.note-preview :deep(blockquote) {
  border-left: 0.25em solid #dfe2e5;
  color: #6a737d;
  padding: 0 1em;
}

.note-content :deep(img),
.note-preview :deep(img) {
  max-width: 100%;
}

.note-preview {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 16px;
  min-height: 200px;
  overflow-y: auto;
  max-height: 500px;
}

.preview-container {
  margin-top: 16px;
  border: 1px solid #eaeaea;
  border-radius: 4px;
  overflow: hidden;
}

.pdf-preview {
  width: 100%;
  height: 600px;
  border: none;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  background-color: #f8f9fa;
}

.pdf-icon {
  font-size: 48px;
  color: #f56c6c;
  margin-bottom: 16px;
}

.stars-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.clickable {
  cursor: pointer;
  transition: all 0.3s;
}

.clickable:hover {
  text-decoration: underline;
  opacity: 0.8;
}

.journal-name,
.conference-name,
.doi-link,
.folder-link {
  color: #1890ff;
  text-decoration: none;
  transition: color 0.3s;
}

.journal-name:hover,
.conference-name:hover,
.doi-link:hover,
.folder-link:hover {
  color: #40a9ff;
  text-decoration: underline;
}

.markdown-tips {
  margin-top: 12px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.markdown-tips ul {
  padding-left: 20px;
  margin: 8px 0 0;
}

/* 引入Playfair Display字体 */
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;700&display=swap");
</style>
