// 用户统计数据
export const userStatsData = {
  totalDocuments: 42,
  recentlyViewed: 8,
  totalFolders: 12,
  sharedDocuments: 5,
  favoriteDocuments: 7,
  storageUsed: "128 MB",
  storageTotal: "5 GB",
  storagePercentage: 2.56, // 使用百分比

  // 最近活动
  recentActivities: [
    {
      id: 1,
      type: "upload",
      documentName: "机器学习算法综述.pdf",
      time: "2023-10-15 14:30",
      folder: "机器学习",
    },
    {
      id: 2,
      type: "view",
      documentName: "人工智能：现代方法.pdf",
      time: "2023-10-14 09:45",
      folder: "人工智能",
    },
    {
      id: 3,
      type: "download",
      documentName: "支持向量机原理与应用.pdf",
      time: "2023-10-12 16:20",
      folder: "机器学习",
    },
    {
      id: 4,
      type: "create_folder",
      folderName: "深度学习",
      time: "2023-10-10 11:15",
      parentFolder: "人工智能",
    },
  ],
};
