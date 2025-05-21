<template>
  <div class="document-detail">
    <div class="document-header">
      <div class="back-button">
        <el-button @click="goBack" icon="ArrowLeft" size="small"
          >返回</el-button
        >
      </div>
      <h1 class="document-title cormorant-font">{{ document.title }}</h1>
      <div class="document-actions">
        <el-button type="primary" size="small" @click="handleEdit">
          <el-icon><Edit /></el-icon>
          编辑元数据
        </el-button>
      </div>
    </div>

    <el-divider />

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="document-content">
      <!-- 使用Ant Design Vue的标签页组件 -->
      <a-tabs default-active-key="1">
        <a-tab-pane key="1" tab="基本信息">
          <a-descriptions
            title="文献信息"
            bordered
            :column="{ xxl: 3, xl: 3, lg: 3, md: 3, sm: 2, xs: 1 }"
          >
            <a-descriptions-item label="标题" :span="3">
              {{ document.title }}
            </a-descriptions-item>

            <!-- 作者信息 -->
            <a-descriptions-item label="作者信息" :span="3">
              <div class="authors-table">
                <a-table
                  :dataSource="formattedAuthors"
                  :columns="authorColumns"
                  :pagination="false"
                  size="small"
                  bordered
                >
                  <template #bodyCell="{ column, record }">
                    <template v-if="column.dataIndex === 'sequence'">
                      <a-tag :color="getSequenceColor(record.sequence)">
                        {{ getSequenceLabel(record.sequence) }}
                      </a-tag>
                    </template>
                  </template>
                </a-table>
              </div>
            </a-descriptions-item>

            <a-descriptions-item label="出版日期">
              {{ document.publishDate || "未知" }}
            </a-descriptions-item>

            <a-descriptions-item label="DOI">
              <a
                v-if="document.doi"
                :href="`https://doi.org/${document.doi}`"
                target="_blank"
                >{{ document.doi }}</a
              >
              <span v-else>未知</span>
            </a-descriptions-item>

            <a-descriptions-item label="上传时间">
              {{ document.uploadTime || "未知" }}
            </a-descriptions-item>

            <!-- 期刊信息 -->
            <a-descriptions-item v-if="document.journal" label="期刊" :span="3">
              {{ document.journal }}
            </a-descriptions-item>

            <!-- 会议信息 -->
            <a-descriptions-item
              v-if="document.conference"
              label="会议"
              :span="3"
            >
              {{ document.conference }}
            </a-descriptions-item>

            <a-descriptions-item label="关键词" :span="3">
              <a-tag
                v-for="(keyword, index) in document.keywords"
                :key="index"
                color="blue"
                class="keyword-tag"
              >
                {{ keyword }}
              </a-tag>
              <span v-if="!document.keywords || document.keywords.length === 0"
                >无关键词</span
              >
            </a-descriptions-item>

            <a-descriptions-item label="评分" :span="3">
              <a-rate
                v-model:value="documentStars"
                :disabled="!editingStars"
                @click="saveRating"
              />
              <a-button type="link" size="small" @click="toggleEditStars">
                {{ editingStars ? "保存" : "编辑" }}
              </a-button>
            </a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>

        <a-tab-pane key="2" tab="阅读笔记">
          <div class="notes-container">
            <div v-if="document.note" class="markdown-content">
              <div v-html="renderedNote"></div>
            </div>
            <a-empty v-else description="暂无阅读笔记" />

            <div class="notes-actions">
              <a-button type="primary" @click="toggleEditNote">
                {{ editingNote ? "保存笔记" : "编辑笔记" }}
              </a-button>
            </div>

            <!-- 编辑笔记的文本区域 -->
            <a-modal
              v-model:visible="editingNote"
              title="编辑阅读笔记"
              width="800px"
              @ok="saveNote"
            >
              <a-tabs default-active-key="edit">
                <a-tab-pane key="edit" tab="编辑">
                  <a-textarea
                    v-model:value="editedNote"
                    :rows="20"
                    placeholder="使用Markdown语法编写笔记"
                  />
                </a-tab-pane>
                <a-tab-pane key="preview" tab="预览">
                  <div
                    class="markdown-preview"
                    v-html="renderedEditedNote"
                  ></div>
                </a-tab-pane>
              </a-tabs>

              <template #footer>
                <a-button key="back" @click="cancelEditNote">取消</a-button>
                <a-button key="submit" type="primary" @click="saveNote"
                  >保存</a-button
                >
              </template>
            </a-modal>
          </div>
        </a-tab-pane>

        <!-- <a-tab-pane key="3" tab="文件预览">
          <div class="pdf-container">
            <a-empty
              v-if="!document.fileUrl"
              description="暂无预览"
              image="https://gw.alipayobjects.com/zos/antfincdn/ZHrcdLPrvN/empty.svg"
            />
            <iframe
              v-else
              :src="document.fileUrl"
              width="100%"
              height="600px"
              frameborder="0"
            ></iframe>
          </div>
        </a-tab-pane> -->
      </a-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Edit, Download } from "@element-plus/icons-vue";
