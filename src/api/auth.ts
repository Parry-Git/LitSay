import { myAxios } from "@/request";

/**
 * 用户登录
 * @param username 用户名
 * @param password 密码
 * @returns Promise 包含用户信息和token
 */
export const login = async (username: string, password: string) => {
  try {
    const response = await myAxios.post("/user/login", {
      username,
      password,
    });

    // 保存token到localStorage
    if (response.data.data.token) {
      localStorage.setItem("token", response.data.data.token);

      // 保存用户信息
      if (response.data.data.user) {
        localStorage.setItem(
          "userInfo",
          JSON.stringify(response.data.data.user)
        );
      }
    }

    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(
        error.response.data.message || "登录失败，请检查用户名和密码"
      );
    }
    throw error;
  }
};

/**
 * 用户注册
 * @param username 用户名
 * @param password 密码
 * @returns Promise 包含注册结果
 */
export const register = async (username: string, password: string) => {
  try {
    const response = await myAxios.post("/user/register", {
      username,
      password,
    });

    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(
        error.response.data.message || "注册失败，用户名可能已存在"
      );
    }
    throw error;
  }
};

/**
 * 用户登出
 * @returns Promise 包含登出结果
 */
export const logout = async () => {
  try {
    // 检查是否为模拟的管理员账号
    const userInfo = localStorage.getItem("userInfo");
    const token = localStorage.getItem("token");

    if (userInfo && token === "admin-mock-token") {
      // 如果是模拟的管理员账户，直接清除本地存储
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
      return { success: true, message: "管理员退出成功" };
    }

    // 否则调用实际的登出接口
    const response = await myAxios.post("/user/logout");

    // 清除本地存储的token和用户信息
    localStorage.removeItem("token");
    localStorage.removeItem("userInfo");

    return response.data;
  } catch (error: any) {
    // 即使API调用失败，也尝试清除本地存储
    localStorage.removeItem("token");
    localStorage.removeItem("userInfo");

    throw error;
  }
};

/**
 * 获取当前登录用户信息
 * @returns Promise 包含用户信息
 */
export const getCurrentUser = async () => {
  // 检查是否为模拟的管理员账号
  const userInfo = localStorage.getItem("userInfo");
  const token = localStorage.getItem("token");

  if (userInfo && token === "admin-mock-token") {
    // 如果是模拟的管理员账户，直接返回用户信息
    return {
      success: true,
      data: JSON.parse(userInfo),
      message: "获取管理员信息成功",
    };
  }

  // eslint-disable-next-line no-useless-catch
  try {
    const response = await myAxios.get("/user/current");
    return response.data;
  } catch (error: any) {
    throw error;
  }
};
