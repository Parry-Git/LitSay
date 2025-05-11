import { MockData } from "./types";

// 模拟数据
const mockData: MockData = {
  essays: [
    {
      id: 1,
      title: "Javascript基础知识",
      content: "Javascript是一种轻量级的脚本语言，用于网页交互...",
      author: "张三",
      publishDate: "2023-01-15",
      tagIds: [1, 3],
    },
    {
      id: 2,
      title: "React状态管理",
      content: "React中的状态管理是前端开发中的重要概念...",
      author: "李四",
      publishDate: "2023-02-20",
      tagIds: [1, 2],
    },
    {
      id: 3,
      title: "Vue组件通信",
      content: "Vue组件之间的通信方式有多种，包括props、事件等...",
      author: "王五",
      publishDate: "2023-03-10",
      tagIds: [1, 4],
    },
    {
      id: 4,
      title: "TypeScript入门指南",
      content: "TypeScript是JavaScript的超集，它添加了静态类型系统...",
      author: "赵六",
      publishDate: "2023-04-05",
      tagIds: [1, 5],
    },
  ],
  tags: [
    { id: 1, name: "前端", color: "#3498db" },
    { id: 2, name: "React", color: "#61dafb" },
    { id: 3, name: "JavaScript", color: "#f1e05a" },
    { id: 4, name: "Vue", color: "#42b883" },
    { id: 5, name: "TypeScript", color: "#007acc" },
  ],
};

// 模拟异步获取数据
export const getData = (): Promise<MockData> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(mockData);
    }, 300);
  });
};
