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
      <a-skeleton active :paragraph="{ rows: 15 }" />
    </div>

    <div v-else class="edit-form-container">
      <a-form
        ref="documentFormRef"
        :model="documentForm"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item label="标题" name="title">
              <a-input
                v-model:value="documentForm.title"
                placeholder="请输入文献标题"
                size="large"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-divider>作者信息</a-divider>

        <div
          v-for="(author, index) in documentForm.authors"
          :key="author.key || index"
          class="author-item"
        >
          <!-- 第一行：作者名称和角色 -->
          <a-row :gutter="[16, 24]">
            <a-col :span="12">
              <a-form-item
                :label="`作者 ${index + 1} 名称`"
                :name="['authors', index, 'name']"
                :rules="{
                  required: true,
                  message: '请输入作者名称',
                  trigger: 'blur',
                }"
              >
                <a-input v-model:value="author.name" placeholder="作者名称" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item
                :label="`角色`"
                :name="['authors', index, 'sequence']"
              >
                <a-select
                  v-model:value="author.sequence"
                  placeholder="选择角色"
                >
                  <a-select-option value="first">第一作者</a-select-option>
                  <a-select-option value="corresponding"
                    >通讯作者</a-select-option
                  >
                  <a-select-option value="additional">合作者</a-select-option>
                  <a-select-option value="other">其他</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <!-- 第二行：机构和机构所在地 -->
          <a-row :gutter="[16, 24]">
            <a-col :span="12">
              <a-form-item
                :label="`机构`"
                :name="['authors', index, 'institution']"
              >
                <a-input
                  v-model:value="author.institution"
                  placeholder="所属机构"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item
                :label="`机构所在地`"
                :name="['authors', index, 'location']"
              >
                <a-input
                  v-model:value="author.location"
                  placeholder="机构所在地"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <!-- 第三行：邮箱和删除按钮 -->
          <a-row :gutter="[16, 24]">
            <a-col :span="18">
              <a-form-item
                :label="`邮箱`"
                :name="['authors', index, 'email']"
                :rules="[
                  {
                    type: 'email',
                    message: '请输入有效的邮箱地址',
                    trigger: 'blur',
                  },
                ]"
              >
                <a-input v-model:value="author.email" placeholder="联系邮箱" />
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item label=" ">
                <a-button
                  danger
                  type="dashed"
                  @click="removeAuthor(index)"
                  block
                >
                  删除
                </a-button>
              </a-form-item>
            </a-col>
          </a-row>
        </div>
        <a-form-item>
          <a-button type="dashed" @click="addAuthor" block>
            <template #icon><UserAddOutlined /></template>
            添加作者
          </a-button>
        </a-form-item>

        <a-divider>其他信息</a-divider>

        <a-row :gutter="24">
          <a-col :xs="24" :sm="12">
            <a-form-item label="DOI" name="doi">
              <a-input
                v-model:value="documentForm.doi"
                placeholder="请输入DOI"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12">
            <a-form-item label="出版日期" name="publishDate">
              <a-date-picker
                v-model:value="documentForm.publishDate"
                placeholder="选择出版日期"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="24">
          <a-col :xs="24" :sm="12">
            <a-form-item label="期刊" name="journal">
              <a-input
                v-model:value="documentForm.journal"
                placeholder="请输入期刊名称"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12">
            <a-form-item label="会议" name="conference">
              <a-input
                v-model:value="documentForm.conference"
                placeholder="请输入会议名称"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="关键词" name="keywords">
          <a-select
            v-model:value="documentForm.keywords"
            mode="tags"
            style="width: 100%"
            placeholder="输入关键词后按回车确认"
            :token-separators="[',']"
          >
          </a-select>
        </a-form-item>

        <a-form-item label="评分" name="stars">
          <a-rate v-model:value="documentForm.stars" />
        </a-form-item>

        <div class="form-actions">
          <a-button type="default" @click="goBack" style="margin-right: 8px"
            >取消</a-button
          >
          <a-button type="primary" @click="saveDocument" :loading="saving"
            >保存</a-button
          >
          <!--          <a-button-->
          <!--            type="dashed"-->
          <!--            @click="goToNoteEdit"-->
          <!--            style="margin-left: auto"-->
          <!--          >-->
          <!--            <template #icon><EditOutlined /></template>-->
          <!--            编辑阅读笔记-->
          <!--          </a-button>-->
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus"; // ElMessage for consistency if used elsewhere
import { message as AntMessage } from "ant-design-vue"; // Ant Design Vue message
import { ArrowLeft } from "@element-plus/icons-vue";
import { UserAddOutlined, EditOutlined } from "@ant-design/icons-vue";
import { getDocumentDetails, updateDocumentMetadata } from "@/api/load"; // Assuming getDocumentDetails is available
import type { FormInstance, FormProps } from "ant-design-vue";

interface Author {
  key?: number; // For v-for key binding
  name: string;
  sequence: string;
  institution: string;
  location: string;
  email: string;
}

interface DocumentFormState {
  title: string;
  authors: Author[];
  doi: string | null;
  publishDate: string | null;
  journal: string | null;
  conference: string | null;
  keywords: string[];
  uploadTime: string | null;
  stars: number;
  // Add other fields from mock data as needed
  // e.g., folderId, path, note (if editable here)
}

const route = useRoute();
const router = useRouter();
const loading = ref(true);
const saving = ref(false);
const documentId = ref(route.params.id as string);

const documentFormRef = ref<FormInstance>();
const documentForm = reactive<DocumentFormState>({
  title: "",
  authors: [],
  doi: null,
  publishDate: null,
  journal: null,
  conference: null,
  keywords: [],
  uploadTime: null,
  stars: 0,
});

