import { myAxios } from "@/request";

// 导入所有的模拟数据
import {
  folderData,
  getFolderContents as mockGetFolderContents,
  documentData,
  getDocumentDetails as mockGetDocumentDetails,
  searchResultData,
  searchLibrary as mockSearchLibrary,
  userStatsData,
} from "@/mock";

// 判断是否为开发环境
const isDevelopment = process.env.NODE_ENV === "development";

/**
 * 获取用户ID
 * @returns 当前登录用户的ID或null
 */
export const getCurrentUserId = (): string | null => {
  const userInfo = localStorage.getItem("userInfo");
  if (userInfo) {
    try {
      const parsedInfo = JSON.parse(userInfo);
      return parsedInfo.id || null;
    } catch (e) {
      console.error("解析用户信息失败", e);
      return null;
    }
  }
  return null;
};

/**
 * 获取文件夹内容
 * @param folderId 文件夹ID
 * @returns Promise 包含文件夹内容
 */
export const getFolderContents = async (folderId: string | number) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 使用模拟数据获取文件夹内容:", folderId);
    const mockData = mockGetFolderContents(folderId);
    // 模拟 API 返回结构
    return Promise.resolve({
      data: {
        code: 0,
        message: "获取成功",
        data: mockData,
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.get(`/folder/${folderId}`, {
      params: { userId },
    });
  } catch (error) {
    console.error("获取文件夹内容失败", error);
    throw error;
  }
};

/**
 * 创建文件夹
 * @param params 创建参数，包括父文件夹ID和名称
 * @returns Promise 包含创建结果
 */
export const createFolder = async (params: {
  parentId: string | number;
  name: string;
}) => {
  // 如果是开发环境，模拟创建文件夹
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟创建文件夹:", params);
    // 返回一个模拟的成功响应
    return Promise.resolve({
      data: {
        code: 0,
        message: "创建成功",
        data: {
          id: Date.now(), // 使用时间戳作为临时 ID
          name: params.name,
          type: "folder",
          createTime: new Date().toISOString().slice(0, 10),
          parentId: params.parentId,
        },
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.post("/folder/create", {
      ...params,
      userId,
    });
  } catch (error) {
    console.error("创建文件夹失败", error);
    throw error;
  }
};

/**
 * 重命名文件夹
 * @param params 重命名参数，包括文件夹ID和新名称
 * @returns Promise 包含重命名结果
 */
export const renameFolder = async (params: {
  folderId: string | number;
  newName: string;
}) => {
  // 如果是开发环境，模拟重命名文件夹
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟重命名文件夹:", params);
    return Promise.resolve({
      data: {
        code: 0,
        message: "重命名成功",
        data: {
          id: params.folderId,
          name: params.newName,
        },
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.put("/folder/rename", {
      ...params,
      userId,
    });
  } catch (error) {
    console.error("重命名文件夹失败", error);
    throw error;
  }
};

/**
 * 删除文件夹
 * @param folderId 文件夹ID
 * @returns Promise 包含删除结果
 */
export const deleteFolder = async (folderId: string | number) => {
  // 如果是开发环境，模拟删除文件夹
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟删除文件夹:", folderId);
    return Promise.resolve({
      data: {
        code: 0,
        message: "删除成功",
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.delete(`/folder/${folderId}`, {
      params: { userId },
    });
  } catch (error) {
    console.error("删除文件夹失败", error);
    throw error;
  }
};

/**
 * 上传PDF文件
 * @param files 文件列表
 * @param folderId 目标文件夹ID
 * @returns Promise 包含上传结果
 */
export const uploadPdfFiles = async (files: File[], folderId?: string) => {
  // 如果是开发环境，模拟上传文件
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟上传文件:", { files, folderId });
    // 创建模拟的文件名列表
    const uploadedFiles = files.map((file) => file.name);
    return Promise.resolve({
      data: {
        code: 0,
        message: "上传成功",
        data: {
          files: uploadedFiles,
          folderId,
        },
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  if (folderId) {
    formData.append("folderId", folderId);
  }

  if (userId) {
    formData.append("userId", userId);
  }

  try {
    return await myAxios.post("/upload/pdf", formData);
  } catch (error) {
    console.error("上传PDF文件失败", error);
    throw error;
  }
};

/**
 * 搜索文库
 * @param query 搜索关键词
 * @param advancedParams 高级搜索参数
 * @returns Promise 包含搜索结果
 */
export const searchLibrary = async (query: string, advancedParams?: any) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 使用模拟数据搜索:", query, advancedParams);

    // 获取模拟搜索结果
    const results = searchResultData[query] || [];

    // 如果有高级搜索参数，应用简单的过滤
    if (advancedParams && Object.keys(advancedParams).length > 0) {
      // 这里可以添加基于 advancedParams 的过滤逻辑
      console.log("[Dev Mode] 应用高级搜索参数:", advancedParams);
    }

    return Promise.resolve({
      data: {
        code: 0,
        message: "搜索成功",
        data: {
          results,
        },
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.get("/search", {
      params: {
        q: query,
        userId,
        ...advancedParams,
      },
    });
  } catch (error) {
    console.error("搜索失败", error);
    throw error;
  }
};

/**
 * 获取文件夹结构
 * @returns Promise 包含文件夹树结构
 */
export const getFolderStructure = async () => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 使用模拟数据获取文件夹结构");
    return Promise.resolve({
      data: {
        code: 0,
        message: "获取成功",
        data: folderData,
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.get("/folder/tree", {
      params: { userId },
    });
  } catch (error) {
    console.error("获取文件夹结构失败", error);
    throw error;
  }
};

/**
 * 获取文档详情
 * @param documentId 文档ID
 * @returns Promise 包含文档详情
 */
export const getDocumentDetails = async (documentId: string | number) => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 使用模拟数据获取文档详情:", documentId);
    const mockDoc = mockGetDocumentDetails(documentId);
    return Promise.resolve({
      data: {
        code: 0,
        message: "获取成功",
        data: mockDoc,
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.get(`/document/${documentId}`, {
      params: { userId },
    });
  } catch (error) {
    console.error("获取文档详情失败", error);
    throw error;
  }
};

/**
 * 删除文档
 * @param documentId 文档ID
 * @returns Promise 包含删除结果
 */
export const deleteDocument = async (documentId: string | number) => {
  // 如果是开发环境，模拟删除文档
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟删除文档:", documentId);
    return Promise.resolve({
      data: {
        code: 0,
        message: "删除成功",
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.delete(`/document/${documentId}`, {
      params: { userId },
    });
  } catch (error) {
    console.error("删除文档失败", error);
    throw error;
  }
};

/**
 * 更新文档元数据
 * @param documentId 文档ID
 * @param metadata 元数据对象
 * @returns Promise 包含更新结果
 */
export const updateDocumentMetadata = async (
  documentId: string | number,
  metadata: any
) => {
  // 如果是开发环境，模拟更新文档元数据
  if (isDevelopment) {
    console.log("[Dev Mode] 模拟更新文档元数据:", documentId, metadata);
    return Promise.resolve({
      data: {
        code: 0,
        message: "更新成功",
        data: {
          id: documentId,
          ...metadata,
        },
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.put(`/document/${documentId}/metadata`, {
      ...metadata,
      userId,
    });
  } catch (error) {
    console.error("更新文档元数据失败", error);
    throw error;
  }
};

/**
 * 获取用户统计数据
 * @returns Promise 包含用户统计信息
 */
export const getUserStats = async () => {
  // 如果是开发环境，使用模拟数据
  if (isDevelopment) {
    console.log("[Dev Mode] 使用模拟数据获取用户统计");
    return Promise.resolve({
      data: {
        code: 0,
        message: "获取成功",
        data: userStatsData,
      },
    });
  }

  // 生产环境使用实际 API
  const userId = getCurrentUserId();
  try {
    return await myAxios.get(`/user/stats`, {
      params: { userId },
    });
  } catch (error) {
    console.error("获取用户统计数据失败", error);
    throw error;
  }
};
