import axios from "axios";
import {
  API_BASE_URL,
  buildApiPath,
  DEFAULT_REQUEST_CONFIG,
  getAuthHeaders,
} from "./config";
import { getCurrentUserId } from "@/api/load";
import { notifyFolderStructureChanged } from "@/services/EventService";

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
  const formData = new FormData();
  formData.append("file", file);
  // console.log("====上传的文件formData格式=====:", formData);

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
 * 仅保存元数据（不上传PDF文件）
 * @param metadataList 元数据列表
 * @param folderId 目标文件夹ID
 * @returns Promise
 */
export const saveMetadataOnly = async (
  metadataList: Array<{ fileName: string; metadata: any }>,
  folderId: string | number
) => {
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

/**
 * 解析元数据文件 (CSV, JSON) - 本地解析
 * @param file 元数据文件
 * @returns Promise 包含解析后的元数据
 */
export const parseMetadataFile = async (file: File): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    // 判断文件类型
    if (file.name.endsWith(".json")) {
      // JSON文件解析
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const jsonData = JSON.parse(e.target?.result as string);
          // 确保数据是数组格式
          const metadataArray = Array.isArray(jsonData) ? jsonData : [jsonData];
          resolve(metadataArray);
        } catch (error) {
          reject(new Error(`JSON解析错误: ${error}`));
        }
      };
      reader.onerror = () => reject(new Error("读取JSON文件失败"));
      reader.readAsText(file);
    } else if (file.name.endsWith(".csv")) {
      // CSV文件解析
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const csvText = e.target?.result as string;
          const metadataArray = parseCSV(csvText);
          resolve(metadataArray);
        } catch (error) {
          reject(new Error(`CSV解析错误: ${error}`));
        }
      };
      reader.onerror = () => reject(new Error("读取CSV文件失败"));
      reader.readAsText(file);
    } else {
      reject(new Error("不支持的文件格式，仅支持JSON和CSV"));
    }
  });
};

/**
 * CSV解析函数
 * @param csvText CSV文本内容
 * @returns 解析后的对象数组
 */
const parseCSV = (csvText: string): any[] => {
  // 分割行
  const lines = csvText.split(/\r\n|\n/);
  if (lines.length < 2) throw new Error("CSV文件格式错误或为空");

  // 提取表头
  const headers = lines[0].split(",").map((header) => header.trim());

  // 解析每行数据
  const results: any[] = [];
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue; // 跳过空行

    const obj: any = {};
    // 使用 CSV 解析逻辑处理引号内的逗号
    const currentLine = parseCSVLine(lines[i]);

    // 确保有足够的列
    if (currentLine.length < headers.length) continue;

    // 映射列到字段
    for (let j = 0; j < headers.length; j++) {
      const value = currentLine[j];
      const header = headers[j];

      // 列表类型字段根据分号分割
      if (
        [
          "authors",
          "sequence",
          "email",
          "institution_location",
          "institutions",
          "keywords",
        ].includes(header)
      ) {
        obj[header] = value ? value.split(";").map((item) => item.trim()) : [];
      }
      // 空字符串的字段设置为 null
      else if (value === "" || value === "null") {
        obj[header] = null;
      }
      // 其他字段直接赋值
      else {
        obj[header] = value;
      }
    }

    // 处理期刊和会议字段的互斥性
    if (obj.journal && obj.journal !== null && obj.journal !== "") {
      // 如果有期刊信息，清空会议相关字段
      obj.conference = null;
      obj.conference_time = null;
      obj.conference_location = null;
    } else if (
      obj.conference &&
      obj.conference !== null &&
      obj.conference !== ""
    ) {
      // 如果有会议信息，清空期刊相关字段
      obj.journal = null;
      obj.journal_issue = null;
    }

    // 确保所有数组字段长度一致（以 authors 数组长度为基准）
    if (obj.authors && obj.authors.length > 0) {
      const arrayFields = [
        "sequence",
        "email",
        "institution_location",
        "institutions",
      ];
      const authorsLength = obj.authors.length;

      arrayFields.forEach((field) => {
        if (obj[field]) {
          // 如果数组长度不足，补充空字符串
          while (obj[field].length < authorsLength) {
            obj[field].push("");
          }
          // 如果数组长度超出，截断
          if (obj[field].length > authorsLength) {
            obj[field] = obj[field].slice(0, authorsLength);
          }
        } else {
          // 如果字段不存在，创建相应长度的空数组
          obj[field] = Array(authorsLength).fill("");
        }
      });
    }

    results.push(obj);
  }
  // console.log("解析后的CSV数据:", results);

  return results;
};

// 辅助函数：解析 CSV 行，正确处理引号内的逗号
const parseCSVLine = (line: string): string[] => {
  const result: string[] = [];
  let currentValue = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"' && (i === 0 || line[i - 1] !== "\\")) {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      result.push(currentValue.trim());
      currentValue = "";
    } else {
      currentValue += char;
    }
  }

  // 添加最后一个值
  result.push(currentValue.trim());

  // 清理值中的引号
  return result.map((val) => {
    if (val.startsWith('"') && val.endsWith('"')) {
      return val.substring(1, val.length - 1);
    }
    return val;
  });
};

/**
 * 批量保存元数据 (不包含文件上传)
 * @param metadataList 元数据列表
 * @param folderId 目标文件夹ID
 * @returns Promise 包含操作结果
 */
export const saveBatchMetadata = async (
  metadataList: any[],
  folderId: string | number
) => {
  // 生产环境使用实际API
  try {
    const response = await axios.post(
      buildApiPath("/upload/metadata"),
      {
        metadataList,
        folderId,
        userId: getCurrentUserId(),
      },
      {
        headers: getAuthHeaders(),
      }
    );
    return response;
  } catch (error) {
    console.error("批量保存元数据失败", error);
    throw error;
  }
};
