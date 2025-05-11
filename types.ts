// 文章类型定义
export interface Essay {
  id: number;
  title: string;
  content: string;
  author: string;
  publishDate: string;
  tagIds: number[];
}

// 标签类型定义
export interface Tag {
  id: number;
  name: string;
  color?: string;
}

// 数据类型定义
export interface MockData {
  essays: Essay[];
  tags: Tag[];
}