import { getDocumentDetails, updateDocumentMetadata } from "@/api/load";
import MarkdownIt from "markdown-it";

// 尝试导入 markdown-it-katex，如果失败则忽略数学公式支持
let md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
});

try {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const MarkdownItKatex = require("markdown-it-katex");
  md = md.use(MarkdownItKatex);
  console.log("KaTeX 支持已启用");
} catch (e) {
  console.warn("未能加载 KaTeX 支持:", e);
}

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const documentId = ref(route.params.id);
const document = ref<any>({});
const documentStars = ref(0);
const editingStars = ref(false);
const editingNote = ref(false);
const editedNote = ref("");

// 定义作者表格列
const authorColumns = [
  {
    title: "姓名",
    dataIndex: "name",
    key: "name",
  },
  {
    title: "角色",
    dataIndex: "sequence",
    key: "sequence",
  },
  {
    title: "机构",
    dataIndex: "institution",
    key: "institution",
  },
  {
    title: "所在地",
    dataIndex: "location",
    key: "location",
  },
  {
    title: "联系方式",
    dataIndex: "email",
    key: "email",
  },
];

// 格式化作者信息
const formattedAuthors = computed(() => {
  if (!document.value.authors || !document.value.authors.length) {
    return [];
  }

  return document.value.authors.map((author, index) => {
    return {
      key: index,
      name: author || "-",
      sequence: document.value.sequence?.[index] || "-",
      institution: document.value.institutions?.[index] || "-",
      location: document.value.institution_location?.[index] || "-",
      email: document.value.email?.[index] || "-",
    };
  });
});

// 获取作者角色标签颜色
const getSequenceColor = (sequence) => {
  const colors = {
    first: "green",
    corresponding: "purple",
    additional: "blue",
    other: "default",
  };
  return colors[sequence] || "default";
};

// 获取作者角色标签文本
const getSequenceLabel = (sequence) => {
  const labels = {
    first: "第一作者",
    corresponding: "通讯作者",
    additional: "合作者",
    other: "其他",
    "-": "未知",
  };
  return labels[sequence] || sequence;
};

// 渲染笔记
const renderedNote = computed(() => {
  return document.value.note ? md.render(document.value.note) : "";
});

// 预览编辑中的笔记
const renderedEditedNote = computed(() => {
  return editedNote.value ? md.render(editedNote.value) : "";
});

