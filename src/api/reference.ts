import axios from "axios";
import {
  API_BASE_URL,
  buildApiPath,
  DEFAULT_REQUEST_CONFIG,
  getAuthHeaders,
} from "./config";
import { getCurrentUserId } from "./load";

/**
 * 生成指定文件夹下的文献参考列表
 * @param folderId 文件夹ID
 * @param format 参考文献格式 ('gbt7714' 或 'apa')
 * @returns 格式化的参考文献列表
 */
export const generateReferenceList = async (
  folderId: string | number,
  format = "gbt7714"
) => {
  try {
    const response = await axios.get(buildApiPath(`/references/generate`), {
      headers: getAuthHeaders(),
      params: {
        folderId,
        format,
        userId: getCurrentUserId(),
      },
    });
    return response;
  } catch (error) {
    console.error("生成参考文献列表失败", error);
    throw error;
  }
};

/**
 * 获取支持的参考文献格式
 * @returns 支持的参考文献格式列表
 */
export const getSupportedReferenceFormats = async () => {
  try {
    const response = await axios.get(buildApiPath(`/references/formats`), {
      headers: getAuthHeaders(),
    });
    return response;
  } catch (error) {
    console.error("获取支持的参考文献格式失败", error);
    throw error;
  }
};
