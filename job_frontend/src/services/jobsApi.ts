import api from "./api";
import type { PaginatedResponse, Job, JobDetail } from "@/types/job";

export interface JobFilters {
  page?: number;
  size?: number;
  search?: string;
  category?: string;
  source_site?: string;
  job_type?: string;
  is_remote?: boolean;
  location?: string;
  min_salary?: number;
  max_salary?: number;
}

export async function fetchJobs(
  filters: JobFilters = {},
): Promise<PaginatedResponse<Job>> {
  const { data } = await api.get<PaginatedResponse<Job>>("/api/v1/jobs", {
    params: filters,
  });
  return data;
}

export async function fetchJobById(id: string): Promise<JobDetail> {
  const { data } = await api.get<JobDetail>(`/api/v1/jobs/${id}`);
  return data;
}
