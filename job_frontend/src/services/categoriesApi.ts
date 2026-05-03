import api from "./api";
import type { Category } from "@/types/category";

export async function fetchCategories(): Promise<Category[]> {
  const { data } = await api.get<Category[]>("/api/v1/categories");
  return data;
}

export default fetchCategories;
