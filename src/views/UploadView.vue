<template>
  <div class="upload-container">
    <a-card class="upload-card">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 方案一：PDF上传与解析 -->
        <a-tab-pane key="pdf" tab="上传PDF文件">
          <a-alert
            v-if="targetFolderInfo"
            message="文件将上传至以下文件夹"
            :description="targetFolderInfo"
            type="info"
            show-icon
            class="folder-alert"
          />

          <a-row :gutter="16">
            <!-- 文件夹选择 -->
            <a-col :span="24">
              <a-form-item label="选择文件夹">
                <a-tree-select
                  v-model:value="selectedFolderId"
                  show-search
                  style="width: 100%"
                  :dropdown-style="{ maxHeight: '400px', overflow: 'auto' }"
                  placeholder="请选择保存位置"
                  allow-clear
                  tree-default-expand-all
                  :tree-data="folderTreeData"
                  :field-names="{
                    children: 'children',
                    label: 'label',
                    value: 'id',
                  }"
                />
              </a-form-item>
            </a-col>

            <!-- 解析方式选择 -->
            <a-col :span="24">
              <a-form-item label="选择解析方式">
                <a-radio-group v-model:value="parseMethod" button-style="solid">
                  <a-radio-button value="normal">普通解析</a-radio-button>
                  <a-radio-button value="ai" class="ai-button">
                    <robot-outlined />
                    AI智能解析
                  </a-radio-button>
                </a-radio-group>
                <div class="method-hint">
                  {{ parseMethodHint }}
                </div>
              </a-form-item>
            </a-col>
          </a-row>

          <!-- PDF拖放上传区域 -->
          <a-upload-dragger
            v-model:fileList="pdfFileList"
            :multiple="true"
            :before-upload="beforePdfUpload"
            :remove="handleFileRemove"
            @drop="handleFileDrop"
            accept=".pdf"
            :customRequest="customRequest"
            :show-preview-icon="true"
            :show-remove-icon="true"
          >
            <p class="ant-upload-drag-icon">
              <inbox-outlined />
            </p>
            <p class="ant-upload-text">点击或拖动PDF文件到此区域上传</p>
            <p class="ant-upload-hint">
              支持批量上传PDF文件，将自动解析文献元数据
            </p>
          </a-upload-dragger>

          <div class="upload-actions">
            <a-button
              type="primary"
              :disabled="pdfFileList.length === 0 || !selectedFolderId"
              :loading="uploading"
              @click="handlePdfUpload"
              size="large"
            >
              <template #icon><cloud-upload-outlined /></template>
              开始上传并解析
            </a-button>
          </div>
        </a-tab-pane>

        <!-- 方案二：批量导入元数据 -->
        <a-tab-pane key="metadata" tab="批量导入元数据">
          <!-- 文件夹选择 -->
          <a-form-item label="选择文件夹">
            <a-tree-select
              v-model:value="selectedFolderId"
              show-search
              style="width: 100%"
              :dropdown-style="{ maxHeight: '400px', overflow: 'auto' }"
              placeholder="请选择保存位置"
              allow-clear
              tree-default-expand-all
              :tree-data="folderTreeData"
              :field-names="{
                children: 'children',
                label: 'label',
                value: 'id',
              }"
            />
          </a-form-item>

          <!-- 元数据文件上传区域 -->
          <a-upload-dragger
            v-model:fileList="metadataFileList"
            :multiple="true"
            :before-upload="beforeMetadataUpload"
            :remove="handleFileRemove"
            accept=".json,.xlsx,.csv"
          >
            <p class="ant-upload-drag-icon">
              <file-outlined />
            </p>
            <p class="ant-upload-text">点击或拖动元数据文件到此区域上传</p>
            <p class="ant-upload-hint">
              支持JSON、XLSX和CSV文件格式的批量元数据导入
            </p>
          </a-upload-dragger>

          <div class="upload-actions">
            <a-button
              type="primary"
              :disabled="metadataFileList.length === 0 || !selectedFolderId"
              :loading="uploading"
              @click="handleMetadataUpload"
              size="large"
            >
              <template #icon><import-outlined /></template>
              批量导入元数据
            </a-button>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 解析结果预览与编辑弹窗 -->
    <a-modal
      v-model:visible="parseResultVisible"
      :width="900"
      title="解析结果预览"
      @ok="handleConfirmUpload"
      @cancel="handleCancelUpload"
      :maskClosable="false"
      :confirmLoading="confirmLoading"
    >
      <!-- 这里我们使用自定义footer而不是:footer绑定 -->
      <template #footer>
        <div v-if="parseResults.length <= 1">
          <a-button key="back" @click="handleCancelUpload">取消</a-button>
          <a-button
            key="submit"
            type="primary"
            :loading="confirmLoading"
            @click="handleConfirmUpload"
          >
            确认并上传
          </a-button>
        </div>
        <div v-else>
          <a-button key="back" @click="handleCancelUpload">取消</a-button>
          <a-button key="prev" @click="prevFile" :disabled="currentStep === 0">
            上一个文件
          </a-button>
          <a-button
            key="next"
            @click="nextFile"
            :disabled="currentStep >= parseResults.length - 1"
          >
            下一个文件
          </a-button>
          <a-button
            key="submit"
            type="primary"
            :loading="confirmLoading"
            @click="handleConfirmUpload"
          >
            确认并上传全部
          </a-button>
        </div>
      </template>

      <a-steps
        :current="currentStep"
        size="small"
        class="parse-steps"
        v-if="parseResults.length > 1"
      >
        <a-step
          v-for="(result, index) in parseResults"
          :key="index"
          :title="`文件 ${index + 1}`"
          :description="getShortFileName(result.fileName)"
        />
      </a-steps>

      <div v-if="parseResults.length > 0 && currentParseResult">
        <div class="parse-info">
          <div class="parse-file-name">
            <file-pdf-outlined /> {{ currentParseResult.fileName }}
          </div>
          <a-tag :color="parseMethod === 'ai' ? '#722ed1' : '#108ee9'">
            {{ parseMethod === "ai" ? "AI解析" : "普通解析" }}
          </a-tag>
        </div>

        <a-form layout="vertical" :model="currentParseResult.metadata">
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="标题" required>
                <a-input v-model:value="currentParseResult.metadata.title" />
              </a-form-item>
            </a-col>
          </a-row>

          <a-divider>作者信息</a-divider>

          <div class="authors-container">
            <div
              v-for="(author, aIndex) in currentParseResult.metadata.authors"
              :key="aIndex"
              class="author-item"
            >
              <a-row :gutter="16">
                <a-col :span="10">
                  <a-form-item :label="`作者 ${aIndex + 1} 名称`">
                    <a-input v-model:value="author.name" />
                  </a-form-item>
                </a-col>
                <a-col :span="10">
                  <a-form-item label="角色">
                    <a-select v-model:value="author.sequence">
                      <a-select-option value="first">第一作者</a-select-option>
                      <a-select-option value="corresponding"
                        >通讯作者</a-select-option
                      >
                      <a-select-option value="additional"
                        >合作者</a-select-option
                      >
                      <a-select-option value="-">未知</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="4">
                  <a-form-item label=" ">
                    <a-button
                      danger
                      type="dashed"
                      @click="removeAuthor(aIndex)"
                      block
                    >
                      删除
                    </a-button>
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="机构">
                    <a-input v-model:value="author.institution" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="机构所在地">
                    <a-input v-model:value="author.location" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="邮箱">
                    <a-input v-model:value="author.email" />
                  </a-form-item>
                </a-col>
              </a-row>

              <a-divider
                v-if="aIndex < currentParseResult.metadata.authors.length - 1"
                dashed
              />
            </div>
          </div>

          <a-button
            type="dashed"
            block
            @click="addAuthor"
            style="margin-bottom: 24px"
          >
            <plus-outlined /> 添加作者
          </a-button>

          <a-divider>其他信息</a-divider>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="DOI">
                <a-input v-model:value="currentParseResult.metadata.doi" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="出版日期">
                <!-- 替换日期选择器为普通HTML5日期输入框 -->
                <a-input
                  type="date"
                  v-model:value="currentParseResult.metadata.publishDate"
                  style="width: 100%"
                  placeholder="YYYY-MM-DD"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="期刊">
                <a-input v-model:value="currentParseResult.metadata.journal" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="会议">
                <a-input
                  v-model:value="currentParseResult.metadata.conference"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="关键词">
            <a-select
              v-model:value="currentParseResult.metadata.keywords"
              mode="tags"
              style="width: 100%"
              placeholder="输入关键词后按回车确认"
              :token-separators="[',']"
            ></a-select>
          </a-form-item>
        </a-form>
      </div>
    </a-modal>

    <!-- 上传结果提示 -->
    <a-modal
      v-model:visible="uploadResultVisible"
      :closable="true"
      :mask-closable="true"
      :footer="null"
      :width="600"
    >
      <template #title>
        <div class="result-title">
          <check-circle-outlined v-if="uploadSuccess" class="success-icon" />
          <close-circle-outlined v-else class="error-icon" />
          {{ uploadSuccess ? "上传成功" : "上传失败" }}
        </div>
      </template>

      <div class="upload-result-content">
        <p>{{ uploadResultMessage }}</p>

        <a-list
          v-if="uploadSuccess && uploadedFiles.length"
          size="small"
          bordered
          class="uploaded-files-list"
        >
          <a-list-item v-for="(file, index) in uploadedFiles" :key="index">
            <file-pdf-outlined /> {{ file }}
          </a-list-item>
        </a-list>
      </div>

      <div class="upload-result-footer">
        <a-button @click="uploadResultVisible = false">关闭</a-button>
        <a-button
          type="primary"
          @click="goToFolder"
          v-if="uploadSuccess && selectedFolderId"
        >
          查看文件夹
        </a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { message, Modal, Upload } from "ant-design-vue"; // 添加Upload引入
