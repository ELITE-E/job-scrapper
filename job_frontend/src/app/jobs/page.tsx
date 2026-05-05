"use client";

import { useState, useMemo } from "react";
import { useJobs } from "@/hooks/useJobs";
import { JobCard } from "@/components/jobs/JobCard";
import { JobCardSkeleton } from "@/components/jobs/JobCardSkeleton";
import { JobFilters } from "@/components/jobs/JobFilters";
import { PaginationBar } from "@/components/common/PaginationBar";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { SearchBar } from "@/components/common/SearchBar";
import { useDebounce } from "@/hooks/useDebounce";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 500);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [location, setLocation] = useState("");
  const [isRemote, setIsRemote] = useState<boolean | null>(null);
  const [minSalary, setMinSalary] = useState<number | null>(null);
  const [maxSalary, setMaxSalary] = useState<number | null>(null);
  const searchParams = useSearchParams();
  const categoryParam = searchParams.get("category");

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

  // Reset page when filters change
  const handleFilterChange = (fn: () => void) => {
    setPage(1);
    fn();
  };

  useEffect(() => {
    if (categoryParam && categoryParam !== selectedCategory) {
      setSelectedCategory(categoryParam);
      setPage(1);
      return;
    }

    if (!categoryParam && selectedCategory) {
      setSelectedCategory(null);
      setPage(1);
    }
  }, [categoryParam, selectedCategory]);

  if (isError) {
    return <ErrorState onRetry={refetch} />;
  }

  const totalPages = data?.meta?.pages || 0;
  const jobs = data?.items || [];

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Search Bar - full width on mobile, centered on desktop */}
      <div className="max-w-2xl mx-auto mb-6">
        <SearchBar
          value={search}
          onChange={(value) => handleFilterChange(() => setSearch(value))}
        />
      </div>

      {/* Two-column layout: filters sidebar + job grid */}
      <div className="flex flex-col md:flex-row gap-6">
        <JobFilters
          selectedCategory={selectedCategory}
          setSelectedCategory={(cat) =>
            handleFilterChange(() => setSelectedCategory(cat))
          }
          location={location}
          setLocation={(loc) => handleFilterChange(() => setLocation(loc))}
          isRemote={isRemote}
          setIsRemote={(remote) =>
            handleFilterChange(() => setIsRemote(remote))
          }
          minSalary={minSalary}
          setMinSalary={(min) => handleFilterChange(() => setMinSalary(min))}
          maxSalary={maxSalary}
          setMaxSalary={(max) => handleFilterChange(() => setMaxSalary(max))}
          clearFilters={() =>
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
    </div>
  );
}
