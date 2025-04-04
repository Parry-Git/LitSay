import { myAxios } from "@/request";

/**
 * 获取特定文件夹下包含的文件夹和具体文献
 * @param folderId 文件夹ID，如果是根目录可以传递特定值如"root"
 */
export const getFolderContents = async (folderId: string | number) => {
  return await myAxios.request({
    url: `/api/folder/${folderId}/contents`,
    method: "GET",
  });
};

/**
 * 新建文件夹
 * @param params 包含父文件夹ID和新文件夹名称
 */
export const createFolder = async (params: {
  parentId: string | number;
  name: string;
}) => {
  return await myAxios.request({
    url: "/api/folder/create",
    method: "POST",
    data: params,
  });
};

/**
 * 删除文件夹
 * @param folderId 要删除的文件夹ID
 */
export const deleteFolder = async (folderId: string | number) => {
  return await myAxios.request({
    url: `/api/folder/${folderId}`,
    method: "DELETE",
  });
};

/**
 * 重命名文件夹
 * @param params 包含文件夹ID和新名称
 */
export const renameFolder = async (params: {
  folderId: string | number;
  newName: string;
}) => {
  return await myAxios.request({
    url: "/api/folder/rename",
    method: "PUT",
    data: params,
  });
};

/**
 * 新建文献
 * @param params 包含文献相关信息
 */
export const createDocument = async (params: {
  folderId: string | number;
  title: string;
  authors?: string[];
  abstract?: string;
  publishDate?: string;
  fileUrl?: string;
  tags?: string[];
  // 其他可能的元数据
}) => {
  return await myAxios.request({
    url: "/api/document/create",
    method: "POST",
    data: params,
  });
};

/**
 * 修改文献元数据信息
 * @param documentId 文献ID
 * @param params 需要更新的字段
 */
export const updateDocumentMetadata = async (
  documentId: string | number,
  params: {
    title?: string;
    authors?: string[];
    abstract?: string;
    publishDate?: string;
    tags?: string[];
    // 其他可能的元数据
  }
) => {
  return await myAxios.request({
    url: `/api/document/${documentId}/metadata`,
    method: "PUT",
    data: params,
  });
};

/**
 * 删除文献
 * @param documentId 要删除的文献ID
 */
export const deleteDocument = async (documentId: string | number) => {
  return await myAxios.request({
    url: `/api/document/${documentId}`,
    method: "DELETE",
  });
};

/**
 * 上传文献文件
 * @param folderId 目标文件夹ID
 * @param formData 包含文件和元数据的表单数据
 */
export const uploadDocumentFile = async (
  folderId: string | number,
  formData: FormData
) => {
  return await myAxios.request({
    url: `/api/document/upload?folderId=${folderId}`,
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

/**
 * 批量上传PDF文件
 * @param files 要上传的PDF文件数组
 * @param folderId 可选的目标文件夹ID
 */
export const uploadPdfFiles = async (
  files: File[],
  folderId?: string | number
) => {
  const formData = new FormData();

  // 添加所有PDF文件到表单
  files.forEach((file) => {
    formData.append("pdfs", file);
  });

  // 如果提供了文件夹ID，添加到表单
  if (folderId) {
    formData.append("folderId", folderId.toString());
  }

  // 使用原始 axios 以便与后端接口保持兼容
  return await myAxios.request({
    url: `/api/upload-files`, // 保持原始URL
    method: "POST",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

/**
 * 下载文献文件
 * @param documentId 文献ID
 */
export const downloadDocument = async (documentId: string | number) => {
  return await myAxios.request({
    url: `/api/document/${documentId}/download`,
    method: "GET",
    responseType: "blob",
  });
};

/**
 * 全局搜索文档和文件夹
 * @param keyword 搜索关键词
 */
export const searchLibrary = async (keyword: string) => {
  return await myAxios.request({
    url: `/api/search`,
    method: "GET",
    params: { keyword },
  });
};