import {
  InboxOutlined,
  FileOutlined,
  FilePdfOutlined,
  PlusOutlined,
  CloudUploadOutlined,
  ImportOutlined,
  RobotOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DeleteOutlined, // 添加删除图标
  EyeOutlined, // 添加预览图标
} from "@ant-design/icons-vue";
import { getFolderStructure } from "@/api/load";
import {
  uploadPdfFiles,
  parsePdfMetadata,
  parsePdfMetadataWithAI,
  uploadMetadataFiles,
  saveMetadataOnly,
} from "@/api/upload";

// 路由和导航
const route = useRoute();
const router = useRouter();

// 基本状态
const activeTab = ref<string>("pdf");
const uploading = ref<boolean>(false);
const selectedFolderId = ref<string | number>("");
const parseMethod = ref<string>("normal");
const folderTreeData = ref<any[]>([]);
const targetFolderId = ref<string | undefined>(undefined);
const targetFolderInfo = ref<string | null>(null);

// 文件列表状态
const pdfFileList = ref<any[]>([]);
const metadataFileList = ref<any[]>([]);

// 解析结果状态
const parseResultVisible = ref<boolean>(false);
const currentStep = ref<number>(0);
const confirmLoading = ref<boolean>(false);
const parseResults = ref<any[]>([]);

