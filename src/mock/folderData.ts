// 文件夹树结构数据
export const folderData = [
  {
    id: 1,
    label: "Home",
    icon: "home",
  },
  {
    id: 2,
    label: "我的文献库",
    icon: "folder",
    children: [
      {
        id: 21,
        label: "计算机科学",
        icon: "folder",
        children: [
          {
            id: 211,
            label: "人工智能",
            icon: "folder",
            children: [
              {
                id: 2111,
                label: "机器学习",
                icon: "folder",
                children: [],
              },
              {
                id: 2112,
                label: "深度学习",
                icon: "folder",
                children: [],
              },
            ],
          },
          {
            id: 212,
            label: "软件工程",
            icon: "folder",
            children: [],
          },
        ],
      },
      {
        id: 22,
        label: "物理学",
        icon: "folder",
        children: [
          {
            id: 221,
            label: "量子物理",
            icon: "folder",
            children: [],
          },
        ],
      },
      {
        id: 23,
        label: "数学",
        icon: "folder",
        children: [],
      },
    ],
  },
  {
    id: 3,
    label: "共享文献",
    icon: "folder",
    children: [],
  },
];

// 文件夹内容数据 - 按文件夹ID组织
export const folderContents = {
  // 根文件夹
  "1": [
    {
      id: 101,
      name: "最近阅读的文献",
      type: "folder",
      createTime: "2023-10-01",
      info: "包含最近阅读的文献",
    },
    {
      id: 102,
      name: "重要文献",
      type: "folder",
      createTime: "2023-09-15",
      info: "重要参考文献",
    },
  ],
  // 我的文献库
  "2": [
    {
      id: 21,
      name: "计算机科学",
      type: "folder",
      createTime: "2023-08-20",
      info: "计算机科学相关文献",
    },
    {
      id: 22,
      name: "物理学",
      type: "folder",
      createTime: "2023-08-21",
      info: "物理学相关文献",
    },
    {
      id: 23,
      name: "数学",
      type: "folder",
      createTime: "2023-08-22",
      info: "数学相关文献",
    },
  ],
  // 计算机科学
  "21": [
    {
      id: 211,
      name: "人工智能",
      type: "folder",
      createTime: "2023-08-25",
      info: "AI相关文献",
    },
    {
      id: 212,
      name: "软件工程",
      type: "folder",
      createTime: "2023-08-26",
      info: "软件工程相关文献",
    },
    {
      id: 2101,
      name: "计算机科学导论.pdf",
      type: "document",
      createTime: "2023-09-01",
      info: "基础教材，作者：John Smith",
      fileSize: "5.2 MB",
      fileType: "PDF",
    },
  ],
  // 人工智能
  "211": [
    {
      id: 2111,
      name: "机器学习",
      type: "folder",
      createTime: "2023-08-27",
      info: "机器学习相关文献",
    },
    {
      id: 2112,
      name: "深度学习",
      type: "folder",
      createTime: "2023-08-28",
      info: "深度学习相关文献",
    },
    {
      id: 21101,
      name: "人工智能：现代方法.pdf",
      type: "document",
      createTime: "2023-09-05",
      info: "经典教材，作者：Stuart Russell, Peter Norvig",
      fileSize: "12.8 MB",
      fileType: "PDF",
    },
  ],
  // 机器学习
  "2111": [
    {
      id: 211101,
      name: "机器学习算法综述.pdf",
      type: "document",
      createTime: "2023-09-10",
      info: "综述论文，作者：李明，张华",
      fileSize: "3.5 MB",
      fileType: "PDF",
    },
    {
      id: 211102,
      name: "支持向量机原理与应用.pdf",
      type: "document",
      createTime: "2023-09-12",
      info: "学术论文，作者：王刚",
      fileSize: "2.1 MB",
      fileType: "PDF",
    },
  ],
};

// 获取特定文件夹内容的函数
export const getFolderContents = (folderId: string | number) => {
  return folderContents[folderId as keyof typeof folderContents] || [];
};
