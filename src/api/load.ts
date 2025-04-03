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
