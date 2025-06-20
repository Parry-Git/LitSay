<template>
  <div class="upload-container">
    <a-card class="upload-card">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 方案一：PDF上传与解析 -->
        <a-tab-pane key="pdf" tab="上传PDF文件">
          <a-alert
            v-if="targetFolderInfo"
            message="文件将上传至以下文件夹"
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
                    <!--                    <robot-outlined />-->
                    <ExperimentOutlined />
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
            accept=".json,.csv"
          >
            <p class="ant-upload-drag-icon">
              <file-outlined />
            </p>
            <p class="ant-upload-text">点击或拖动元数据文件到此区域上传</p>
            <p class="ant-upload-hint">支持JSON、CSV文件格式的批量元数据导入</p>
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
            <!-- 添加格式要求按钮 -->
            <a-button
              type="link"
              @click="showFormatRequirements = true"
              size="large"
            >
              <template #icon><question-circle-outlined /></template>
              具体要求
            </a-button>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 格式要求浮窗 -->
    <a-modal
      v-model:visible="showFormatRequirements"
      title="文件格式要求"
      width="800px"
      @cancel="showFormatRequirements = false"
      :footer="null"
    >
      <a-tabs default-active-key="json">
        <a-tab-pane key="json" tab="JSON格式">
          <div class="format-requirements">
            <p>
              JSON文件应包含元数据数组，每个元素表示一个文献的元数据。格式如下：
            </p>
            <a-card class="code-card">
              <pre class="code-block"><code>{{ jsonExample }}</code></pre>
              <a-button
                class="copy-btn"
                type="primary"
                size="small"
                @click="copyToClipboard(jsonExample)"
              >
                <template #icon><copy-outlined /></template>
                复制示例
              </a-button>
            </a-card>
            <div class="format-notes">
              <h4>要求说明：</h4>
              <ul>
                <li>必须是有效的JSON数组格式</li>
                <li>title（标题）字段为必填项</li>
                <li>authors（作者）应为字符串数组</li>
                <li>
                  sequence、institutions、institution_location、email等数组字段长度应与authors一致
                </li>
                <li>
                  如提供journal字段，则conference相关字段应为null，反之亦然
                </li>
                <li>local_url字段可用于提供文献在本地存储的路径</li>
              </ul>
            </div>
          </div>
        </a-tab-pane>
        <a-tab-pane key="csv" tab="CSV格式">
          <div class="format-requirements">
            <p>CSV文件第一行为字段名称，每行表示一个文献的元数据。格式如下：</p>
            <a-table
              :columns="csvColumns"
              :data-source="csvData"
              :pagination="false"
              size="small"
              bordered
            ></a-table>
            <div class="table-actions">
              <a-button
                type="primary"
                size="small"
                @click="copyToClipboard(csvExample)"
              >
                <template #icon><copy-outlined /></template>
                复制CSV示例
              </a-button>
            </div>
            <div class="format-notes">
              <h4>要求说明：</h4>
              <ul>
                <li>CSV文件必须包含表头行</li>
                <li>title（标题）字段为必填项</li>
                <li>
                  对于多值字段（如authors、keywords等），使用分号(;)分隔值
                </li>
                <li>
                  sequence、institutions、institution_location、email等必须与authors一一对应
                </li>
                <li>
                  如提供journal字段，则conference相关字段应为null，反之亦然
                </li>
                <li>日期格式推荐使用YYYY-MM-DD</li>
                <li>空值可以使用空字符串或"null"表示</li>
              </ul>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-modal>

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

          <!-- 添加文件本地路径字段 -->
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="文件本地路径">
                <a-input
                  v-model:value="currentParseResult.metadata.local_url"
                  placeholder="文件在本地的存储路径"
                />
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
              <a-form-item label="期刊期号">
                <a-input
                  v-model:value="currentParseResult.metadata.journal_issue"
                />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="会议">
                <a-input
                  v-model:value="currentParseResult.metadata.conference"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="会议地点">
                <a-input
                  v-model:value="
                    currentParseResult.metadata.conference_location
                  "
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="会议日期" name="conference_time">
                <a-date-picker
                  v-model:value="
                    currentParseResult.metadata.conference_location
                  "
                  placeholder="选择会议日期"
                  style="width: 100%"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
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

          <!-- 添加文件本地路径预览和编辑
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="文件本地路径" required>
                <a-input
                  v-model:value="currentParseResult.metadata.local_url"
                  placeholder="文件的本地路径"
                  disabled
                />
              </a-form-item>
            </a-col>
          </a-row> -->
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
  ExperimentOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  DeleteOutlined, // 添加删除图标
  EyeOutlined, // 添加预览图标
  QuestionCircleOutlined, // 添加问号图标
  CopyOutlined, // 添加复制图标
} from "@ant-design/icons-vue";
import { getFolderStructure } from "@/api/load";
import {
  uploadPdfFiles,
  parsePdfMetadata,
  parsePdfMetadataWithAI,
  parseMetadataFile,
  saveBatchMetadata,
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
  // console.log("当前解析结果：", parseResults.value);
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

  // 尝试获取文件的本地路径
  try {
    // 将原始File对象扩展，添加localPath属性
    const fileWithPath = Object.assign(file, {
      localPath: extractLocalPath(file),
    });

    // console.log("获取文件本地路径:", fileWithPath.localPath);
  } catch (error) {
    console.error("获取文件本地路径失败:", error);
  }

  // 返回 false 阻止自动上传，而是等待用户点击"开始上传并解析"按钮
  return false;
}

