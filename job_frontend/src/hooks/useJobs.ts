import { useQuery, keepPreviousData } from "@tanstack/react-query";
import type { JobFilters } from "@/services/jobsApi";
import { fetchJobs } from "@/services/jobsApi";
import type { PaginatedResponse, Job } from "@/types/job";

export function useJobs(filters: JobFilters) {
  return useQuery<PaginatedResponse<Job>, unknown>({
    queryKey: ["jobs", filters],
    queryFn: () => fetchJobs(filters),
    placeholderData: keepPreviousData,
  });
}

export default useJobs;
