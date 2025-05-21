import axios from "axios";
import {
  API_BASE_URL,
  buildApiPath,
  DEFAULT_REQUEST_CONFIG,
  getAuthHeaders,
} from "./config";
import { getCurrentUserId } from "@/api/load";
import { notifyFolderStructureChanged } from "@/services/EventService";

// 判断是否为开发环境
const isDevelopment = process.env.NODE_ENV === "not";

/**
 * 上传PDF文件和解析后的元数据
 * @param files 包含文件和元数据的对象数组
 * @param folderId 目标文件夹ID
 * @returns Promise
 */
export const uploadPdfFiles = async (
  files: Array<{ file: File; metadata: any }>,
  folderId: string | number
) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟上传PDF文件和元数据:", { files, folderId });

    // 模拟上传延迟
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // 返回模拟成功响应
    return Promise.resolve({
      data: {
        code: 0,
        message: "上传成功",
        data: {
          files: files.map((item) => item.file.name),
          folderId,
        },
      },
    });
  }

  // 生产环境使用实际API
  const userId = getCurrentUserId();
  const formData = new FormData();

  // 添加文件到FormData
  files.forEach((item, index) => {
    formData.append(`files[${index}]`, item.file);
    formData.append(`metadata[${index}]`, JSON.stringify(item.metadata));
  });

  if (folderId) {
    formData.append("folderId", folderId.toString());
  }

  if (userId) {
    formData.append("userId", userId);
  }

  try {
    const response = await axios.post(
      buildApiPath("/upload/pdf-with-metadata"),
      formData,
      {
        headers: {
          ...getAuthHeaders(),
          "Content-Type": "multipart/form-data",
        },
      }
    );

    // 上传后触发更新事件
    notifyFolderStructureChanged();

    return response;
  } catch (error) {
    console.error("上传PDF文件失败", error);
    throw error;
  }
};

/**
 * 解析PDF文件元数据 (普通方法)
 * @param file PDF文件
 * @returns Promise 包含解析后的元数据
 */
export const parsePdfMetadata = async (file: File) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟解析PDF文件元数据:", file.name);

    // 模拟解析延迟
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // 生成模拟元数据结果
    return Promise.resolve({
      success: true,
      fileName: file.name,
      metadata: {
        title: file.name.replace(".pdf", ""),
        authors: ["作者1", "作者2"],
        sequence: ["first", "additional"],
        institutions: ["北京大学", "清华大学"],
        institution_location: ["北京, 中国", "北京, 中国"],
        email: ["author1@example.com", "author2@example.com"],
        doi: "10.1234/example.5678",
        publishDate: "2023-01-15",
        journal: "示例期刊",
        conference: null,
        keywords: ["关键词1", "关键词2", "关键词3"],
      },
    });
  }

  // 生产环境使用实际API
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post(buildApiPath("/parse/pdf"), formData, {
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("解析PDF文件失败", error);
    throw error;
  }
};

/**
 * 使用AI方法解析PDF文件元数据
 * @param file PDF文件
 * @returns Promise 包含解析后的元数据
 */
export const parsePdfMetadataWithAI = async (file: File) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟使用AI解析PDF文件元数据:", file.name);

    // 模拟AI解析延迟 (比普通解析更长)
    await new Promise((resolve) => setTimeout(resolve, 3000));

    // 生成模拟AI解析结果 (更详细的信息)
    return Promise.resolve({
      success: true,
      fileName: file.name,
      metadata: {
        title: `${file.name.replace(".pdf", "")} - 高级分析报告`,
        authors: ["张三", "李四", "王五"],
        sequence: ["first", "corresponding", "additional"],
        institutions: [
          "北京大学人工智能研究所",
          "清华大学计算机科学系",
          "中国科学院",
        ],
        institution_location: ["北京, 中国", "北京, 中国", "上海, 中国"],
        email: ["zhangsan@pku.edu.cn", "lisi@tsinghua.edu.cn", "wangwu@cas.cn"],
        doi: "10.1038/s41586-020-2649-2",
        publishDate: "2023-03-21",
        journal: "Nature Machine Intelligence",
        conference: null,
        keywords: [
          "人工智能",
          "机器学习",
          "深度学习",
          "自然语言处理",
          "计算机视觉",
        ],
      },
    });
  }

  // 生产环境使用实际API
  const formData = new FormData();
  formData.append("file", file);
  console.log("====上传的文件formData格式=====:", formData);

  try {
    const response = await axios.post(buildApiPath("/parse/pdf/ai"), formData, {
      headers: {
        ...getAuthHeaders(),
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    console.error("AI解析PDF文件失败", error);
    throw error;
  }
};

/**
 * 上传元数据文件 (JSON/XLSX/CSV)
 * @param files 元数据文件数组
 * @param folderId 目标文件夹ID
 * @returns Promise
 */
export const uploadMetadataFiles = async (
  files: File[],
  folderId: string | number
) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟上传元数据文件:", { files, folderId });

    // 模拟上传延迟
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // 返回模拟成功响应
    return Promise.resolve({
      data: {
        code: 0,
        message: `成功导入 ${files.length} 个文献的元数据`,
        data: {
          files: files.map((file) => file.name),
          folderId,
          importedCount: files.length * 3 + 2, // 模拟导入的数量大于文件数
        },
      },
    });
  }

  // 生产环境使用实际API
  const userId = getCurrentUserId();
  const formData = new FormData();

  files.forEach((file, index) => {
    formData.append(`files[${index}]`, file);
  });

  if (folderId) {
    formData.append("folderId", folderId.toString());
  }

  if (userId) {
    formData.append("userId", userId);
  }

  try {
    const response = await axios.post(
      buildApiPath("/upload/metadata"),
      formData,
      {
        headers: {
          ...getAuthHeaders(),
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response;
  } catch (error) {
    console.error("上传元数据文件失败", error);
    throw error;
  }
};

/**
 * 仅保存元数据（不上传PDF文件）
 * @param metadataList 元数据列表
 * @param folderId 目标文件夹ID
 * @returns Promise
 */
export const saveMetadataOnly = async (
  metadataList: Array<{ fileName: string; metadata: any }>,
  folderId: string | number
) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟保存元数据:", { metadataList, folderId });

    // 模拟处理延迟
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // 返回模拟成功响应
    return Promise.resolve({
      data: {
        code: 0,
        message: `成功保存 ${metadataList.length} 条元数据记录`,
        data: {
          docIds: Array.from(
            { length: metadataList.length },
            (_, i) => i + 1000
          ),
          fileNames: metadataList.map((item) => item.fileName),
        },
      },
    });
  }

  // 生产环境使用实际API
  try {
    const response = await axios.post(
      buildApiPath("/upload/metadata-only"),
      {
        metadataList,
        folderId,
        userId: getCurrentUserId(),
      },
      {
        headers: getAuthHeaders(),
      }
    );

    // 保存元数据后触发更新事件
    notifyFolderStructureChanged();

    return response;
  } catch (error) {
    console.error("保存元数据失败", error);
    throw error;
  }
};
