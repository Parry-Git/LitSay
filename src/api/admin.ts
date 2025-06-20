import axios from "axios";
import { API_BASE_URL, buildApiPath, getAuthHeaders } from "./config";

/**
 * 获取所有用户列表
 * @returns Promise 包含所有用户的列表
 */
export const getAllUsers = async () => {
  try {
    const response = await axios.get(buildApiPath("/user/all"), {
      headers: getAuthHeaders(),
    });
    return response;
  } catch (error) {
    console.error("获取用户列表失败", error);
    throw error;
  }
};

/**
 * 更新用户角色
 * @param userId 用户ID
 * @param role 新角色 ('admin' 或 'user')
 * @returns Promise 包含更新结果
 */
export const updateUserRole = async (userId: number, role: string) => {
  try {
    const response = await axios.put(
      buildApiPath(`/user/${userId}/role`),
      { role },
      { headers: getAuthHeaders() }
    );
    return response;
  } catch (error) {
    console.error("更新用户角色失败", error);
    throw error;
  }
};

/**
 * 删除用户账号
 * @param userId 用户ID
 * @returns Promise 包含删除结果
 */
export const deleteUserAccount = async (userId: number) => {
  try {
    const response = await axios.delete(buildApiPath(`/user/${userId}`), {
      headers: getAuthHeaders(),
    });
    return response;
  } catch (error) {
    console.error("删除用户失败", error);
    throw error;
  }
};