// 上传结果状态
const uploadResultVisible = ref<boolean>(false);
const uploadSuccess = ref<boolean>(false);
const uploadResultMessage = ref<string>("");
const uploadedFiles = ref<string[]>([]);

// 计算属性
const currentParseResult = computed(() => {
  if (
    parseResults.value.length &&
    currentStep.value < parseResults.value.length
  ) {
    return parseResults.value[currentStep.value];
  }
  return null;
});

const parseMethodHint = computed(() => {
  return parseMethod.value === "ai"
    ? "AI智能解析：使用高级算法精准提取元数据，更适合复杂格式的文献，解析速度较慢"
    : "普通解析：快速提取基本元数据，适合标准格式的文献";
});

// 初始化
onMounted(async () => {
  if (route.query.folderId) {
    targetFolderId.value = route.query.folderId as string;
    selectedFolderId.value = targetFolderId.value;

    // 获取文件夹名称
    try {
      const response = await getFolderInfo(targetFolderId.value);
      if (response && response.name) {
        targetFolderInfo.value = `${response.path || response.name}`;
      }
    } catch (error) {
      console.error("获取文件夹信息失败", error);
    }
  }

  // 获取文件夹结构
  await fetchFolderStructure();
});

// 获取文件夹信息
async function getFolderInfo(folderId: string): Promise<any> {
  // 模拟函数，实际应该从API获取
  // 这部分应该在 api/load.js 中实现
  return {
    id: folderId,
    name: `文件夹 ${folderId}`,
    path: `我的文献库/文件夹 ${folderId}`,
  };
}

