"use client";

import React, { useState, useMemo } from "react";
import useDebounce from "@/hooks/useDebounce";
import useJobs from "@/hooks/useJobs";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";
import JobCardSkeleton from "@/components/jobs/JobCardSkeleton";
import JobCard from "@/components/jobs/JobCard";
//import JobDetailPage from "./JobDetailPage";

export default function JobListPage() {
  const [page, setPage] = useState<number>(1);
  const [search, setSearch] = useState<string>("");
  const debouncedSearch = useDebounce<string>(search, 500);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [location, setLocation] = useState<string>("");
  const [isRemote, setIsRemote] = useState<boolean | null>(null);

  // Helper function to update filters and reset page to 1 simultaneously
  function updateFilter<T>(
    setter: React.Dispatch<React.SetStateAction<T>>,
    value: T,
  ) {
    setter(value);
    setPage(1);
  }

  function clearFilters() {
    setSearch("");
    setSelectedCategory(null);
    setLocation("");
    setIsRemote(null);
    setPage(1);
  }

  const filters = useMemo(
    () => ({
      page,
      size: 20,
      search: debouncedSearch || undefined,
      category: selectedCategory || undefined,
      is_remote: isRemote ?? undefined,
      location: location || undefined,
    }),
    [page, debouncedSearch, selectedCategory, isRemote, location],
  );

  // Destructure isPlaceholderData to handle smooth transitions in v5
  const { data, isLoading, isError, refetch, isPlaceholderData } =
    useJobs(filters);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <h1 className="text-2xl font-bold mb-4">Jobs</h1>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Filter sidebar (desktop) */}
        <aside className="hidden md:block w-[280px] shrink-0">
          <div className="space-y-3">
            <input
              aria-label="Search jobs"
              placeholder="Search jobs"
              value={search}
              onChange={(e) => updateFilter(setSearch, e.target.value)}
              className="border p-2 rounded w-full"
            />
            <input
              placeholder="Location"
              value={location}
              onChange={(e) => updateFilter(setLocation, e.target.value)}
              className="border p-2 rounded w-full"
            />
            <select
              aria-label="Job Category"
              value={selectedCategory ?? ""}
              onChange={(e) =>
                updateFilter(setSelectedCategory, e.target.value || null)
              }
              className="border p-2 rounded w-full"
            >
              <option value="">All categories</option>
              <option value="engineering">Engineering</option>
              <option value="design">Design</option>
            </select>
            <select
              aria-label="Work Type"
              value={isRemote === null ? "" : isRemote ? "true" : "false"}
              onChange={(e) => {
                const v = e.target.value;
                const val = v === "" ? null : v === "true";
                updateFilter(setIsRemote, val);
              }}
              className="border p-2 rounded w-full"
            >
              <option value="">Any Location</option>
              <option value="true">Remote</option>
              <option value="false">On-site</option>
            </select>
            <button
              onClick={clearFilters}
              className="w-full px-3 py-2 rounded border text-sm"
            >
              Clear filters
            </button>
          </div>
        </aside>

        <main className="flex-1">
          {/* Mobile filters (stacked) */}
          <div className="mb-4 md:hidden space-y-2">
            <input
              aria-label="Search jobs"
              placeholder="Search jobs"
              value={search}
              onChange={(e) => updateFilter(setSearch, e.target.value)}
              className="border p-2 rounded w-full"
            />
            <div className="flex gap-2">
              <input
                placeholder="Location"
                value={location}
                onChange={(e) => updateFilter(setLocation, e.target.value)}
                className="border p-2 rounded flex-1"
              />
              <select
                aria-label="Work Type"
                value={isRemote === null ? "" : isRemote ? "true" : "false"}
                onChange={(e) => {
                  const v = e.target.value;
                  const val = v === "" ? null : v === "true";
                  updateFilter(setIsRemote, val);
                }}
                className="border p-2 rounded w-36"
              >
                <option value="">Any</option>
                <option value="true">Remote</option>
                <option value="false">On-site</option>
              </select>
            </div>
          </div>

          {/* Results List */}
          <div
            className={`${isPlaceholderData ? "opacity-50" : "opacity-100"}`}
          >
            {isError ? (
              <ErrorState onRetry={() => refetch()} />
            ) : !isLoading && data?.items?.length === 0 ? (
              <EmptyState onClear={clearFilters} />
            ) : isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <JobCardSkeleton key={i} />
                ))}
              </div>
            ) : (
              <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {data?.items?.map((job) => (
                  <li key={job.id} className="h-full">
                    <JobCard
                      job={job}
                      jobDetail={{ description: job.description ?? "" }}
                    />
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center gap-2 mt-4">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isPlaceholderData}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Prev
            </button>
            <div className="text-sm font-medium">
              Page {data?.meta?.page ?? page} of {data?.meta?.pages ?? "-"}
            </div>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={data?.meta?.has_next === false || isPlaceholderData}
              className="px-3 py-1 border rounded disabled:opacity-50"
            >
              Next
            </button>
            <button
              onClick={() => refetch()}
              className="ml-auto px-3 py-1 border rounded text-sm bg-gray-100"
            >
              Refresh
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}
