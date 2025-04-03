<template>
  <div class="document-edit">
    <div class="edit-header">
      <div class="back-button">
        <el-button @click="goBack" icon="ArrowLeft" size="small"
          >返回</el-button
        >
      </div>
      <h1 class="edit-title">编辑文献信息</h1>
    </div>

    <el-divider />

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else class="edit-form-container">
      <el-form
        ref="documentForm"
        :model="documentForm"
        :rules="formRules"
        label-width="100px"
        label-position="top"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="documentForm.title" placeholder="请输入文献标题" />
        </el-form-item>

        <el-form-item label="作者" prop="authors">
          <el-tag
            v-for="(author, index) in documentForm.authors"
            :key="index"
            closable
            @close="removeAuthor(index)"
            class="tag-input"
          >
            {{ author }}
          </el-tag>
          <el-input
            v-if="authorInputVisible"
            ref="authorInput"
            v-model="authorInputValue"
            class="tag-input-new"
            size="small"
            @keyup.enter="addAuthor"
            @blur="addAuthor"
          />
          <el-button v-else size="small" @click="showAuthorInput">
            + 添加作者
          </el-button>
        </el-form-item>

        <el-form-item label="出版日期">
          <el-date-picker
            v-model="documentForm.publishDate"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="摘要">
          <el-input
            v-model="documentForm.abstract"
            type="textarea"
            :rows="4"
            placeholder="请输入文献摘要"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-tag
            v-for="(tag, index) in documentForm.tags"
            :key="index"
            closable
            @close="removeTag(index)"
            class="tag-input"
          >
            {{ tag }}
          </el-tag>
          <el-input
            v-if="tagInputVisible"
            ref="tagInput"
            v-model="tagInputValue"
            class="tag-input-new"
            size="small"
            @keyup.enter="addTag"
            @blur="addTag"
          />
          <el-button v-else size="small" @click="showTagInput">
            + 添加标签
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="form-actions">
            <el-button @click="goBack">取消</el-button>
            <el-button type="primary" @click="saveDocument" :loading="saving"
              >保存</el-button
            >
          </div>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, FormInstance } from "element-plus";
import { ArrowLeft } from "@element-plus/icons-vue";
import { updateDocumentMetadata } from "@/api/load";

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const saving = ref(false);
const documentId = ref(route.params.id);

// 表单引用
const documentForm = ref<any>({
  title: "",
  authors: [],
  publishDate: "",
  abstract: "",
  tags: [],
});

// 表单验证规则
const formRules = {
  title: [{ required: true, message: "请输入文献标题", trigger: "blur" }],
};

// 作者标签相关
const authorInputVisible = ref(false);
const authorInputValue = ref("");
const authorInput = ref<HTMLInputElement | null>(null);

// 标签相关
const tagInputVisible = ref(false);
const tagInputValue = ref("");
const tagInput = ref<HTMLInputElement | null>(null);

// 表单引用
const documentFormRef = ref<FormInstance>();

// 模拟获取文档详情
const fetchDocumentDetails = async () => {
  loading.value = true;
  try {
    // 在实际应用中，这里应该调用API获取文档详情
    // const response = await getDocumentDetails(documentId.value);
    // const docData = response.data.data;
    // documentForm.value = {
    //   title: docData.title,
    //   authors: docData.authors || [],
    //   publishDate: docData.publishDate,
    //   abstract: docData.abstract,
    //   tags: docData.tags || []
    // };

    // 模拟数据
    setTimeout(() => {
      documentForm.value = {
        title: "深度学习在自然语言处理中的应用研究",
        authors: ["张三", "李四", "王五"],
        publishDate: "2023-06-15",
        abstract:
          "本文探讨了深度学习技术在自然语言处理领域的最新应用和进展。研究表明，基于神经网络的深度学习模型在多项NLP任务中取得了显著的效果提升。本文分析了各种模型架构的优缺点，并探讨了未来可能的研究方向。",
        tags: ["深度学习", "NLP", "神经网络", "人工智能"],
      };
      loading.value = false;
    }, 1000);
  } catch (error) {
    console.error("获取文档详情失败", error);
    ElMessage.error("获取文档详情失败");
    loading.value = false;
  }
};

// 显示添加作者输入框
const showAuthorInput = () => {
  authorInputVisible.value = true;
  nextTick(() => {
    authorInput.value?.focus();
  });
};

// 添加作者
const addAuthor = () => {
  if (
    authorInputValue.value &&
    documentForm.value.authors.indexOf(authorInputValue.value) === -1
  ) {
    documentForm.value.authors.push(authorInputValue.value);
  }
  authorInputVisible.value = false;
  authorInputValue.value = "";
};

// 移除作者
const removeAuthor = (index: number) => {
  documentForm.value.authors.splice(index, 1);
};

// 显示添加标签输入框
const showTagInput = () => {
  tagInputVisible.value = true;
  nextTick(() => {
    tagInput.value?.focus();
  });
};

// 添加标签
const addTag = () => {
  if (
    tagInputValue.value &&
    documentForm.value.tags.indexOf(tagInputValue.value) === -1
  ) {
    documentForm.value.tags.push(tagInputValue.value);
  }
  tagInputVisible.value = false;
  tagInputValue.value = "";
};

// 移除标签
const removeTag = (index: number) => {
  documentForm.value.tags.splice(index, 1);
};

// 保存文档
const saveDocument = async () => {
  if (!documentFormRef.value) return;

  await documentFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true;
      try {
        await updateDocumentMetadata(documentId.value, {
          title: documentForm.value.title,
          authors: documentForm.value.authors,
          publishDate: documentForm.value.publishDate,
          abstract: documentForm.value.abstract,
          tags: documentForm.value.tags,
        });

        ElMessage.success("保存成功");
        router.push(`/document/${documentId.value}`);
      } catch (error) {
        console.error("保存文档失败", error);
        ElMessage.error("保存文档失败");
      } finally {
        saving.value = false;
      }
    } else {
      ElMessage.warning("请填写必填字段");
    }
  });
};

const goBack = () => {
  router.back();
};

onMounted(() => {
  fetchDocumentDetails();
});
</script>

<style scoped>
.document-edit {
  padding: 20px;
}

.edit-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  margin-right: 20px;
}

.edit-title {
  font-size: 22px;
  font-weight: 500;
  color: #303133;
  margin: 0;
}

.loading-container {
  padding: 20px 0;
}

.edit-form-container {
  max-width: 800px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.tag-input {
  margin-right: 8px;
  margin-bottom: 8px;
}

.tag-input-new {
  width: 100px;
  margin-right: 8px;
  vertical-align: bottom;
}
</style>
