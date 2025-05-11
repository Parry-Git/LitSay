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

// 文件夹信息数据 - 按文件夹ID组织
export const folderInfo = {
  "1": {
    id: 1,
    name: "Home",
    label: "首页",
    parentId: null,
    path: "/",
  },
  "2": {
    id: 2,
    name: "我的文献库",
    label: "我的文献库",
    parentId: null,
    path: "/我的文献库",
  },
  "21": {
    id: 21,
    name: "计算机科学",
    label: "计算机科学",
    parentId: 2,
    path: "/我的文献库/计算机科学",
  },
  "211": {
    id: 211,
    name: "人工智能",
    label: "人工智能",
    parentId: 21,
    path: "/我的文献库/计算机科学/人工智能",
  },
  "2111": {
    id: 2111,
    name: "机器学习",
    label: "机器学习",
    parentId: 211,
    path: "/我的文献库/计算机科学/人工智能/机器学习",
  },
  "2112": {
    id: 2112,
    name: "深度学习",
    label: "深度学习",
    parentId: 211,
    path: "/我的文献库/计算机科学/人工智能/深度学习",
  },
  "212": {
    id: 212,
    name: "软件工程",
    label: "软件工程",
    parentId: 21,
    path: "/我的文献库/计算机科学/软件工程",
  },
  "22": {
    id: 22,
    name: "物理学",
    label: "物理学",
    parentId: 2,
    path: "/我的文献库/物理学",
  },
  "221": {
    id: 221,
    name: "量子物理",
    label: "量子物理",
    parentId: 22,
    path: "/我的文献库/物理学/量子物理",
  },
  "23": {
    id: 23,
    name: "数学",
    label: "数学",
    parentId: 2,
    path: "/我的文献库/数学",
  },
  "3": {
    id: 3,
    name: "共享文献",
    label: "共享文献",
    parentId: null,
    path: "/共享文献",
  },
};

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
      name: "计算机科学导论",
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
      name: "人工智能：现代方法",
      type: "document",
      createTime: "2023-09-05",
      info: "经典教材，作者：Stuart Russell, Peter Norvig",
    },
  ],
  // 机器学习
  "2111": [
    {
      id: 211101,
      name: "机器学习算法综述",
      type: "document",
      createTime: "2023-09-10",
      info: "综述论文，作者：李明，张华",
    },
    {
      id: 211102,
      name: "支持向量机原理与应用",
      type: "document",
      createTime: "2023-09-12",
      info: "学术论文，作者：王刚",
    },
  ],
};

// 获取特定文件夹内容的函数
export const getFolderContents = (folderId: string | number) => {
  // 获取文件夹信息
  const currentFolder = folderInfo[folderId as keyof typeof folderInfo] || {
    id: folderId,
    name: `文件夹 ${folderId}`,
    label: `文件夹 ${folderId}`,
  };

  // 获取文件夹内容
  const items = folderContents[folderId as keyof typeof folderContents] || [];

  // 返回包含当前文件夹信息和内容的对象
  return {
    currentFolder,
    items,
  };
};