const formRules: FormProps["rules"] = {
  title: [{ required: true, message: "请输入文献标题", trigger: "blur" }],
  // Add more specific rules if needed
};

const fetchDocumentDetails = async () => {
  loading.value = true;
  try {
    const response = await getDocumentDetails(documentId.value);
    let docData;
    if (response && response.data && response.data.data) {
      // Dev mode with mock API structure
      docData = response.data.data;
    } else if (response && response.id) {
      // Dev mode with direct mock data
      docData = response;
    } else {
      AntMessage.error("加载文献数据失败: 无效的数据格式");
      loading.value = false;
      return;
    }

    documentForm.title = docData.title || "";
    documentForm.authors = (docData.authors || []).map((name, index) => ({
      key: Date.now() + index, // Unique key for new items
      name: name || "",
      sequence: docData.sequence?.[index] || "-",
      institution: docData.institutions?.[index] || "",
      location: docData.institution_location?.[index] || "",
      email: docData.email?.[index] || "",
    }));
    documentForm.doi = docData.doi || null;
    documentForm.publishDate = docData.publishDate || null;
    documentForm.journal = docData.journal || null;
    documentForm.conference = docData.conference || null;
    documentForm.keywords = docData.keywords || [];
    documentForm.uploadTime = docData.uploadTime || null;
    documentForm.stars = docData.stars || 0;
  } catch (error) {
    console.error("获取文档详情失败", error);
    AntMessage.error("获取文档详情失败");
  } finally {
    loading.value = false;
  }
};

const addAuthor = () => {
  documentForm.authors.push({
    key: Date.now(), // Unique key
    name: "",
    sequence: "additional", // 更改默认值为 "additional"
    institution: "",
    location: "",
    email: "",
  });
};

const removeAuthor = (index: number) => {
  documentForm.authors.splice(index, 1);
};

const saveDocument = async () => {
  if (!documentFormRef.value) return;
  try {
    await documentFormRef.value.validate();
    saving.value = true;

    // Prepare data for API
    const authorsData = documentForm.authors.map((a) => a.name);
    const sequenceData = documentForm.authors.map((a) => a.sequence);
    const institutionsData = documentForm.authors.map((a) => a.institution);
    const locationsData = documentForm.authors.map((a) => a.location);
    const emailsData = documentForm.authors.map((a) => a.email);

    const payload = {
      title: documentForm.title,
      authors: authorsData,
      sequence: sequenceData,
      institutions: institutionsData,
      institution_location: locationsData,
      email: emailsData,
      doi: documentForm.doi,
      publishDate: documentForm.publishDate,
      journal: documentForm.journal,
      conference: documentForm.conference,
      keywords: documentForm.keywords,
      uploadTime: documentForm.uploadTime,
      stars: documentForm.stars,
      // folderId, path, note might also be part of the payload if editable
    };

    await updateDocumentMetadata(documentId.value, payload);
    AntMessage.success("保存成功");
    router.push(`/document/${documentId.value}`);
  } catch (errorInfo) {
    if (errorInfo.errorFields) {
      AntMessage.warning("请填写所有必填字段并修正错误");
    } else {
      console.error("保存文档失败", errorInfo);
      AntMessage.error("保存文档失败");
    }
  } finally {
    saving.value = false;
  }
};

// 跳转到笔记编辑页面
const goToNoteEdit = () => {
  // 先保存当前表单数据
  saveDocument()
    .then(() => {
      // 保存成功后跳转
      router.push(`/document/${documentId.value}`);
      // 显示提示
      setTimeout(() => {
        AntMessage.info('请在详情页面点击"编辑笔记"按钮编辑阅读笔记');
      }, 500);
    })
    .catch((error) => {
      // 保存失败，不跳转
      console.error("保存失败", error);
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
  background-color: #fff; /* Add background for better contrast */
  border-radius: 8px; /* Optional: add some rounding */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09); /* Optional: add subtle shadow */
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
  padding: 40px 0;
}

.edit-form-container {
  max-width: 900px; /* Increased width for better layout */
  margin: 0 auto; /* Center the form */
}

.author-item {
  padding: 20px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  margin-bottom: 24px;
  background-color: #fafafa;
}

/* 增加作者信息条目内表单项的垂直间距 */
.author-item .ant-form-item {
  margin-bottom: 8px;
}

/* 调整作者条目中的行间距 */
.author-item .ant-row {
  margin-bottom: 16px;
}

/* 确保最后一行没有下边距 */
.author-item .ant-row:last-child {
  margin-bottom: 0;
}

/* 专门针对小屏幕时的垂直布局 */
@media (max-width: 768px) {
  .author-item .ant-col {
    margin-bottom: 16px;
  }

  /* 确保每个表单项之间有足够的空间 */
  .author-item .ant-form-item {
    margin-bottom: 20px;
  }
}

/* 针对最后一个作者条目内的删除按钮，移除其下方的额外间距 */
.author-item .ant-form-item:last-child {
  margin-bottom: 0;
}

/* 直接定位邮箱输入栏 */
.author-item .ant-col:nth-child(5) .ant-form-item,
.author-item .ant-col:nth-child(6) .ant-form-item {
  margin-top: 24px; /* 显著增加上边距 */
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0; /* Add a separator */
}

/* Ensure Ant Design Vue components are styled correctly if needed */
:deep(.ant-form-item-label > label) {
  font-weight: 500; /* Make labels slightly bolder */
}

:deep(.ant-divider-horizontal.ant-divider-with-text) {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

/* 移除关键词 Select 组件的下拉箭头（如果存在且不需要） */
:deep(.ant-select-multiple .ant-select-arrow) {
  display: none;
}
</style>
