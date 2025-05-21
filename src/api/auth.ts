import axios from "axios";
import {
  API_BASE_URL,
  buildApiPath,
  DEFAULT_REQUEST_CONFIG,
  getAuthHeaders,
} from "./config";

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 * @returns Promise 登录结果
 */
export const login = async (username: string, password: string) => {
  try {
    const response = await axios.post(
      buildApiPath("/auth/login"),
      { username, password },
      { headers: DEFAULT_REQUEST_CONFIG.headers }
    );

    const responseData = response.data;
    console.log("登录API响应:", responseData);

    let token, user;

    if (responseData.access_token) {
      token = responseData.access_token;
      user = responseData.user;
    } else if (responseData.data && responseData.data.access_token) {
      token = responseData.data.access_token;
      user = responseData.data.user;
    }

    if (token) {
      localStorage.setItem("token", token);
      console.log("API - Token已存储:", token);
    }

    if (user) {
      localStorage.setItem("userInfo", JSON.stringify(user));
      console.log("API - 用户信息已存储:", user);
    }

    return responseData;
  } catch (error: any) {
    console.error("登录失败:", error.response?.data || error.message);
    throw new Error(
      error.response?.data?.message || "登录失败，请检查用户名和密码"
    );
  }
};

/**
 * 用户注册
 * @param username 用户名
 * @param password 密码
 * @returns Promise 注册结果
 */
export const register = async (username: string, password: string) => {
  try {
    const response = await axios.post(
      buildApiPath("/auth/register"),
      { username, password },
      { headers: DEFAULT_REQUEST_CONFIG.headers }
    );
    return response.data;
  } catch (error: any) {
    console.error(
      "Registration failed:",
      error.response?.data || error.message
    );
    throw new Error(error.response?.data?.message || "注册失败，请稍后再试");
  }
};

/**
 * 用户登出
 * @returns Promise
 */
export const logout = async () => {
  try {
    localStorage.removeItem("token");
    localStorage.removeItem("userInfo");

    return { success: true };
  } catch (error: any) {
    console.error("Logout failed:", error);
    // 即使API调用失败，也清除本地存储
    localStorage.removeItem("token");
    localStorage.removeItem("userInfo");
    throw error;
  }
};

/**
 * 获取用户个人资料
 * @returns Promise 用户资料
 */
export const getUserProfile = async () => {
  try {
    const response = await axios.get(buildApiPath("/auth/profile"), {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error: any) {
    console.error(
      "Failed to get user profile:",
      error.response?.data || error.message
    );
    throw new Error(error.response?.data?.message || "获取用户资料失败");
  }
};
