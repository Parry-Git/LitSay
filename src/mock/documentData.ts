// 文献详细数据
export const documentData = {
  // 文献ID为键
  "211101": {
    id: 211101,
    title: "机器学习算法综述",
    authors: ["李明", "张华"],
    publishDate: "2022-06-15",
    abstract:
      "本文对当前主流的机器学习算法进行了全面的综述，包括监督学习、无监督学习和强化学习三大类算法。文章分析了各类算法的原理、适用场景和局限性，并对未来发展趋势进行了展望。",
    tags: ["机器学习", "算法", "综述"],
    fileUrl: "https://example.com/papers/211101.pdf",
    fileType: "PDF",
    fileSize: "3.5 MB",
    uploadTime: "2023-09-10",
    folderId: 2111,
    path: "我的文献库/计算机科学/人工智能/机器学习",
  },
  "211102": {
    id: 211102,
    title: "支持向量机原理与应用",
    authors: ["王刚"],
    publishDate: "2021-11-20",
    abstract:
      "支持向量机(SVM)是一种常用的分类算法，本文详细介绍了SVM的数学原理和核函数选择方法，并通过实际案例展示了SVM在图像识别、文本分类等领域的应用效果。",
    tags: ["支持向量机", "分类算法", "模式识别"],
    fileUrl: "https://example.com/papers/211102.pdf",
    fileType: "PDF",
    fileSize: "2.1 MB",
    uploadTime: "2023-09-12",
    folderId: 2111,
    path: "我的文献库/计算机科学/人工智能/机器学习",
  },
  "21101": {
    id: 21101,
    title: "人工智能：现代方法",
    authors: ["Stuart Russell", "Peter Norvig"],
    publishDate: "2020-01-15",
    abstract:
      "这是人工智能领域最具影响力的教材之一，全面介绍了人工智能的基本概念、理论和方法，涵盖了搜索、知识表示、机器学习、自然语言处理等多个方向。",
    tags: ["人工智能", "教材", "综合"],
    fileUrl: "https://example.com/papers/21101.pdf",
    fileType: "PDF",
    fileSize: "12.8 MB",
    uploadTime: "2023-09-05",
    folderId: 211,
    path: "我的文献库/计算机科学/人工智能",
  },
  "2101": {
    id: 2101,
    title: "计算机科学导论",
    authors: ["John Smith"],
    publishDate: "2019-08-30",
    abstract:
      "本书是计算机科学的入门教材，介绍了计算机科学的基本概念、发展历史、核心理论和主要应用领域，适合计算机专业的初学者阅读。",
    tags: ["计算机科学", "教材", "入门"],
    fileUrl: "https://example.com/papers/2101.pdf",
    fileType: "PDF",
    fileSize: "5.2 MB",
    uploadTime: "2023-09-01",
    folderId: 21,
    path: "我的文献库/计算机科学",
  },
};

// 获取文献详情的函数
export const getDocumentDetails = (documentId: string | number) => {
  return documentData[documentId as keyof typeof documentData] || null;
};
