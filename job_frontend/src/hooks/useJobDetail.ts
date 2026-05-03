import { useQuery } from "@tanstack/react-query";
import { fetchJobById } from "@/services/jobsApi";
import type { JobDetail } from "@/types/job";

export function useJobDetail(id?: string) {
  return useQuery<JobDetail, unknown>({
    queryKey: ["job", id],
    queryFn: () => fetchJobById(id as string),
    enabled: !!id,
  });
}

export default useJobDetail;
