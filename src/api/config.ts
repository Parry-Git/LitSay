const DEV_API_BASE_URL = "http://localhost:5000";
const PROD_API_BASE_URL = "";

export const API_BASE_URL =
  process.env.NODE_ENV === "production" ? PROD_API_BASE_URL : DEV_API_BASE_URL;

export const buildApiPath = (path: string): string => {
  // 确保path总是以/api开头
  if (!path.startsWith("/api")) {
    path = `/api${path.startsWith("/") ? path : `/${path}`}`;
  }
  return `${API_BASE_URL}${path}`;
};

// 默认的请求配置
export const DEFAULT_REQUEST_CONFIG = {
  headers: {
    "Content-Type": "application/json",
  },
  // 如果需要携带cookie，可以设置withCredentials为true，感觉后续应该不需要写cookie
  // withCredentials: true,
};

/**
 * 获取包含认证信息的请求头
 */
export const getAuthHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    Authorization: token ? `Bearer ${token}` : "",
    "Content-Type": "application/json",
  };
};

/**
 * 获取简单请求的认证参数（适用于避免OPTIONS预检请求的场景）
 */
export const getAuthParams = () => {
  const token = localStorage.getItem("token");
  return {
    token: token || "",
  };
};