// 获取文档详情
const fetchDocumentDetails = async () => {
  loading.value = true;
  try {
    const response = await getDocumentDetails(documentId.value);

    if (response && response.data && response.data.data) {
      document.value = response.data.data;
      documentStars.value = document.value.stars || 0;
      editedNote.value = document.value.note || "";
    } else if (response) {
      document.value = response;
      documentStars.value = document.value.stars || 0; //
      editedNote.value = document.value.note || ""; //
    }
  } catch (error) {
    console.error("获取文档详情失败", error);
    ElMessage.error("获取文档详情失败");

    // 开发环境下使用模拟数据
    if (process.env.NODE_ENV === "development") {
      // 简单模拟数据
      setTimeout(() => {
        document.value = {
          id: documentId.value,
          title: "深度学习在自然语言处理中的应用研究",
          authors: ["张三", "李四", "王五"],
          sequence: ["first", "corresponding", "additional"],
          institutions: ["北京大学", "清华大学", null],
          institution_location: ["北京, 中国", "北京, 中国", null],
          email: ["zhangsan@pku.edu.cn", "lisi@tsinghua.edu.cn", null],
          abstract:
            "本文探讨了深度学习技术在自然语言处理领域的最新应用和进展...",
          publishDate: "2023-06-15",
          fileType: "PDF",
          fileSize: "2.3 MB",
          uploadTime: "2023-10-20 14:30:22",
          conference: null,
          journal: "IEEE Transactions on Neural Networks and Learning Systems",
          keywords: ["深度学习", "NLP", "神经网络", "人工智能"],
          fileUrl: "https://example.com/sample.pdf",
          stars: 4, // 确保模拟数据也有星级
          note: "# 深度学习笔记\n\n这是一篇关于**深度学习**的笔记。\n\n## 主要内容\n1. 神经网络基础\n2. 循环神经网络\n3. 转换器模型", // 确保模拟数据有笔记
        };
        documentStars.value = document.value.stars || 0;
        editedNote.value = document.value.note || "";
      }, 500);
    }
  } finally {
    loading.value = false;
  }
};

// 切换星级编辑状态
const toggleEditStars = () => {
  editingStars.value = !editingStars.value;
  if (!editingStars.value) {
    saveRating();
  }
};

// 保存评分
const saveRating = async () => {
  try {
    await updateDocumentMetadata(documentId.value, {
      stars: documentStars.value,
    });
    document.value.stars = documentStars.value;
    ElMessage.success("评分已保存");
    editingStars.value = false;
  } catch (error) {
    console.error("保存评分失败", error);
    ElMessage.error("保存评分失败");
  }
};

// 切换笔记编辑状态
const toggleEditNote = () => {
  editingNote.value = !editingNote.value;
  editedNote.value = document.value.note || "";
};

// 取消编辑笔记
const cancelEditNote = () => {
  editingNote.value = false;
  editedNote.value = document.value.note || "";
};

// 保存笔记
const saveNote = async () => {
  try {
    await updateDocumentMetadata(documentId.value, {
      note: editedNote.value,
    });
    document.value.note = editedNote.value;
    ElMessage.success("笔记已保存");
    editingNote.value = false;
  } catch (error) {
    console.error("保存笔记失败", error);
    ElMessage.error("保存笔记失败");
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 编辑元数据
const handleEdit = () => {
  router.push(`/document/${documentId.value}/edit`);
};

// 组件挂载时获取文档详情
onMounted(() => {
  fetchDocumentDetails();
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap");

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

.cormorant-font {
  font-family: "Playfair Display", serif;
  font-weight: 600;
  font-size: 26px;
  letter-spacing: 0.01em;
  line-height: 1.3;
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

.keyword-tag {
  margin-right: 8px;
  margin-bottom: 5px;
}

.pdf-container {
  margin-top: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.notes-container {
  padding: 16px;
  background-color: #fafafa;
  border-radius: 4px;
  min-height: 400px;
}

.notes-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.markdown-content {
  background-color: #ffffff;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-content :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content :deep(p) {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content :deep(blockquote) {
  margin: 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content :deep(code) {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-content :deep(pre) {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier,
    monospace;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.markdown-content :deep(table) {
  display: block;
  width: 100%;
  overflow: auto;
  margin-top: 0;
  margin-bottom: 16px;
  border-spacing: 0;
  border-collapse: collapse;
}

.markdown-content :deep(table tr) {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-content :deep(table th),
.markdown-content :deep(table td) {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-content :deep(table th) {
  font-weight: 600;
}

.markdown-content :deep(table tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

.markdown-content :deep(img) {
  max-width: 100%;
  box-sizing: content-box;
  background-color: #fff;
}

.markdown-preview {
  background-color: #ffffff;
  padding: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-height: 300px;
  max-height: 500px;
  overflow-y: auto;
}

/* 作者表格样式 */
.authors-table {
  width: 100%;
  overflow-x: auto;
}

.authors-table :deep(.ant-table-small) {
  font-size: 13px;
}

.authors-table :deep(.ant-table-cell) {
  padding: 8px 12px;
}
</style>