// 获取文件夹树结构
async function fetchFolderStructure() {
  try {
    const response = await getFolderStructure();
    if (response && response.data && response.data.data) {
      folderTreeData.value = response.data.data;
    }
  } catch (error) {
    console.error("获取文件夹结构失败", error);
    message.error("获取文件夹结构失败");
  }
}

// 添加自定义上传方法 - 阻止默认的自动上传行为
const customRequest = (options: any) => {
  // 将文件存储在 fileList 中但不实际上传
  // 保存原始文件对象
  const { file } = options;

  // 如果需要，可以在这里模拟进度事件
  if (options.onProgress) {
    options.onProgress({ percent: 100 });
  }

  // 成功回调
  if (options.onSuccess) {
    options.onSuccess("OK");
  }
};

// 修改文件预览处理
// const handlePreview = async (file: any) => {
//   if (file.url || file.thumbUrl) {
//     window.open(file.url || file.thumbUrl);
//   } else {
//     message.info(
//       `文件名: ${file.name}, 大小: ${(file.size / 1024 / 1024).toFixed(2)}MB`
//     );
//   }
// };

// 文件上传前验证
function beforePdfUpload(file: File) {
  const isPDF = file.type === "application/pdf";
  if (!isPDF) {
    message.error(`${file.name} 不是PDF文件`);
    return Upload.LIST_IGNORE;
  }

  // 返回 false 阻止自动上传，而是等待用户点击"开始上传并解析"按钮
  return false;
}

function beforeMetadataUpload(file: File) {
  const isJson = file.type === "application/json";
  const isExcel =
    file.type ===
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
    file.type === "application/vnd.ms-excel";
  const isCsv = file.type === "text/csv";

  const isValid = isJson || isExcel || isCsv;
  if (!isValid) {
    message.error(`${file.name} 不是支持的文件格式`);
    return Upload.LIST_IGNORE;
  }

  // 返回 false 阻止自动上传
  return false;
}

// 文件列表处理
function handleFileRemove(file: any) {
  if (activeTab.value === "pdf") {
    pdfFileList.value = pdfFileList.value.filter(
      (item) => item.uid !== file.uid
    );
  } else {
    metadataFileList.value = metadataFileList.value.filter(
      (item) => item.uid !== file.uid
    );
  }
  return true;
}

function handleFileDrop(e: any) {
  console.log("Dropped files", e.dataTransfer.files);
  // 拖放事件已由 a-upload-dragger 组件处理
}