// 提取本地路径的函数
function extractLocalPath(file: File): string {
  // 检查是否存在webkitRelativePath (仅适用于使用input type="file" webkitdirectory的情况)
  if (file.webkitRelativePath) {
    return file.webkitRelativePath;
  }

  // 尝试从文件属性中获取路径信息（在某些浏览器中可用）
  if (file.path) {
    return file.path;
  }

  // 尝试读取可能存在的非标准属性
  if (file.localPath || file.filePath || file.fileName) {
    return file.localPath || file.filePath || file.fileName;
  }

  // 如果无法获取真实路径，至少返回文件名
  return file.name;
}

// 文件上传前验证 - 修改为只允许JSON和CSV
function beforeMetadataUpload(file: File) {
  const isJson =
    file.type === "application/json" || file.name.endsWith(".json");
  const isCsv = file.type === "text/csv" || file.name.endsWith(".csv");

  const isValid = isJson || isCsv;
  if (!isValid) {
    message.error(`${file.name} 不是支持的文件格式，仅支持CSV和JSON文件`);
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

      // 将每个解析结果添加到列表中，合并local_url信息
      if (result && result.metadata) {
        const localUrl = extractLocalPath(file);

        parseResults.value.push({
          fileName: file.name,
          file: file,
          metadata: formatMetadata({
            ...result.metadata,
            local_url: localUrl, // 添加local_url到元数据
          }),
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

// 格式化元数据，确保包含所有必要的字段，包括local_url
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
    journal_issue: metadata.journal_issue || null,
    conference_location: metadata.conference_location || null,
    conference_time: metadata.conference_time || null,
    conference: metadata.conference || null,
    keywords: metadata.keywords || [],
    local_url: metadata.local_url || null, // 添加local_url字段
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
    // 将元数据从格式化后的对象转回API所需的格式，包含local_url
    const metadataToUpload = parseResults.value.map((result) => {
      // 处理 authors 数组和相关字段
      const metadata = { ...result.metadata };
      const authorsData = metadata.authors.map((a) => a.name);
      const sequenceData = metadata.authors.map((a) => a.sequence);
      const institutionsData = metadata.authors.map((a) => a.institution);
      const locationsData = metadata.authors.map((a) => a.location);
      const emailsData = metadata.authors.map((a) => a.email);

      // 保存local_url，确保在删除格式化作者数组前先保存
      const localUrl = metadata.local_url;

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
          local_url: localUrl, // 确保local_url被包含
        },
      };
    });

    // 调用API只上传元数据
    // console.log("准备上传的元数据：", metadataToUpload);
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

// 修改上传元数据文件的处理方法
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
  message.loading("正在解析元数据文件...", 0);

  try {
    const files = metadataFileList.value.map((file) => file.originFileObj);
    let allMetadata: any[] = [];
    let processedFiles: string[] = [];

    // 在前端解析所有文件
    for (const file of files) {
      try {
        const metadata = await parseMetadataFile(file);
        allMetadata = [...allMetadata, ...metadata];
        processedFiles.push(file.name);
      } catch (error) {
        console.error(`解析文件 ${file.name} 失败:`, error);
        message.error(`解析文件 ${file.name} 失败: ${error}`);
      }
    }

    message.destroy();

    if (allMetadata.length === 0) {
      message.error("未能从文件中提取到有效元数据");
      uploading.value = false;
      return;
    }
    // console.log("===解析后的元数据：", allMetadata);

    // 调用API上传解析后的元数据
    const response = await saveBatchMetadata(
      allMetadata,
      selectedFolderId.value
    );

    // 显示上传结果
    uploadSuccess.value = true;
    uploadResultMessage.value = `成功导入 ${allMetadata.length} 条元数据记录`;
    uploadedFiles.value = processedFiles;
    uploadResultVisible.value = true;

    // 清空文件列表
    metadataFileList.value = [];
  } catch (error) {
    console.error("批量导入元数据失败", error);
    message.error("批量导入元数据失败");
    uploadSuccess.value = false;
    uploadResultMessage.value = "批量导入元数据失败，请重试";
    uploadResultVisible.value = true;
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

// 添加格式要求浮窗控制变量
const showFormatRequirements = ref(false);

// JSON示例
const jsonExample = ref(`[
  {
    "title": "机器学习算法综述",
    "authors": ["张三", "李四", "王五"],
    "sequence": ["first", "corresponding", "additional"],
    "institutions": ["北京大学人工智能研究所", "清华大学计算机科学系", "中国科学院"],
    "institution_location": ["北京, 中国", "北京, 中国", "上海, 中国"],
    "email": ["zhangsan@pku.edu.cn", "lisi@tsinghua.edu.cn", "wangwu@cas.cn"],
    "doi": "10.1038/s41586-020-2649-2",
    "publishDate": "2023-03-21",
    "journal": "Nature Machine Intelligence",
    "journal_issue": "Vol. 5, Issue 3",
    "conference": null,
    "conference_location": null,
    "conference_time": null,
    "keywords": ["人工智能", "机器学习", "深度学习", "自然语言处理"],
    "local_url": "C:\\\\Users\\\\Documents\\\\Papers\\\\机器学习算法综述.pdf"
  },
  {
    "title": "深度学习在自然语言处理中的应用",
    "authors": ["赵六", "钱七"],
    "sequence": ["first", "additional"],
    "institutions": ["复旦大学计算机科学学院", "上海交通大学"],
    "institution_location": ["上海, 中国", "上海, 中国"],
    "email": ["zhaoliu@fudan.edu.cn", "qianqi@sjtu.edu.cn"],
    "doi": "10.1109/JPROC.2021.3067762",
    "publishDate": "2022-05-17",
    "journal": null,
    "journal_issue": null,
    "conference": "ACL 2022",
    "conference_location": "都柏林, 爱尔兰",
    "conference_time": "2022-05-22",
    "keywords": ["深度学习", "自然语言处理", "Transformer", "BERT"],
    "local_url": "D:\\\\论文\\\\NLP\\\\深度学习在自然语言处理中的应用.pdf"
  }
]`);

// CSV示例和表格配置
const csvExample =
  ref(`title,authors,sequence,institutions,institution_location,email,doi,publishDate,journal,journal_issue,conference,conference_location,conference_time,keywords,local_url
机器学习算法综述,张三;李四;王五,first;corresponding;additional,北京大学人工智能研究所;清华大学计算机科学系;中国科学院,北京 中国;北京 中国;北京 中国,zhangsan@pku.edu.cn;lisi@tsinghua.edu.cn;wangwu@cas.cn,10.1038/s41586-020-2649-2,2023-03-21,Nature Machine Intelligence,Vol. 5 Issue 3,null,null,null,人工智能;机器学习;深度学习;自然语言处理,C:\\Users\\Documents\\Papers\\机器学习算法综述.pdf
深度学习在自然语言处理中的应用,赵六;钱七,first;additional,复旦大学计算机科学学院;上海交通大学,上海 中国;上海 中国,zhaoliu@fudan.edu.cn;qianqi@sjtu.edu.cn,10.1109/JPROC.2021.3067762,2022-05-17,null,null,ACL 2022,都柏林 爱尔兰,2022-05-22,深度学习;自然语言处理;Transformer;BERT,D:\\论文\\NLP\\深度学习在自然语言处理中的应用.pdf`);

// CSV表格列定义
const csvColumns = [
  { title: "字段名", dataIndex: "field", key: "field", width: 150 },
  { title: "示例值", dataIndex: "example", key: "example" },
  { title: "说明", dataIndex: "description", key: "description" },
];

// CSV表格数据
const csvData = [
  {
    key: "1",
    field: "title",
    example: "机器学习算法综述",
    description: "文献标题（必填）",
  },
  {
    key: "2",
    field: "authors",
    example: "张三;李四;王五",
    description: "作者列表，使用分号(;)分隔",
  },
  {
    key: "3",
    field: "sequence",
    example: "first;corresponding;additional",
    description: "作者角色，与authors对应",
  },
  {
    key: "4",
    field: "institutions",
    example: "北京大学人工智能研究所;...",
    description: "作者单位，与authors对应",
  },
  {
    key: "5",
    field: "institution_location",
    example: "北京, 中国;...",
    description: "单位地址，与authors对应",
  },
  {
    key: "6",
    field: "doi",
    example: "10.1038/s41586-020-2649-2",
    description: "文献DOI号",
  },
  {
    key: "7",
    field: "publishDate",
    example: "2023-03-21",
    description: "发布日期，建议YYYY-MM-DD格式",
  },
  {
    key: "8",
    field: "journal",
    example: "Nature Machine Intelligence",
    description: "期刊名称，如有则conference相关字段为null",
  },
  {
    key: "9",
    field: "journal_issue",
    example: "Vol. 5 Issue 3",
    description: "期刊期号",
  },
  {
    key: "10",
    field: "conference",
    example: "ACL 2022",
    description: "会议名称，如有则journal相关字段为null",
  },
  {
    key: "11",
    field: "keywords",
    example: "人工智能;机器学习;深度学习",
    description: "关键词，使用分号(;)分隔",
  },
  {
    key: "12",
    field: "local_url",
    example: "C:\\Users\\Documents\\Papers\\文件名.pdf",
    description: "本地文件路径",
  },
];

// 复制到剪贴板函数
const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text).then(
    () => {
      message.success("已复制到剪贴板");
    },
    () => {
      message.error("复制失败，请手动复制");
    }
  );
};

// ...existing code...
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
  display: flex;
  align-items: center;
  gap: 10px;
}

.ai-button {
  color: #722ed1;
  border: 1px solid #722ed1;
}

.ai-button :deep(.ant-radio-button-checked) {
  background: #871ccc;
  border-color: #ef2192;
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

/* 格式要求浮窗样式 */
.format-requirements {
  padding: 10px 0;
}

.code-card {
  position: relative;
  margin-bottom: 16px;
  background: #f5f5f5;
}

.code-block {
  margin: 0;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  font-family: "Courier New", Courier, monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

.copy-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0.8;
}

.copy-btn:hover {
  opacity: 1;
}

.format-notes {
  margin-top: 16px;
  padding: 10px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
}

.format-notes h4 {
  margin-top: 0;
  margin-bottom: 8px;
  font-weight: 500;
  color: #d48806;
}

.format-notes ul {
  margin: 0;
  padding-left: 20px;
}

.format-notes li {
  margin-bottom: 4px;
}

.table-actions {
  margin: 16px 0;
  text-align: right;
}
</style>
