import axios from "axios";
import { API_BASE_URL, buildApiPath, getAuthHeaders } from "./config";

/**
 * 获取用户统计数据概览
 * @returns Promise 包含统计概览数据
 */
export const getStatsOverview = async () => {
  try {
    console.log("正在请求统计概览数据...");
    const response = await axios.get(buildApiPath("/stats/overview"), {
      headers: getAuthHeaders(),
    });
    console.log("获取统计概览数据成功:", response.data);
    return response.data;
  } catch (error) {
    console.error("获取统计概览数据失败", error);
    throw error;
  }
};

/**
 * 获取关键词Top5统计
 * @returns Promise 包含关键词统计数据
 */
export const getKeywordsTop = async () => {
  try {
    console.log("正在请求关键词TOP5数据...");
    const response = await axios.get(buildApiPath("/stats/keywords/top"), {
      headers: getAuthHeaders(),
      params: { limit: 5 },
    });
    console.log("获取关键词TOP5数据成功:", response.data);
    return response.data;
  } catch (error) {
    console.error("获取关键词统计数据失败", error);
    throw error;
  }
};

/**
 * 获取作者星级Top5统计
 * @returns Promise 包含作者星级统计数据
 */
export const getAuthorsStarsTop = async () => {
  try {
    console.log("正在请求作者星级TOP5数据...");
    const response = await axios.get(buildApiPath("/stats/authors/stars"), {
      headers: getAuthHeaders(),
      params: { limit: 5 },
    });
    console.log("获取作者星级TOP5数据成功:", response.data);
    return response.data;
  } catch (error) {
    console.error("获取作者星级统计数据失败", error);
    throw error;
  }
};

/**
 * 模拟数据：用于开发环境测试
 */
export const getMockStatsData = () => {
  // 基本统计数据 - 使用与后端相同的结构
  const overview = {
    documentsCount: 7,
    foldersCount: 4,
    authorsCount: 9,
  };

  // 关键词统计数据 - 使用与后端相同的结构
  const keywordsTop = [
    { keyword: "深度学习", count: 4 },
    { keyword: "自然语言处理", count: 4 },
    { keyword: "人工智能", count: 2 },
    { keyword: "机器学习", count: 2 },
    { keyword: "Transformer", count: 2 },
  ];

  // 作者星级统计数据 - 使用与后端相同的结构
  const authorsStarsTop = [
    { author: "Steffen Nestler", stars: null },
    { author: "Yaowu Liu", stars: null },
    { author: "Jun Xie", stars: null },
    { author: "张三", stars: null },
    { author: "李四", stars: null },
  ];

  return {
    overview,
    keywordsTop,
    authorsStarsTop,
  };
};