// PDF文件上传与解析
async function handlePdfUpload() {
  if (pdfFileList.value.length === 0) {
    message.warning("请选择PDF文件");
    return;
  }

  if (!selectedFolderId.value) {
    message.warning("请选择保存文件夹");
    return;
  }

  uploading.value = true;
  message.loading("正在解析PDF文件...", 0);

  try {
    // 使用选定的解析方法解析每个文件
    parseResults.value = [];
    const files = pdfFileList.value.map((file) => file.originFileObj);

    for (const file of files) {
      let result;
      if (parseMethod.value === "ai") {
        result = await parsePdfMetadataWithAI(file);
      } else {
        result = await parsePdfMetadata(file);
      }

      // 将每个解析结果添加到列表中
      if (result && result.metadata) {
        parseResults.value.push({
          fileName: file.name,
          file: file,
          metadata: formatMetadata(result.metadata),
        });
      }
      // console.log("解析结果：", parseResults);
    }

    // 关闭加载提示
    message.destroy();

    if (parseResults.value.length > 0) {
      // 显示解析结果预览
      currentStep.value = 0;
      parseResultVisible.value = true;
    } else {
      message.error("无法解析所选PDF文件");
      uploading.value = false;
    }
  } catch (error) {
    console.error("解析PDF失败", error);
    message.error("解析PDF失败");
    uploading.value = false;
  }
}

// 格式化元数据，确保包含所有必要的字段
function formatMetadata(metadata: any) {
  const authors = metadata.authors || [];
  const formattedAuthors =
    authors.map((author: string, index: number) => {
      return {
        name: author || "",
        sequence: metadata.sequence?.[index] || "-",
        institution: metadata.institutions?.[index] || "",
        location: metadata.institution_location?.[index] || "",
        email: metadata.email?.[index] || "",
      };
    }) || [];

  if (formattedAuthors.length === 0) {
    formattedAuthors.push({
      name: "",
      sequence: "-",
      institution: "",
      location: "",
      email: "",
    });
  }

  // 更稳健地处理 publishDate - 确保它是字符串格式
  const rawPublishDate = metadata.publishDate;
  const finalPublishDate =
    rawPublishDate &&
    typeof rawPublishDate === "string" &&
    rawPublishDate.trim() !== ""
      ? rawPublishDate
      : ""; // 返回空字符串而不是null，更适合input控件

  return {
    title: metadata.title || "",
    authors: formattedAuthors,
    doi: metadata.doi || null,
    publishDate: finalPublishDate, // 使用处理后的日期
    journal: metadata.journal || null,
    conference: metadata.conference || null,
    keywords: metadata.keywords || [],
  };
}

// 添加新作者
function addAuthor() {
  if (currentParseResult.value) {
    currentParseResult.value.metadata.authors.push({
      name: "",
      sequence: "-",
      institution: "",
      location: "",
      email: "",
    });
  }
}

// 删除作者
function removeAuthor(index: number) {
  if (
    currentParseResult.value &&
    currentParseResult.value.metadata.authors.length > 1
  ) {
    currentParseResult.value.metadata.authors.splice(index, 1);
  } else {
    message.warning("至少需要保留一个作者");
  }
}

// 文件导航
function nextFile() {
  if (currentStep.value < parseResults.value.length - 1) {
    currentStep.value++;
  }
}

function prevFile() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

// 确认上传已解析的文件
async function handleConfirmUpload() {
  confirmLoading.value = true;

  try {
    // 将元数据从格式化后的对象转回API所需的格式
    const metadataToUpload = parseResults.value.map((result) => {
      // 处理 authors 数组和相关字段
      const metadata = { ...result.metadata };
      const authorsData = metadata.authors.map((a) => a.name);
      const sequenceData = metadata.authors.map((a) => a.sequence);
      const institutionsData = metadata.authors.map((a) => a.institution);
      const locationsData = metadata.authors.map((a) => a.location);
      const emailsData = metadata.authors.map((a) => a.email);

      // 删除格式化后的作者数组，使用分开的数组
      delete metadata.authors;

      // 构建最终的元数据对象
      return {
        fileName: result.fileName, // 保存原始文件名
        metadata: {
          ...metadata,
          authors: authorsData,
          sequence: sequenceData,
          institutions: institutionsData,
          institution_location: locationsData,
          email: emailsData,
        },
      };
    });

    // 调用API只上传元数据
    const response = await saveMetadataOnly(
      metadataToUpload,
      selectedFolderId.value
    );

    confirmLoading.value = false;
    parseResultVisible.value = false;

    // 显示上传结果
    uploadSuccess.value = true;
    uploadResultMessage.value = response.data?.message || "元数据保存成功";
    uploadedFiles.value = parseResults.value.map((item) => item.fileName);
    uploadResultVisible.value = true;

    // 清空文件列表
    pdfFileList.value = [];
  } catch (error) {
    console.error("保存元数据失败", error);
    confirmLoading.value = false;

    // 显示错误结果
    uploadSuccess.value = false;
    uploadResultMessage.value = "保存失败，请重试";
    uploadResultVisible.value = true;
  } finally {
    uploading.value = false;
  }
}

