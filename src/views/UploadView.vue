<template>
  <div class="upload">
    <h1>PDF文件批量上传</h1>
    <div class="upload-container">
      <div
        class="upload-area"
        @click="triggerFileInput"
        @drop.prevent="handleDrop"
        @dragover.prevent
      >
        <div v-if="!selectedFiles.length">
          <p>拖拽PDF文件到此处，或</p>
          <button class="select-button">选择文件</button>
          <p>支持批量上传PDF文件</p>
        </div>
        <div v-else class="file-list">
          <h3>已选择文件 ({{ selectedFiles.length }})</h3>
          <ul>
            <li v-for="(file, index) in selectedFiles" :key="index">
              {{ file.name }} ({{ formatFileSize(file.size) }})
            </li>
          </ul>
          <div class="button-group">
            <button class="select-button" @click.stop="triggerFileInput">
              添加更多文件
            </button>
            <button
              class="upload-button"
              @click.stop="uploadFiles"
              :disabled="uploading"
            >
              {{ uploading ? "上传中..." : "开始上传" }}
            </button>
            <button
              class="clear-button"
              @click.stop="clearFiles"
              :disabled="uploading"
            >
              清空文件
            </button>
          </div>
        </div>
      </div>
      <input
        type="file"
        ref="fileInput"
        multiple
        accept=".pdf"
        style="display: none"
        @change="handleFileSelect"
      />
    </div>

    <div v-if="uploadResult" class="upload-result">
      <h2>上传结果</h2>
      <div :class="uploadResult.success ? 'success' : 'error'">
        {{ uploadResult.message }}
      </div>
      <div
        v-if="uploadResult.files && uploadResult.files.length"
        class="uploaded-files"
      >
        <h3>上传的文件:</h3>
        <ul>
          <li v-for="(file, index) in uploadResult.files" :key="index">
            {{ file }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import axios from "axios";

export default defineComponent({
  name: "UploadView",
  setup() {
    const fileInput = ref<HTMLInputElement | null>(null);
    const selectedFiles = ref<File[]>([]);
    const uploading = ref(false);
    const uploadResult = ref<{
      success: boolean;
      message: string;
      files?: string[];
    } | null>(null);

    const triggerFileInput = () => {
      fileInput.value?.click();
    };

    const handleFileSelect = (event: Event) => {
      const input = event.target as HTMLInputElement;
      if (input.files) {
        addFiles(Array.from(input.files));
      }
    };

    const handleDrop = (event: DragEvent) => {
      if (event.dataTransfer?.files) {
        addFiles(Array.from(event.dataTransfer.files));
      }
    };

    const addFiles = (files: File[]) => {
      const pdfFiles = files.filter((file) => file.type === "application/pdf");
      if (pdfFiles.length) {
        selectedFiles.value.push(...pdfFiles);
      }
    };

    const clearFiles = () => {
      selectedFiles.value = [];
      if (fileInput.value) {
        fileInput.value.value = "";
      }
    };

    const formatFileSize = (bytes: number): string => {
      if (bytes < 1024) {
        return bytes + " B";
      } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + " KB";
      } else {
        return (bytes / (1024 * 1024)).toFixed(2) + " MB";
      }
    };

    const uploadFiles = async () => {
      if (selectedFiles.value.length === 0) {
        uploadResult.value = {
          success: false,
          message: "请先选择文件",
        };
        return;
      }

      uploading.value = true;
      uploadResult.value = null;

      try {
        const formData = new FormData();
        selectedFiles.value.forEach((file) => {
          formData.append("pdfs", file);
        });

        const response = await axios.post(
          "http://localhost:5000/upload-pdfs",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        uploadResult.value = {
          success: true,
          message: response.data.message,
          files: response.data.files,
        };

        // 上传成功后清空文件列表
        clearFiles();
      } catch (error) {
        let message = "上传失败";
        if (axios.isAxiosError(error) && error.response) {
          message = error.response.data.message || message;
        }
        uploadResult.value = {
          success: false,
          message,
        };
      } finally {
        uploading.value = false;
      }
    };

    return {
      fileInput,
      selectedFiles,
      uploading,
      uploadResult,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      clearFiles,
      uploadFiles,
      formatFileSize,
    };
  },
});
</script>

<style scoped>
.upload {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.upload-container {
  margin-top: 20px;
}

.upload-area {
  border: 2px dashed #42b983;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  background-color: #f9f9f9;
  transition: background-color 0.3s;
}

.upload-area:hover {
  background-color: #f0f0f0;
}

.select-button {
  padding: 10px 15px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
}

.upload-button {
  padding: 10px 15px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
}

.clear-button {
  padding: 10px 15px;
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin: 10px;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.file-list {
  text-align: left;
}

.file-list ul {
  max-height: 200px;
  overflow-y: auto;
  margin: 15px 0;
  padding-left: 20px;
  list-style-type: disc;
}

.file-list li {
  margin: 5px 0;
  display: block;
}

.button-group {
  text-align: center;
  margin-top: 15px;
}

.upload-result {
  margin-top: 30px;
  padding: 15px;
  border-radius: 4px;
}

.success {
  color: #2ecc71;
  font-weight: bold;
}

.error {
  color: #e74c3c;
  font-weight: bold;
}

.uploaded-files {
  margin-top: 15px;
}

.uploaded-files ul {
  padding-left: 20px;
  list-style-type: disc;
}
</style>
