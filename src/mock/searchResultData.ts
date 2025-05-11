// 搜索结果模拟数据

// 定义返回值的接口类型
interface SearchResultItem {
  id: string | number;
  name: string;
  type: "folder" | "document"; // 限制为这两种类型
  matchField?: string;
  path?: string;
  highlight?: string;
}

export const searchResultData: Record<string, SearchResultItem[]> = {
  // 关键词为键，搜索结果为值
  机器学习: [
    {
      id: 211101,
      name: "机器学习算法综述.pdf",
      type: "document", // 确保类型为 "document"
      matchField: "title",
      path: "我的文献库/计算机科学/人工智能/机器学习",
      highlight: "本文对当前主流的<em>机器学习</em>算法进行了全面的综述...",
    },
    {
      id: 2111,
      name: "机器学习",
      type: "folder", // 确保类型为 "folder"
      matchField: "name",
      path: "我的文献库/计算机科学/人工智能",
      highlight: "<em>机器学习</em>相关文献",
    },
    {
      id: 211102,
      name: "支持向量机原理与应用.pdf",
      type: "document",
      matchField: "tags",
      path: "我的文献库/计算机科学/人工智能/机器学习",
      highlight: "标签包含：<em>机器学习</em>",
    },
  ],
  人工智能: [
    {
      id: 21101,
      name: "人工智能：现代方法.pdf",
      type: "document",
      matchField: "title",
      path: "我的文献库/计算机科学/人工智能",
      highlight: "<em>人工智能</em>：现代方法",
    },
    {
      id: 211,
      name: "人工智能",
      type: "folder",
      matchField: "name",
      path: "我的文献库/计算机科学",
      highlight: "<em>人工智能</em>相关文献",
    },
  ],
  算法: [
    {
      id: 211101,
      name: "机器学习算法综述.pdf",
      type: "document",
      matchField: "title",
      path: "我的文献库/计算机科学/人工智能/机器学习",
      highlight: "机器学习<em>算法</em>综述",
    },
    {
      id: 211102,
      name: "支持向量机原理与应用.pdf",
      type: "document",
      matchField: "abstract",
      path: "我的文献库/计算机科学/人工智能/机器学习",
      highlight: "支持向量机(SVM)是一种常用的分类<em>算法</em>...",
    },
  ],
};

// 模拟搜索函数
export const searchLibrary = (
  keyword: string,
  advancedParams: Record<string, any> = {}
): SearchResultItem[] => {
  // 简单返回预设的搜索结果
  return searchResultData[keyword as keyof typeof searchResultData] || [];
};
