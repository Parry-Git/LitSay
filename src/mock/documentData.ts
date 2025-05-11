// 文献详细数据
export const documentData = {
  // 文献ID为键
  "211101": {
    id: 211101,
    title: "机器学习算法综述",
    doi: "10.1109/TNNLS.2022.1234567",
    authors: ["李明", "张华"],
    sequence: ["first", "additional"],
    institutions: ["Peking University", "Fudan University"],
    institution_location: ["Beijing, China", "Shanghai, China"],
    email: ["liming@pku.edu.cn", "zhanghua@fudan.edu.cn"],
    conference: null,
    journal: "IEEE Transactions on Neural Networks and Learning Systems",
    keywords: ["机器学习", "算法", "综述", "深度学习"],
    publishDate: "2022-06-15",
    uploadTime: "2023-09-10",
    folderId: 2111,
    path: "我的文献库/计算机科学/人工智能/机器学习",
    stars: 4,
    note: `## 阅读笔记：机器学习算法综述

### 核心观点
- 机器学习算法可分为三大类：**监督学习**、**无监督学习**和**强化学习**
- 深度学习是当前最热门的研究方向
- 迁移学习在数据稀缺场景下表现优异

### 重要公式
常用的损失函数：
\`\`\`
L(y, f(x)) = (y - f(x))²
\`\`\`

### 关键问题
1. 过拟合与欠拟合的平衡
2. 计算效率与模型复杂度的权衡
3. 数据质量对算法性能的影响

![机器学习框架](https://example.com/ml-framework.png)

> 本文是机器学习领域一篇非常全面的综述，值得反复阅读。`,
  },
  "211102": {
    id: 211102,
    title: "支持向量机原理与应用",
    doi: "10.1016/j.patcog.2021.108321",
    authors: ["王刚"],
    sequence: ["first"],
    institutions: ["Tsinghua University"],
    institution_location: ["Beijing, China"],
    email: ["wanggang@tsinghua.edu.cn"],
    conference: null,
    journal: "Pattern Recognition",
    keywords: ["支持向量机", "分类算法", "模式识别", "核函数"],
    publishDate: "2021-11-20",
    uploadTime: "2023-09-12",
    folderId: 2111,
    path: "我的文献库/计算机科学/人工智能/机器学习",
    stars: 3,
    note: `# 支持向量机笔记

支持向量机(SVM)是一种常用的**分类算法**，核心思想是寻找最优分隔超平面。

## 关键特性
- 最大间隔分类器
- 核技巧可以处理非线性问题
- 对噪声有较好的抵抗力

### 常见核函数
* 线性核：K(x,y) = x·y
* 多项式核：K(x,y) = (x·y + c)^d
* 高斯核(RBF)：K(x,y) = exp(-γ||x-y||²)

## 应用场景
SVM在以下领域表现优异：
1. 文本分类
2. 图像识别
3. 生物信息学

![SVM示意图](https://example.com/svm-illustration.png)

**代码示例：**
\`\`\`python
from sklearn import svm
model = svm.SVC(kernel='rbf')
model.fit(X_train, y_train)
\`\`\``,
  },
  "21101": {
    id: 21101,
    title: "人工智能：现代方法",
    doi: "10.1007/s10462-019-09728-3",
    authors: ["Stuart Russell", "Peter Norvig"],
    sequence: ["first", "additional"],
    institutions: ["University of California, Berkeley", "Google"],
    institution_location: ["Berkeley, CA, USA", "Mountain View, CA, USA"],
    email: ["russell@cs.berkeley.edu", "norvig@google.com"],
    conference: "ICML 2020",
    journal: null,
    keywords: ["人工智能", "教材", "综合", "机器学习", "知识表示"],
    publishDate: "2020-01-15",
    uploadTime: "2023-09-05",
    folderId: 211,
    path: "我的文献库/计算机科学/人工智能",
    stars: 5,
    note: `# 《人工智能：现代方法》阅读笔记

这本书是AI领域的经典教材，由Stuart Russell和Peter Norvig编写。

## 主要章节笔记

### 第1章：人工智能简介
人工智能的定义、历史发展和主要研究方向。

### 第2章：智能Agent
* **PEAS**模型：Performance, Environment, Actuators, Sensors
* 不同类型的环境：全观测vs部分观测，确定性vs随机性

### 第3章：搜索算法
搜索算法包括：
1. 盲目搜索
   - BFS(宽度优先)
   - DFS(深度优先)
2. 启发式搜索
   - A*算法
   - 最佳优先搜索

**重要公式**:
\`\`\`
f(n) = g(n) + h(n)
\`\`\`
其中g(n)是从起点到n的实际代价，h(n)是从n到目标的估计代价。

## 重要概念

| 算法 | 优点 | 缺点 |
|------|------|------|
| BFS | 完备性、最优性 | 空间复杂度高 |
| A* | 效率高、最优性 | 需要好的启发函数 |
| 遗传算法 | 适用于大规模空间 | 不保证最优性 |

![AI领域关系图](https://example.com/ai-map.jpg)`,
  },
  "2101": {
    id: 2101,
    title: "计算机科学导论",
    doi: "10.1145/12345.67890",
    authors: ["John Smith"],
    sequence: ["first"],
    institutions: ["Stanford University"],
    institution_location: ["Stanford, CA, USA"],
    email: ["john.smith@stanford.edu"],
    reference: "Smith, J. (2019). Introduction to computer science. ACM Press.",
    journal: null,
    keywords: ["计算机科学", "教材", "入门", "算法", "数据结构"],
    publishDate: "2019-08-30",
    uploadTime: "2023-09-01",
    folderId: 21,
    path: "我的文献库/计算机科学",
    stars: 4,
    note: `# 计算机科学导论笔记

## 数据结构与算法
计算机科学中最基础的概念之一是**数据结构**和**算法**。

### 常见数据结构：
* 数组 (Array)
* 链表 (Linked List)
* 栈 (Stack)
* 队列 (Queue)
* 树 (Tree)
* 图 (Graph)
* 散列表 (Hash Table)

### 算法复杂度
Big O表示法：
- O(1): 常数时间
- O(log n): 对数时间
- O(n): 线性时间
- O(n log n): 线性对数时间
- O(n²): 平方时间
- O(2^n): 指数时间

## 编程范式
1. **命令式编程**
2. **声明式编程**
3. **函数式编程**
4. **面向对象编程**

\`\`\`java
// Java示例：简单的面向对象程序
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, Computer Science!");
    }
}
\`\`\`

![计算机科学学科关系图](https://example.com/cs-map.png)

> "计算机科学是关于计算机的科学，正如天文学是关于望远镜的科学一样" - Edsger W. Dijkstra`,
  },
};

// 获取文献详情的函数
export const getDocumentDetails = (documentId: string | number) => {
  return documentData[documentId as keyof typeof documentData] || null;
};
