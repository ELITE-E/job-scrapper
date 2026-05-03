import { useQuery } from "@tanstack/react-query";
import { fetchCategories } from "@/services/categoriesApi";
import type { Category } from "@/types/category";

export function useCategories() {
  return useQuery<Category[], unknown>({
    queryKey: ["categories"],
    queryFn: fetchCategories,
    staleTime: Infinity,
  });
}

export default useCategories;