// 取消上传
function handleCancelUpload() {
  // 保存当前预览窗口的可见状态，用于在用户取消"取消上传"操作后恢复
  const currentVisibility = parseResultVisible.value;

  Modal.confirm({
    title: "确认取消?",
    content: "取消操作将丢失当前的解析结果，确定要取消吗？",
    onOk() {
      // 用户确认取消操作，关闭预览窗口
      parseResultVisible.value = false;
      uploading.value = false;
      confirmLoading.value = false; // 重置加载状态，防止再次打开时按钮显示加载
    },
    onCancel() {
      // 用户取消"取消"操作，确保预览窗口保持打开
      console.log("用户取消了'取消上传'操作，继续编辑");
      parseResultVisible.value = true; // 明确设置为 true，确保窗口显示
    },
  });
}

// 上传元数据文件
async function handleMetadataUpload() {
  if (metadataFileList.value.length === 0) {
    message.warning("请选择元数据文件");
    return;
  }

  if (!selectedFolderId.value) {
    message.warning("请选择保存文件夹");
    return;
  }

  uploading.value = true;
  message.loading("正在上传元数据文件...", 0);

  try {
    const files = metadataFileList.value.map((file) => file.originFileObj);

    // 调用API上传元数据文件
    const response = await uploadMetadataFiles(files, selectedFolderId.value);

    message.destroy();

    // 显示上传结果
    uploadSuccess.value = true;
    uploadResultMessage.value = response.data?.message || "元数据上传成功";
    uploadedFiles.value = metadataFileList.value.map((file) => file.name);
    uploadResultVisible.value = true;

    // 清空文件列表
    metadataFileList.value = [];
  } catch (error) {
    console.error("上传元数据文件失败", error);
    message.error("上传元数据文件失败");
  } finally {
    uploading.value = false;
  }
}

// 跳转到文件夹
function goToFolder() {
  if (selectedFolderId.value) {
    router.push(`/folder/${selectedFolderId.value}`);
    uploadResultVisible.value = false;
  }
}

// 工具函数
function getShortFileName(fileName: string) {
  if (fileName.length > 20) {
    return fileName.substring(0, 17) + "...";
  }
  return fileName;
}
</script>

<style scoped>
.upload-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.upload-card {
  box-shadow: 0 1px 2px -2px rgba(0, 0, 0, 0.16),
    0 3px 6px 0 rgba(0, 0, 0, 0.12), 0 5px 12px 4px rgba(0, 0, 0, 0.09);
}

.folder-alert {
  margin-bottom: 16px;
}

.method-hint {
  margin-top: 8px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.upload-actions {
  margin-top: 24px;
  text-align: center;
}

.ai-button {
  color: #722ed1;
  border: 1px solid #722ed1;
}

.ai-button :deep(.ant-radio-button-checked) {
  background: #f9f0ff;
  border-color: #722ed1;
}

/* 解析步骤样式 */
.parse-steps {
  margin-bottom: 24px;
}

.parse-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
}

.parse-file-name {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.authors-container {
  margin-bottom: 16px;
}

.author-item {
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

/* 上传结果样式 */
.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-icon {
  color: #52c41a;
  font-size: 22px;
}

.error-icon {
  color: #f5222d;
  font-size: 22px;
}

.upload-result-content {
  padding: 16px 0;
}

.uploaded-files-list {
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.upload-result-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 16px;
}
</style>
