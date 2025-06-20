import axios from "axios";
import {
  API_BASE_URL,
  buildApiPath,
  DEFAULT_REQUEST_CONFIG,
  getAuthHeaders,
} from "./config";
import { notifyFolderStructureChanged } from "@/services/EventService";

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

/**
 * 获取用户ID
 * @returns 当前登录用户的ID或null
 */
export const getCurrentUserId = (): string | null => {
  const userInfo = localStorage.getItem("userInfo");
  // console.log("获取到的数据：", userInfo);
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
  try {
    const response = await axios.get(buildApiPath(`/folder/${folderId}`), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });
    return response;
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
  const userId = getCurrentUserId();
  try {
    const response = await axios.post(
      buildApiPath("/folder/create"),
      { ...params, userId },
      { headers: getAuthHeaders() }
    );

    // 创建文件夹后触发更新事件
    notifyFolderStructureChanged();

    return response;
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
  try {
    const response = await axios.put(
      buildApiPath("/folder/rename"),
      { ...params, userId: getCurrentUserId() },
      { headers: getAuthHeaders() }
    );

    // 重命名后触发更新事件
    notifyFolderStructureChanged();

    return response;
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
  try {
    const response = await axios.delete(buildApiPath(`/folder/${folderId}`), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });

    // 删除文件夹后触发更新事件
    notifyFolderStructureChanged();

    return response;
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
    return await axios.post("/upload/pdf", formData);
  } catch (error) {
    console.error("上传PDF文件失败", error);
    throw error;
  }
};

/**
 * 获取文件夹结构
 * @returns Promise 包含文件夹树结构
 */
export const getFolderStructure = async () => {
  try {
    const response = await axios.get(buildApiPath("/folder/tree"), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });
    return response;
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
  try {
    const response = await axios.get(buildApiPath(`/document/${documentId}`), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });
    return response;
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
  try {
    const response = await axios.delete(
      buildApiPath(`/document/${documentId}`),
      {
        headers: getAuthHeaders(),
        params: { userId: getCurrentUserId() },
      }
    );
    return response;
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
  try {
    const response = await axios.put(
      buildApiPath(`/document/${documentId}/metadata`),
      { ...metadata, userId: getCurrentUserId() },
      { headers: getAuthHeaders() }
    );
    return response;
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
  try {
    const response = await axios.get(buildApiPath(`/user/stats`), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });
    return response;
  } catch (error) {
    console.error("获取用户统计数据失败", error);
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
  try {
    // 修改搜索API调用，使用URL参数传递token而不是Authorization头
    const token = localStorage.getItem("token");
    const params = {
      q: query,
      userId: getCurrentUserId(),
      token: token ? token : "", // 通过URL参数传递token
      ...advancedParams,
    };

    // console.log("搜索参数:", params);

    // 发起符合"简单请求"条件的请求
    const response = await axios.get(buildApiPath("/search"), {
      params,
      // 移除可能触发预检请求的头部
      headers: {
        Accept: "application/json", // 这是"简单请求"允许的头部
        "Content-Type": "application/json", // 这是"简单请求"允许的头部之一
      },
    });
    return response;
  } catch (error) {
    console.error("搜索失败", error);
    throw error;
  }
};

/**
 * 获取作者详情
 * @param authorId 作者ID
 * @returns Promise 包含作者详情
 */
export const getAuthorDetails = async (authorId: string | number) => {
  try {
    const response = await axios.get(buildApiPath(`/author/${authorId}`), {
      headers: getAuthHeaders(),
      params: { userId: getCurrentUserId() },
    });
    return response;
  } catch (error) {
    console.error("获取作者详情失败", error);
    throw error;
  }
};

/**
 * 获取机构详情
 * @param institutionId 机构ID
 * @returns Promise 包含机构详情
 */
export const getInstitutionDetails = async (institutionId: string | number) => {
  try {
    const response = await axios.get(
      buildApiPath(`/institution/${institutionId}`),
      {
        headers: getAuthHeaders(),
        params: { userId: getCurrentUserId() },
      }
    );
    return response;
  } catch (error) {
    console.error("获取机构详情失败", error);
    throw error;
  }
};

/**
 * 获取容器（期刊/会议）详情
 * @param containerId 容器ID
 * @returns Promise 包含容器详情及相关文献
 */
export const getContainerDetails = async (containerId: string | number) => {
  try {
    const response = await axios.get(
      buildApiPath(`/container/${containerId}`),
      {
        headers: getAuthHeaders(),
        params: { userId: getCurrentUserId() },
      }
    );
    return response;
  } catch (error) {
    console.error("获取容器详情失败", error);
    throw error;
  }
};
