import { getData } from "./mock";
import { Essay, Tag } from "./types";

// 加载文章列表
export async function loadEssays(): Promise<Essay[]> {
  const data = await getData();
  return data.essays;
}

// 根据ID加载单篇文章
export async function loadEssayById(id: number): Promise<Essay | undefined> {
  const data = await getData();
  return data.essays.find((essay) => essay.id === id);
}

// 加载所有标签
export async function loadTags(): Promise<Tag[]> {
  const data = await getData();
  return data.tags;
}

// 根据标签ID加载文章列表
export async function loadEssaysByTagId(tagId: number): Promise<Essay[]> {
  const data = await getData();
  return data.essays.filter((essay) => essay.tagIds.includes(tagId));
}

// 根据标签ID列表加载文章列表
export async function loadEssaysByTagIds(tagIds: number[]): Promise<Essay[]> {
  const data = await getData();
  return data.essays.filter((essay) =>
    essay.tagIds.some((id) => tagIds.includes(id))
  );
}

// 根据关键字搜索文章
export async function searchEssays(keyword: string): Promise<Essay[]> {
  const data = await getData();
  const lowerKeyword = keyword.toLowerCase();

  return data.essays.filter(
    (essay) =>
      essay.title.toLowerCase().includes(lowerKeyword) ||
      essay.content.toLowerCase().includes(lowerKeyword)
  );
}
