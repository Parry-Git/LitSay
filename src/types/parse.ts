/**
 * 解析结果类型
 */
export interface ParseResult {
  /**
   * 文件名
   */
  fileName: string;
  
  /**
   * 解析出的元数据
   */
  metadata: {
    title: string;
    authors: string[];
    sequence?: string[];
    institutions?: string[];
    institution_location?: string[];
    email?: string[];
    doi: string | null;
    publishDate: string | null;
    journal: string | null;
    conference: string | null;
    keywords: string[];
    queryTime?: number;
  };
}
