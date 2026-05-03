"use client";

import { useState, useMemo } from "react";
import { useJobs } from "@/hooks/useJobs";
import { useCategories } from "@/hooks/useCategories";
import { JobCard } from "@/components/jobs/JobCard";
import { JobCardSkeleton } from "@/components/jobs/JobCardSkeleton";
import { JobFilters } from "@/components/jobs/JobFilters";
import { PaginationBar } from "@/components/common/PaginationBar";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { SearchBar } from "@/components/common/SearchBar";
import { useDebounce } from "@/hooks/useDebounce";

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 500);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [location, setLocation] = useState("");
  const [isRemote, setIsRemote] = useState<boolean | null>(null);
  const [minSalary, setMinSalary] = useState<number | null>(null);
  const [maxSalary, setMaxSalary] = useState<number | null>(null);

  const filters = useMemo(
    () => ({
      page,
      size: 20,
      search: debouncedSearch || undefined,
      category: selectedCategory || undefined,
      location: location || undefined,
      is_remote: isRemote ?? undefined,
      min_salary: minSalary ?? undefined,
      max_salary: maxSalary ?? undefined,
    }),
    [
      page,
      debouncedSearch,
      selectedCategory,
      location,
      isRemote,
      minSalary,
      maxSalary,
    ],
  );

  const { data, isLoading, isError, refetch } = useJobs(filters);
  const { data: categories } = useCategories();

  // Reset page when filters change
  const handleFilterChange = (fn: () => void) => {
    setPage(1);
    fn();
  };

  if (isError) {
    return <ErrorState onRetry={refetch} />;
  }

  const totalPages = data?.meta?.pages || 0;
  const jobs = data?.items || [];

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Search Bar - full width on mobile, centered on desktop */}
      <div className="max-w-2xl mx-auto mb-6">
        <SearchBar value={search} onChange={setSearch} />
      </div>

      {/* Two-column layout: filters sidebar + job grid */}
      <div className="flex flex-col md:flex-row gap-6">
        {/* Filters - hidden on mobile, shown in drawer (we'll add drawer later) */}
        <aside className="hidden md:block w-72 shrink-0">
          <JobFilters
            categories={categories || []}
            selectedCategory={selectedCategory}
            onCategoryChange={(cat) =>
              handleFilterChange(() => setSelectedCategory(cat))
            }
            location={location}
            onLocationChange={(loc) =>
              handleFilterChange(() => setLocation(loc))
            }
            isRemote={isRemote}
            onRemoteChange={(remote) =>
              handleFilterChange(() => setIsRemote(remote))
            }
            minSalary={minSalary}
            maxSalary={maxSalary}
            onSalaryChange={(min, max) =>
              handleFilterChange(() => {
                setMinSalary(min);
                setMaxSalary(max);
              })
            }
            onClear={() =>
              handleFilterChange(() => {
                setSelectedCategory(null);
                setLocation("");
                setIsRemote(null);
                setMinSalary(null);
                setMaxSalary(null);
                setSearch("");
              })
            }
          />
        </aside>

        {/* Main content */}
        <main className="flex-1">
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <JobCardSkeleton key={i} />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <EmptyState
              onClear={() =>
                handleFilterChange(() => {
                  setSelectedCategory(null);
                  setLocation("");
                  setIsRemote(null);
                  setMinSalary(null);
                  setMaxSalary(null);
                  setSearch("");
                })
              }
            />
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {jobs.map((job) => (
                  <JobCard key={job.id} job={job} />
                ))}
              </div>
              {totalPages > 1 && (
                <div className="mt-8">
                  <PaginationBar
                    currentPage={page}
                    totalPages={totalPages}
                    hasPrev={data?.meta?.has_prev || false}
                    hasNext={data?.meta?.has_next || false}
                    onPageChange={setPage}
                  />
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* Mobile filter drawer button - simple for now */}
      <div className="fixed bottom-4 right-4 md:hidden">
        <button className="bg-primary text-primary-foreground rounded-full p-3 shadow-lg">
          Filters
        </button>
      </div>
    </div>
  );
}
