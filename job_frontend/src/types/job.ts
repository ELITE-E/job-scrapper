export interface Company {
  name: string;
  url: string | null;
  industry: string | null;
  logo_url: string | null;
}

export interface Category {
  name: string;
  slug: string;
}

export interface Job {
  id: string;
  title: string;
  company: Company | null;
  category: Category | null;
  location: string | null;
  location_city: string | null;
  location_state: string | null;
  location_country: string | null;
  is_remote: boolean;
  job_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  salary_interval: string | null;
  source_site: string;
  job_url: string;
  date_posted: string | null;
  date_scraped: string;
}

export interface JobDetail extends Job {
  description: string | null;
  extras: Record<string, unknown>;
}

export interface PaginationMeta {
  total: number;
  page: number;
  size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  meta: PaginationMeta;
}
